package com.example.demo.entities;

import jakarta.persistence.*;
import lombok.Data;

import java.sql.Date;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Data
@Table(name = "Pets")
public class Pet {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    long id;

    @ManyToOne(fetch = FetchType.EAGER)
    Shelter shelter;

    @OneToMany(mappedBy = "pet")
    List<BasicActivity> basicActivities;

    @ManyToOne(fetch = FetchType.EAGER)
    PetGroup group;

    String name;

    int age;

    double weight;

    double height;

    String description;

    String breed;

    String species;

    LocalDateTime createDt;
}
