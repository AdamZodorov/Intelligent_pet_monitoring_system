package com.example.demo.entities;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Data
@Table(name = "Videos")
public class Video {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    long id;

    @OneToMany(mappedBy = "video")
    List<BasicActivity> basicActivity;

    @ManyToOne(fetch = FetchType.EAGER)
    PetGroup group;

    String filePath;

    LocalDateTime startTime;

    LocalDateTime endTime;

    boolean isProcessed;
}
