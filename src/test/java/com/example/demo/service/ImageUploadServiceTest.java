package com.example.demo.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

class ImageUploadServiceTest {

    private ImageUploadService imageUploadService;
    @Value("${file.upload-dir}")
    private String uploadDir;

    @Value("${file.temp-dir}")
    private String tempDir;

    @BeforeEach
    void setUp() {
        imageUploadService = new ImageUploadService();
    }

    @Test
    void saveTempImage_shouldSaveImageSuccessfully() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "test.jpg",
                "image/jpeg",
                "fake image content".getBytes()
        );

        String tempId = imageUploadService.saveTempImage(file);

        assertNotNull(tempId);

        boolean fileExists = Files.list(Path.of(tempDir))
                .anyMatch(path -> path.getFileName().toString().startsWith(tempId));
        assertTrue(fileExists);
    }

    @Test
    void saveTempImage_shouldThrowExceptionForInvalidFile() {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "test.txt",
                "text/plain",
                "not an image".getBytes()
        );

        assertThrows(IllegalArgumentException.class, () -> {
            imageUploadService.saveTempImage(file);
        });
    }

}
