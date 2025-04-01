package com.example.demo.repository;

import com.example.demo.entities.Video;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface VideoRepository extends JpaRepository<Video, Long> {
    Video findVideoById(long id);

    @Query("SELECT v FROM Video v JOIN v.group g JOIN g.pets p WHERE p.id = :petId ORDER BY v.startTime DESC")
    List<Video> findLatestByPetId(@Param("petId") Long petId, Pageable pageable);

    Optional<Video> findFirstByIsProcessedFalse();
}