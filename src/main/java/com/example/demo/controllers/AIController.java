package com.example.demo.controllers;

import com.example.demo.DTO.PetStatDTO;
import com.example.demo.DTO.VideoDTO;
import com.example.demo.service.PetService;
import com.example.demo.service.VideoService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
public class AIController {

    private final VideoService videoService;

    private final PetService petService;

    @GetMapping("/next-video")
    public ResponseEntity<Resource> getNextUnprocessedVideo() throws IOException {
        VideoDTO videoDto = videoService.getUnprocessedVideo();

        return ResponseEntity.ok()
                .header("X-Video-Id", videoDto.getVideoId().toString())
//                .header(HttpHeaders.CONTENT_DISPOSITION,
//                        "attachment; filename=\"" + videoDto.getVideoResource().getFilename() + "\"")
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .body(videoDto.getVideoResource());
    }

    @GetMapping("/pets-photos/{videoId}")
    public ResponseEntity<?> getAnimalPhotos(@PathVariable Long videoId) {
        try {
            System.out.println("Пытаемся вернуть zip, videoID:" + videoId);
            Resource photosZip = petService.getPhotosAsZip(videoId);
            return ResponseEntity.ok(photosZip);
        } catch (Exception e) {
            System.out.println("Ошибка, videoID:" + videoId);
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/pet-stat")
    public ResponseEntity<?> processAIData(@RequestBody PetStatDTO request) {
        try {
            System.out.println("Обработать результаты, request:" + request.toString());
            petService.processPredictions(request);
            return ResponseEntity.ok().build();
        } catch (EntityNotFoundException e) {
            System.out.println("Ошибка, request:" + request.toString());
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            System.out.println("Ошибка, request:" + request.toString());
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            System.out.println("Ошибка, request:" + request.toString());
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "Ошибка обработки данных"));
        }
    }
}