package com.example.demo.controller;

import com.example.demo.DTO.ShelterLoginDTO;
import com.example.demo.DTO.LoginResponseDTO;
import com.example.demo.service.ShelterService;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.persistence.EntityNotFoundException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.test.web.servlet.MockMvc;


class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    ShelterService shelterService;

    @Test
    @DisplayName("Успешная аутентификация приюта")
    void login_success() throws Exception {
        ShelterLoginDTO loginDTO = new ShelterLoginDTO("shelter123", "qwerty123");
        LoginResponseDTO responseDTO = new LoginResponseDTO("mocked-jwt-token", 15L);

        when(shelterService.verify(any(ShelterLoginDTO.class))).thenReturn(responseDTO);

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(new ObjectMapper().writeValueAsString(loginDTO)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").value("mocked-jwt-token"))
                .andExpect(jsonPath("$.shelterId").value(15));
    }

    @Test
    @DisplayName("Неверные учетные данные")
    void login_invalidCredentials() throws Exception {
        ShelterLoginDTO loginDTO = new ShelterLoginDTO("wrongLogin", "wrongPassword");

        when(shelterService.verify(any(ShelterLoginDTO.class)))
                .thenThrow(new BadCredentialsException("Неверный логин или пароль"));

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(new ObjectMapper().writeValueAsString(loginDTO)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.message").value("Неверный логин или пароль"));
    }

    @Test
    @DisplayName("Приют не найден")
    void login_shelterNotFound() throws Exception {
        ShelterLoginDTO loginDTO = new ShelterLoginDTO("notFoundLogin", "password");

        when(shelterService.verify(any(ShelterLoginDTO.class)))
                .thenThrow(new EntityNotFoundException("Приют с указанными данными не существует"));

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(new ObjectMapper().writeValueAsString(loginDTO)))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.message").value("Приют с указанными данными не существует"));
    }

    @Test
    @DisplayName("Внутренняя ошибка сервера при аутентификации")
    void login_internalServerError() throws Exception {
        ShelterLoginDTO loginDTO = new ShelterLoginDTO("anyLogin", "anyPassword");

        when(shelterService.verify(any(ShelterLoginDTO.class)))
                .thenThrow(new RuntimeException("Внутренняя ошибка сервера"));

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(new ObjectMapper().writeValueAsString(loginDTO)))
                .andExpect(status().isInternalServerError())
                .andExpect(jsonPath("$.message").value("Внутренняя ошибка сервера"));
    }
}
