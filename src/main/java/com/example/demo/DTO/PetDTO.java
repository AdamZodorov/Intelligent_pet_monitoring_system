package com.example.demo.DTO;

import com.example.demo.entities.Pet;
import lombok.Data;

@Data
public class PetDTO {
    private Long id;

    private int age;

    private double weight;

    private double height;

    private String breed;

    private String species;

    private String name;

    private String description;

    public PetDTO(Pet pet) {
        this.id = pet.getId();
        this.name = pet.getName();
        this.description = pet.getDescription();
        this.age = pet.getAge();
        this.breed = pet.getBreed();
        this.species = pet.getSpecies();
        this.height = pet.getHeight();
        this.weight = pet.getWeight();
    }
}
