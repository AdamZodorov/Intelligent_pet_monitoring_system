package com.example.demo.model;

import com.example.demo.entities.Shelter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.Collections;
import java.util.List;

public class ShelterDetails implements UserDetails {

    private final Shelter shelter;

    public ShelterDetails(Shelter shelter){
        this.shelter = shelter;
    }

    public Long getShelterId() {
        return shelter.getId();
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singleton(new SimpleGrantedAuthority("ROLE_SHELTER"));
    }

    @Override
    public String getPassword() {
        return shelter.getShelterPassword();
    }

    @Override
    public String getUsername() {
        return shelter.getShelterLogin();
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return true;
    }
}
