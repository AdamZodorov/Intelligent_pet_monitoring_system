package com.example.demo.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.FileNotFoundException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Service
public class ImageUploadService {
    @Value("${file.upload-dir}")
    private String uploadDir;

    @Value("${file.temp-dir}")
    private String tempDir;

    public String saveTempImage(MultipartFile file) throws IOException {
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new IllegalArgumentException("File must be an image");
        }

        String tempId = UUID.randomUUID().toString();

        String originalFilename = file.getOriginalFilename();
        String extension = originalFilename != null ?
                originalFilename.substring(originalFilename.lastIndexOf(".")) : ".jpg";

        Path path = Paths.get(tempDir);
        if (!Files.exists(path)) {
            Files.createDirectories(path);
        }

        Path tempFilePath = path.resolve(tempId + extension);
        Files.copy(file.getInputStream(), tempFilePath, StandardCopyOption.REPLACE_EXISTING);

        return tempId;
    }

    public String moveTempImageToPermanent(String tempId, Long petId, int imageIndex) throws IOException {
        Path path = Paths.get(tempDir);

        try (DirectoryStream<Path> stream = Files.newDirectoryStream(path, tempId + ".*")) {
            for (Path tempFile : stream) {
                Path petImagesPath = Paths.get(uploadDir, petId.toString());
                if (!Files.exists(petImagesPath)) {
                    Files.createDirectories(petImagesPath);
                }

                String filename = tempFile.getFileName().toString();
                String extension = filename.substring(filename.lastIndexOf("."));

                String newFilename = imageIndex + extension;
                Path targetPath = petImagesPath.resolve(newFilename);

                Files.move(tempFile, targetPath, StandardCopyOption.REPLACE_EXISTING);

                return petId + "/" + newFilename;
            }
        }

        throw new FileNotFoundException("Temporary image not found: " + tempId);
    }

    public boolean deleteTempImage(String tempId) throws IOException {
        Path path = Paths.get(tempDir);
        boolean deleted = false;

        try (DirectoryStream<Path> stream = Files.newDirectoryStream(path, tempId + ".*")) {
            for (Path tempFile : stream) {
                Files.delete(tempFile);
                deleted = true;
            }
        }

        return deleted;
    }


}
