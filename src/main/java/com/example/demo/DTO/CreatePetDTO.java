package com.example.demo.DTO;

import lombok.Data;

import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import java.util.List;

@Data
public class CreatePetDTO {
    @NotBlank(message = "Name is required")
    private String name;

    @Min(value = 0, message = "Age must be positive")
    @NotNull(message = "Age is required")
    private int age;

    @Min(value = 0, message = "Weight must be positive")
    @NotNull(message = "Weight is required")
    private double weight;

    @Min(value = 0, message = "Height must be positive")
    @NotNull(message = "Height is required")
    private double height;

    @NotBlank(message = "Breed is required")
    private String breed;

    @NotBlank(message = "Species is required")
    private String species;

    @NotBlank(message = "Main image is required")
    private String mainImageId;

    @Size(min = 8, max = 8, message = "8 images are required")
    private List<String> tempImageIds;

    @NotBlank(message = "Group is required")
    private long group;

    @NotBlank(message = "Description is required")
    private String description;
}
