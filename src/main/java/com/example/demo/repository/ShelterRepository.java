package com.example.demo.repository;

import com.example.demo.entities.Shelter;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ShelterRepository extends JpaRepository<Shelter, Long> {
    Shelter findShelterById(long id);

    Shelter findByShelterLogin(String shelterName);
}