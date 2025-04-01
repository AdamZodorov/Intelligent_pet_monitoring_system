package com.example.demo.service;

import com.example.demo.DTO.LoginResponseDTO;
import com.example.demo.DTO.ShelterLoginDTO;
import com.example.demo.entities.Shelter;
import com.example.demo.model.ShelterDetails;
import com.example.demo.repository.ShelterRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ShelterService {
    final ShelterRepository shelterRepository;

    @Autowired
    private JWTService jwtService;

    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(10);

    final AuthenticationManager authManager;

    public List<Shelter> getAllShelters() {
        return shelterRepository.findAll();
    }

    public Shelter findShelter(long id) {
        return shelterRepository.findShelterById(id);
    }

    public Shelter register(Shelter shelter) {
        if (shelterRepository.findByShelterLogin(shelter.getShelterLogin()) != null) {
            throw new RuntimeException("Приют с таким логином уже существует");
        }
        shelter.setShelterPassword(encoder.encode(shelter.getShelterPassword()));
        return shelterRepository.save(shelter);
    }


    public LoginResponseDTO verify(ShelterLoginDTO shelter) {
        System.out.println(shelter);
        try {
            Authentication auth = authManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            shelter.getLogin(),
                            shelter.getPassword()
                    )
            );

            ShelterDetails shelterDetails = (ShelterDetails) auth.getPrincipal();

            String token = jwtService.generateToken(shelter.getLogin());

            return new LoginResponseDTO(token, shelterDetails.getShelterId());

        } catch (BadCredentialsException e) {
            throw new ResponseStatusException(
                    HttpStatus.UNAUTHORIZED,
                    "Неверный логин или пароль"
            );
        } catch (Exception e) {
            System.out.println("Аутентификация не удалась: " + e.getClass().getName() + " - " + e.getMessage());
            throw e;
        }
    }

}
