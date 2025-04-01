package com.example.demo.controller;

import com.example.demo.controllers.PetController;
import com.example.demo.entities.Pet;
import com.example.demo.service.PetService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(PetController.class)
class PetControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PetService petService;

    @Test
    @DisplayName("Успешное получение информации о животном")
    void getPetById_success() throws Exception {
        Pet pet = new Pet();
        pet.setId(1);
        pet.setAge(5);
        pet.setWeight(10.5);
        pet.setHeight(30.0);
        pet.setBreed("Labrador");
        pet.setSpecies("Dog");
        pet.setName("Buddy");
        pet.setDescription("Friendly dog");

        when(petService.findPetById(pet.getId())).thenReturn(pet);

        mockMvc.perform(get("/api/pets/1"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.age").value(5))
                .andExpect(jsonPath("$.weight").value(10.5))
                .andExpect(jsonPath("$.height").value(30.0))
                .andExpect(jsonPath("$.breed").value("Labrador"))
                .andExpect(jsonPath("$.species").value("Dog"))
                .andExpect(jsonPath("$.name").value("Buddy"))
                .andExpect(jsonPath("$.description").value("Friendly dog"));
    }

    @Test
    @DisplayName("Животное не найдено")
    void getPetById_notFound() throws Exception {
        when(petService.findPetById((long) 999)).thenReturn(null);

        mockMvc.perform(get("/api/pets/999"))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("Успешное получение фото животного")
    void getPetPhoto_success() throws Exception {
        byte[] photoBytes = new byte[]{1, 2, 3, 4};
        Resource photoResource = new ByteArrayResource(photoBytes);

        when(petService.getPetPhoto((long) 999)).thenReturn(photoResource);

        mockMvc.perform(get("/api/pets/1/photo"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.IMAGE_JPEG))
                .andExpect(content().bytes(photoBytes));
    }

    @Test
    @DisplayName("Фото животного не найдено")
    void getPetPhoto_notFound() throws Exception {
        when(petService.getPetPhoto((long) 999)).thenReturn(null);

        mockMvc.perform(get("/api/pets/999/photo"))
                .andExpect(status().isNotFound());
    }
}
