package com.example.demo.controllers;

import com.example.demo.service.ImageUploadService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/uploads")
@RequiredArgsConstructor
public class ImageController {
    private final ImageUploadService imageUploadService;

    @PostMapping("/temp")
    @PreAuthorize("hasRole('SHELTER')")
    public ResponseEntity<Map<String, String>> uploadTempImage(
            @RequestParam("file") MultipartFile file) {
        try {
            String tempId = imageUploadService.saveTempImage(file);
            return ResponseEntity.ok(Map.of("tempId", tempId));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error uploading image: " + e.getMessage()));
        }
    }

    @DeleteMapping("/temp/{tempId}")
    @PreAuthorize("hasRole('SHELTER')")
    public ResponseEntity<?> deleteTempImage(@PathVariable String tempId) {
        try {
            boolean deleted = imageUploadService.deleteTempImage(tempId);
            if (deleted) {
                return ResponseEntity.ok(Map.of("message", "Image deleted successfully"));
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Image not found"));
            }
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error deleting image: " + e.getMessage()));
        }
    }
}
