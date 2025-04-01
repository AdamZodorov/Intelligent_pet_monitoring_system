package com.example.demo.repository;

import com.example.demo.entities.PetGroup;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PetGroupRepository extends JpaRepository<PetGroup, Long> {
    PetGroup findGroupById(long id);

    @Query("SELECT g FROM PetGroup g WHERE g.shelter.id = :shelterId AND g.groupNumber = :groupNumber")
    Optional<PetGroup> findByShelterIdAndGroupId(
            @Param("shelterId") Long shelterId,
            @Param("groupNumber") Long groupNumber
    );
}