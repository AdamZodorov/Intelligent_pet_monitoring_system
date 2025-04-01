package com.example.demo.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import com.example.demo.service.PetService;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class ShelterControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void getAllShelters_ReturnsListOfShelters() throws Exception {
        mockMvc.perform(get("/api/shelters"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json"))
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$[0].id").exists())
                .andExpect(jsonPath("$[0].name").exists())
                .andExpect(jsonPath("$[0].description").exists());
    }

    @Test
    void getShelterById_ReturnsShelter_WhenExists() throws Exception {
        int shelterId = 1;

        mockMvc.perform(get("/api/shelters/{id}", shelterId))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json"))
                .andExpect(jsonPath("$.id").value(shelterId))
                .andExpect(jsonPath("$.name").exists())
                .andExpect(jsonPath("$.description").exists());
    }

    @Test
    void getShelterById_ReturnsNotFound_WhenDoesNotExist() throws Exception {
        int nonExistingShelterId = 9999;

        mockMvc.perform(get("/api/shelters/{id}", nonExistingShelterId))
                .andExpect(status().isNotFound());
    }

    @Test
    void getPetsByShelterId_ReturnsListOfPets_WhenShelterExists() throws Exception {
        int shelterId = 1;

        mockMvc.perform(get("/api/shelters/{id}/pets", shelterId))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json"))
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$[0].id").exists())
                .andExpect(jsonPath("$[0].age").exists())
                .andExpect(jsonPath("$[0].weight").exists())
                .andExpect(jsonPath("$[0].height").exists())
                .andExpect(jsonPath("$[0].breed").exists())
                .andExpect(jsonPath("$[0].species").exists())
                .andExpect(jsonPath("$[0].name").exists())
                .andExpect(jsonPath("$[0].description").exists());
    }

    @Test
    void getPetsByShelterId_ReturnsNotFound_WhenShelterDoesNotExist() throws Exception {
        int nonExistingShelterId = 9999;

        mockMvc.perform(get("/api/shelters/{id}/pets", nonExistingShelterId))
                .andExpect(status().isNotFound());
    }
}
