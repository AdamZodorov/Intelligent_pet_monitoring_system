package com.example.demo.entities;

import com.example.demo.model.ActivityType;
import jakarta.persistence.*;
import lombok.Data;

import java.sql.Date;
import java.time.LocalDateTime;

@Entity
@Data
@Table(name = "BasicActivities")
public class BasicActivity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    long id;

    @ManyToOne(fetch = FetchType.EAGER)
    Pet pet;

    @ManyToOne(fetch = FetchType.EAGER)
    Video video;

    ActivityType activityType;

    long startTimeInSeconds;

    long endTimeInSeconds;
}