package com.example.demo.entities;

import jakarta.persistence.*;
import lombok.Data;

import java.sql.Date;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Data
@Table(name = "PetGroups")
public class PetGroup {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    long id;

    @ManyToOne(fetch = FetchType.EAGER)
    Shelter shelter;

    @OneToMany(mappedBy = "group")
    List<Video> videos;

    @OneToMany(mappedBy = "group")
    List<Pet> pets;

    long groupNumber;

    LocalDateTime createdDt;
}
