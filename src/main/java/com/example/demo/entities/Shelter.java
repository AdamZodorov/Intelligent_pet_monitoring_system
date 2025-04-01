package com.example.demo.entities;

import jakarta.persistence.*;
import lombok.Data;

import java.sql.Date;
import java.util.List;


@Entity
@Data
@Table(name = "Shelters")
public class Shelter {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    long id;

    @OneToMany(mappedBy = "shelter")
    List<Pet> pets;

    @OneToMany(mappedBy = "shelter")
    List<PetGroup> groups;

    String name;

    String shelterLogin;

    String shelterPassword;

    String email;

    String description;

    Date createDt;

    public Shelter() {
    }

    public Shelter(String name, String shelterLogin, String shelterPassword, String email) {
        this.name = name;
        this.shelterLogin = shelterLogin;
        this.shelterPassword = shelterPassword;
        this.createDt = new Date(System.currentTimeMillis());
        this.email = email;
    }
}
