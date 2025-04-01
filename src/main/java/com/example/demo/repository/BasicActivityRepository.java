package com.example.demo.repository;

import com.example.demo.DTO.PetStatDTO;
import com.example.demo.entities.BasicActivity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface BasicActivityRepository extends JpaRepository<BasicActivity, Long> {
    BasicActivity findBasicActivityById(long id);

//    @Query("""
//        SELECT a
//        FROM BasicActivity a
//        WHERE
//            a.pet.id = :petId
//            AND a.startTime <= :end
//            AND a.endTime >= :start
//        """)
//    List<BasicActivity> findActivitiesInTimeRange(
//            @Param("petId") Long petId,
//            @Param("start") LocalDateTime start,
//            @Param("end") LocalDateTime end
//    );

    void deleteByPetId(Long petId);

    List<BasicActivity> findByPetId(Long petId);

    List<BasicActivity> findByPetIdAndVideoId(long petId, long videoId);
}