package com.example.demo.DTO;

import com.example.demo.entities.Pet;
import com.example.demo.entities.Shelter;
import lombok.Data;

import java.util.List;

@Data
public class ShelterDTO {
    private long id;

    private String name;

    private String description;

    public ShelterDTO(Shelter shelter) {
        this.setId(shelter.getId());
        this.setName(shelter.getName());
        this.setDescription(shelter.getDescription());
    }
}
