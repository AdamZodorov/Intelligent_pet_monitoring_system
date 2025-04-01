package com.example.demo.entities;

import jakarta.persistence.*;
import lombok.Data;

import java.sql.Date;
import java.time.LocalDateTime;
import java.util.List;

//@Entity
//@Data
//@Table(name = "Events")
//public class Event {
//    @Id
//    @GeneratedValue(strategy = GenerationType.IDENTITY)
//    @Column(name = "id")
//    long id;
//
//    @ManyToMany(fetch = FetchType.EAGER)
//    @JoinTable(
//            name = "event_participants",
//            joinColumns = @JoinColumn(name = "event_id"),
//            inverseJoinColumns = @JoinColumn(name = "pet_id")
//    )
//    List<Pet> pets;
//
//    @OneToOne(fetch = FetchType.EAGER)
//    Video video;
//
//    LocalDateTime startTime;
//
//    LocalDateTime endTime;
//
//    String type;
//
//    String description;
//}
