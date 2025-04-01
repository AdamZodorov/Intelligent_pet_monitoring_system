package com.example.demo.service;

import com.example.demo.DTO.ActivityDurationDTO;
import com.example.demo.DTO.CreatePetDTO;
import com.example.demo.DTO.PetStatDTO;
import com.example.demo.entities.*;
import com.example.demo.model.ActivityType;
import com.example.demo.repository.*;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.data.jpa.repository.support.SimpleJpaRepository;
import org.springframework.http.MediaType;
import org.springframework.http.MediaTypeFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

@Service
@RequiredArgsConstructor
public class PetService {
    private final PetRepository petRepository;

    private final ShelterRepository shelterRepository;

    private final BasicActivityRepository basicActivityRepository;

    private final ImageUploadService imageUploadService;

    private final VideoRepository videoRepository;

    private final   PetGroupRepository petGroupRepository;

    private static final Map<ActivityType, String> ACTIVITY_NAMES = Map.ofEntries(
            Map.entry(ActivityType.KEEPING_STILL, "Не двигается"),
            Map.entry(ActivityType.WALKING, "Гуляет"),
            Map.entry(ActivityType.EATING, "Ест"),
            Map.entry(ActivityType.MOVING, "Движется"),
            Map.entry(ActivityType.RUNNING, "Бегает"),
            Map.entry(ActivityType.DRINKING, "Пьёт"),
            Map.entry(ActivityType.ATTACKING, "Атакует"),
            Map.entry(ActivityType.FIGHTING, "Дерется"),
            Map.entry(ActivityType.DISPLAYING_DEFENSIVE_POSE, "В боевом режиме"),
            Map.entry(ActivityType.STANDING, "Стоит"),
            Map.entry(ActivityType.SITTING, "Сидит"),
            Map.entry(ActivityType.RESTING, "Отдыхает"),
            Map.entry(ActivityType.LYING_DOWN, "Лежит")
    );

    @Value("${file.upload-dir}")
    private String uploadDir;

    public Pet findPetById(Long petId) {
        return petRepository.findPetById(petId);
    }

    public void createPet(CreatePetDTO request, Long  shelterId) {
        Shelter shelter = shelterRepository.findById(shelterId)
                .orElseThrow(() -> new IllegalArgumentException("Приют не найден"));

        PetGroup group = petGroupRepository.findByShelterIdAndGroupId(shelterId, request.getGroup())
                .orElseGet(() -> {
                    PetGroup newGroup = new PetGroup();
                    newGroup.setShelter(shelter);
                    newGroup.setGroupNumber(request.getGroup());
                    newGroup.setCreatedDt(LocalDateTime.now());
                    return petGroupRepository.save(newGroup);
                });

        Pet pet = new Pet();
        pet.setName(request.getName());
        pet.setAge(request.getAge());
        pet.setShelter(shelter);
        pet.setBreed(request.getBreed());
        pet.setSpecies(request.getSpecies());
        pet.setWeight(request.getWeight());
        pet.setHeight(request.getHeight());
        pet.setGroup(group);
        pet.setCreateDt(LocalDateTime.now());
        pet.setDescription(request.getDescription());

        Pet savedPet = petRepository.save(pet);

        // main image save
        try {
            String mainImagePath = imageUploadService.moveTempImageToPermanent(
                    request.getMainImageId(), savedPet.getId(), 0);
        } catch (IOException e) {
            throw new RuntimeException("Error processing image: " + e.getMessage(), e);
        }
        // other image save
        for (int i = 0; i < request.getTempImageIds().size(); i++) {
            String tempImageId = request.getTempImageIds().get(i);
            try {
                String imagePath = imageUploadService.moveTempImageToPermanent(tempImageId, savedPet.getId(), i + 1);
            } catch (IOException e) {
                throw new RuntimeException("Error processing image: " + e.getMessage(), e);
            }
        }
    }

    public Resource getPetPhoto(Long petId) {
        try {
            Pet pet = petRepository.findPetById(petId);
            if (pet == null) {
                return null;
            }
            String[] extensions = { "jpg", "jpeg", "png" };
            for (String ext : extensions) {
                Path path = Paths.get(uploadDir, Long.toString(pet.getId()), "0." + ext);
                System.out.println("path to photo: " + path);
                Resource resource = new UrlResource(path.toUri());
                if (resource.exists() && resource.isReadable()) {
                    return resource;
                }
            }
            return null;
        } catch (Exception e) {
            return null;
        }
    }

    public void deletePet(Long petId) {
        Pet pet = petRepository.findById(petId)
                .orElseThrow(() -> new EntityNotFoundException("Питомец с ID " + petId + " не найден"));
        try {
            basicActivityRepository.deleteByPetId(petId);
            petRepository.delete(pet);
        } catch (DataIntegrityViolationException e) {
            throw new RuntimeException("Ошибка при удалении данных", e);
        }
    }

    public List<ActivityDurationDTO> getTopActivities(Long petId) {
        List<BasicActivity> activities = basicActivityRepository.findByPetId(petId);

        return activities.stream()
                .collect(Collectors.groupingBy(
                        BasicActivity::getActivityType,
                        Collectors.summingLong(activity ->
                                activity.getEndTimeInSeconds() - activity.getStartTimeInSeconds())
                        )
                )
                .entrySet().stream()
                .sorted(Map.Entry.<ActivityType, Long>comparingByValue().reversed())
                .limit(3)
                .map(entry -> new ActivityDurationDTO(
                        ACTIVITY_NAMES.get(entry.getKey()),
                        entry.getValue()
                ))
                .toList();
    }

    public Resource getPhotosAsZip(Long videoId) throws IOException {
        Video video = videoRepository.findById(videoId)
                .orElseThrow(() -> new EntityNotFoundException("Видео не найдено"));
        PetGroup group = video.getGroup();
        if (group == null) {
            throw new EntityNotFoundException("Группа не привязана к видео");
        }
        List<Pet> pets = petRepository.findByGroupId(group.getId());
        if (pets.isEmpty()) {
            throw new IOException("В группе нет питомцев");
        }
        Path zipPath = Files.createTempFile("photos", ".zip");
        try (ZipOutputStream zipOut = new ZipOutputStream(Files.newOutputStream(zipPath))) {
            for (Pet pet : pets) {
                String photoDir = Paths.get(uploadDir, Long.toString(pet.getId())).toString();

                File directory = new File(photoDir);
                if (!directory.exists() || !directory.isDirectory()) continue;
                Path petDirPath = directory.toPath();

                Files.walk(petDirPath)
                        .filter(Files::isRegularFile)
                        .filter(path -> {
                            String fileName = path.getFileName().toString();
                            return !fileName.startsWith("0.");
                        })
                        .forEach(path -> {
                            Path relativePath = petDirPath.relativize(path);
                            String entryName = pet.getId() + "/" + relativePath.toString();
                            ZipEntry zipEntry = new ZipEntry(entryName);
                            try {
                                zipOut.putNextEntry(zipEntry);
                                Files.copy(path, zipOut);
                                zipOut.closeEntry();
                            } catch (IOException e) {
                                throw new UncheckedIOException("Ошибка архивирования файла: " + path, e);
                            }
                        });
            }

        } catch (IOException e) {
            Files.deleteIfExists(zipPath); // Удалить битый архив
            throw new IOException("Ошибка создания архива: " + e.getMessage());
        }
        return new UrlResource(zipPath.toUri());
    }

    public void processPredictions(PetStatDTO request) {
        Pet pet = petRepository.findById(request.getPetId())
                .orElseThrow(() -> new EntityNotFoundException("Питомец не найден"));
        Video video = videoRepository.findById(request.getVideoId())
                .orElseThrow(() -> new EntityNotFoundException("Видео не найдено"));
        Double fps = request.getVideoFps();
        if (fps == null || fps <= 0) {

            throw new IllegalArgumentException("Некорректная частота кадров");
        }
        int minFramesCount = (int) Math.ceil(fps / 16);
        int currentFramesCount = 0;
        ActivityType prevActivity = null;
        for (PetStatDTO.FramePrediction framePred : request.getPredictions()) {
            List<Double> pred = framePred.getPreds().get(0);
            // getting index of max el
            int maxInd = 0;
            for (int i = 1; i < pred.size(); ++i) {
                if (pred.get(maxInd) < pred.get(i)) {
                    maxInd = i;
                }
            }
            ActivityType nowActivity = ActivityType.values()[maxInd];
            if (nowActivity != prevActivity) {
                if (currentFramesCount > minFramesCount) {
                    saveActivity(pet, video,
                            prevActivity, framePred.getFrameIndex(), currentFramesCount, fps, request.getFrameIndent());
                }
                currentFramesCount = 0;
            }
            prevActivity = nowActivity;
            ++currentFramesCount;
        }
        if (currentFramesCount > minFramesCount) {
            saveActivity(pet, video,
                    prevActivity, request.getPredictions().size(), currentFramesCount, fps, request.getFrameIndent());
        }
        video.setProcessed(true);
        videoRepository.save(video);
    }

    private void saveActivity(Pet pet, Video video, ActivityType activity, long framePredInd, long currentFramesCount, double fps, Long frameIndent) {
        long frameInd = framePredInd - currentFramesCount;
        long startTime = (long) Math.ceil((frameIndent + frameInd * 16) / fps);
        long endTime = startTime + (long) Math.floor(currentFramesCount * 16 / fps);
        BasicActivity basicActivity = new BasicActivity();
        basicActivity.setActivityType(activity);
        basicActivity.setPet(pet);
        basicActivity.setVideo(video);
        basicActivity.setStartTimeInSeconds(startTime);
        basicActivity.setEndTimeInSeconds(endTime);
        basicActivityRepository.save(basicActivity);
    }
}
