package com.example.demo.service;

import com.example.demo.entities.Shelter;
import com.example.demo.model.ShelterDetails;
import com.example.demo.repository.ShelterRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class ShelterDetailsService implements UserDetailsService {

    @Autowired
    private ShelterRepository shelterRepository;

    @Override
    public UserDetails loadUserByUsername(String shelterName) throws UsernameNotFoundException {
        Shelter shelter = shelterRepository.findByShelterLogin(shelterName);
        if (shelter == null) {
            System.out.println("shelter not found");
            throw new UsernameNotFoundException("shelter not found");
        }
        return new ShelterDetails(shelter);
    }
}
