package com.example.demo.service;

import com.example.demo.DTO.ActivityTimingDTO;
import com.example.demo.DTO.VideoDTO;
import com.example.demo.entities.BasicActivity;
import com.example.demo.entities.Video;
import com.example.demo.model.ActivityType;
import com.example.demo.repository.VideoRepository;

import jakarta.persistence.EntityNotFoundException;

import com.example.demo.repository.BasicActivityRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.*;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(SpringExtension.class)
class VideoServiceTest {

    @InjectMocks
    private VideoService videoService;

    @Mock
    private VideoRepository videoRepository;

    @Mock
    private BasicActivityRepository basicActivityRepository;

    @Value("${file.video-dir}")
    private Path tempDir;

    @BeforeEach
    void setUp() {
        videoService = new VideoService(videoRepository, basicActivityRepository);
    }

    @Test
    void getLatestVideo_success() throws IOException {
        // Arrange
        Video video = new Video();
        video.setFilePath("video.mp4");

        when(videoRepository.findLatestByPetId(eq(1L), any())).thenReturn(List.of(video));

        Files.createDirectories(tempDir);
        Path videoFile = tempDir.resolve("video.mp4");
        Files.createFile(videoFile);

        // Act
        Resource resource = videoService.getLatestVideo(1L);

        // Assert
        assertNotNull(resource);
        assertTrue(resource.exists());
        assertEquals(videoFile.toUri(), resource.getURI());
    }

    @Test
    void getLatestVideo_notFoundInDb() {
        // Arrange
        when(videoRepository.findLatestByPetId(eq(1L), any())).thenReturn(List.of());

        // Act & Assert
        assertThrows(EntityNotFoundException.class, () -> videoService.getLatestVideo(1L));
    }

    @Test
    void getLatestVideo_fileNotExists() {
        // Arrange
        Video video = new Video();
        video.setFilePath("missing.mp4");

        when(videoRepository.findLatestByPetId(eq(1L), any())).thenReturn(List.of(video));

        // Act & Assert
        assertThrows(FileNotFoundException.class, () -> videoService.getLatestVideo(1L));
    }

    @Test
    void getActivityTimings_success() {
        // Arrange
        Video video = new Video();
        video.setId(100L);
        when(videoRepository.findLatestByPetId(eq(1L), any())).thenReturn(List.of(video));

        BasicActivity activity = new BasicActivity();
        activity.setActivityType(ActivityType.WALKING);
        activity.setStartTimeInSeconds(90L);

        when(basicActivityRepository.findByPetIdAndVideoId(1L, 100L)).thenReturn(List.of(activity));

        // Act
        List<ActivityTimingDTO> timings = videoService.getActivityTimings(1L);

        // Assert
        assertEquals(1, timings.size());
        ActivityTimingDTO dto = timings.get(0);
        assertEquals("00:01:30", dto.getStartTime());
        assertNotNull(dto.getActivityType());
    }

    @Test
    void getUnprocessedVideo_success() throws IOException {
        // Arrange
        Video video = new Video();
        video.setId(1L);
        video.setFilePath("unprocessed.mp4");

        when(videoRepository.findFirstByIsProcessedFalse()).thenReturn(Optional.of(video));

        Files.createDirectories(tempDir);
        Path videoFile = tempDir.resolve("unprocessed.mp4");
        Files.createFile(videoFile);

        // Act
        VideoDTO videoDTO = videoService.getUnprocessedVideo();

        // Assert
        assertEquals(1L, videoDTO.getVideoId());
        assertNotNull(videoDTO.getVideoResource());
        assertTrue(videoDTO.getVideoResource().exists());
    }

    @Test
    void getUnprocessedVideo_notFound() {
        // Arrange
        when(videoRepository.findFirstByIsProcessedFalse()).thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(EntityNotFoundException.class, () -> videoService.getUnprocessedVideo());
    }

    @Test
    void getUnprocessedVideo_fileMissing() {
        // Arrange
        Video video = new Video();
        video.setId(1L);
        video.setFilePath("missing_unprocessed.mp4");

        when(videoRepository.findFirstByIsProcessedFalse()).thenReturn(Optional.of(video));

        // Act & Assert
        assertThrows(FileNotFoundException.class, () -> videoService.getUnprocessedVideo());
    }
}
