package com.example.demo.service;

import com.example.demo.DTO.ActivityTimingDTO;
import com.example.demo.DTO.VideoDTO;
import com.example.demo.entities.BasicActivity;
import com.example.demo.entities.Video;
import com.example.demo.model.ActivityType;
import com.example.demo.repository.BasicActivityRepository;
import com.example.demo.repository.VideoRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class VideoService {
    private final VideoRepository videoRepository;
    private final BasicActivityRepository basicActivityRepository;

    private static final Map<ActivityType, List<String>> ACTIVITY_STATUSES = Map.ofEntries(
            Map.entry(ActivityType.KEEPING_STILL, List.of(
                    "Питомец замер. Видимо, размышляет о вечном."
            )),
            Map.entry(ActivityType.WALKING, List.of(
                    "Грациозно шагает."
            )),
            Map.entry(ActivityType.EATING, List.of(
                    "В процессе трапезы. Судя по звукам — очень доволен."
            )),
            Map.entry(ActivityType.MOVING, List.of(
                    "Куда-то идет. Похоже, у него важные дела."
            )),
            Map.entry(ActivityType.RUNNING, List.of(
                    "Устроил марафон без зрителей."
            )),
            Map.entry(ActivityType.DRINKING, List.of(
                    "Поддерживает водный баланс"
            )),
            Map.entry(ActivityType.ATTACKING, List.of(
                    "Цель обезврежена. Миссия выполнена."
            )),
            Map.entry(ActivityType.FIGHTING, List.of(
                    "Вступил в схватку за уютное место. Победил."
            )),
            Map.entry(ActivityType.DISPLAYING_DEFENSIVE_POSE, List.of(
                    "Настроен серьёзно. Лучше не подходить без вкусняшки."
            )),
            Map.entry(ActivityType.STANDING, List.of(
                    "Замер. Анализирует обстановку."
            )),
            Map.entry(ActivityType.SITTING, List.of(
                    "Сидит, как истинный философ. Или просто отдыхает."
            )),
            Map.entry(ActivityType.RESTING, List.of(
                    "Отдыхает. Восстановление сил идёт по плану."
            )),
            Map.entry(ActivityType.LYING_DOWN, List.of(
                    "В лежачем состоянии достиг просветления."
            ))
    );

    @Value("${file.video-dir}")
    private Path videoDir;

    public Resource getLatestVideo(Long petId) throws IOException {
        Video video = videoRepository.findLatestByPetId(petId, PageRequest.of(0, 1))
                .stream()
                .findFirst()
                .orElseThrow(() -> new EntityNotFoundException("Видео для питомца с ID " + petId + " не найдено"));


        String relativePath = video.getFilePath();
        if (relativePath == null || relativePath.isBlank()) {
            throw new FileNotFoundException("Путь к видео не указан");
        }

        Path filePath = videoDir.resolve(relativePath).normalize();
        System.out.println("videoDir: " + videoDir);
        System.out.println("relative path: " + relativePath);
        if (!Files.exists(filePath)) {
            throw new FileNotFoundException("Видеофайл не найден: " + filePath);
        }

        return new UrlResource(filePath.toUri());
    }

    public List<ActivityTimingDTO> getActivityTimings(Long petId) {
        Video video = videoRepository.findLatestByPetId(petId, PageRequest.of(0, 1))
                .stream()
                .findFirst()
                .orElseThrow(() -> new EntityNotFoundException("Видео для питомца с ID " + petId + " не найдено"));

//        List<BasicActivity> activities = basicActivityRepository.findActivitiesInTimeRange(
//                petId, videoStart, videoEnd);
        List<BasicActivity> activities = basicActivityRepository.findByPetIdAndVideoId(petId, video.getId());

        return activities.stream()
                .map(this::convertToTimingDTO)
                .sorted(Comparator.comparing(ActivityTimingDTO::getStartTime))
                .collect(Collectors.toList());
    }

    private ActivityTimingDTO convertToTimingDTO(BasicActivity activity) {
        ActivityTimingDTO dto = new ActivityTimingDTO();

        long startSeconds = activity.getStartTimeInSeconds();

        dto.setStartTime(formatSeconds(startSeconds));
        List<String> statuses = ACTIVITY_STATUSES
                .getOrDefault(activity.getActivityType(), List.of("Статус недоступен"));
        dto.setActivityType(statuses.get(new Random().nextInt(statuses.size())));

        return dto;
    }

    private String formatSeconds(long totalSeconds) {
        long hours = totalSeconds / 3600;
        long minutes = (totalSeconds % 3600) / 60;
        long seconds = totalSeconds % 60;

        return String.format("%02d:%02d:%02d", hours, minutes, seconds);
    }

    public VideoDTO getUnprocessedVideo() throws IOException {
       Video video = videoRepository.findFirstByIsProcessedFalse()
               .orElseThrow(() -> new EntityNotFoundException("Нет необработанных видео"));
        // Video video = null;
        String relativePath = video.getFilePath();
        Path filePath = videoDir.resolve(relativePath).normalize();
        System.out.println("Отпарвка видео AI сервису: " + relativePath);
        if (!Files.exists(filePath)) {
            System.out.println("Ошибка отправки AI сервису: " + relativePath);
            throw new FileNotFoundException("Видеофайл не найден: " + filePath);
        }

        return new VideoDTO(
                video.getId(),
                new UrlResource(filePath.toUri())
        );
    }
}
