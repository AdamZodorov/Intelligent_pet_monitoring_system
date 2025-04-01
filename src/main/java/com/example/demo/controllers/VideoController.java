package com.example.demo.controllers;

import com.example.demo.DTO.ActivityTimingDTO;
import com.example.demo.service.VideoService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class VideoController {
    private final VideoService videoService;

    @GetMapping("/pets/{petId}/video")
    public ResponseEntity<?> getLatestVideoFile(@PathVariable Long petId) {
        try {
            System.out.println("getting video file for " +  petId);
            Resource videoResource = videoService.getLatestVideo(petId);

            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"" + videoResource.getFilename() + "\"")
                    .body(videoResource);

        } catch (EntityNotFoundException | FileNotFoundException e) {
            System.out.println(e.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", e.getMessage()));
        } catch (IOException e) {
            System.out.println(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Ошибка при обработке видеофайла"));
        }
    }

    @GetMapping("/pets/{petId}/activities")
    public ResponseEntity<?> getActivities(
            @PathVariable Long petId) {
        try {
            List<ActivityTimingDTO> timings = videoService.getActivityTimings(petId);
            return ResponseEntity.ok(timings);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", "Ошибка получения данных"));
        }
    }
}
