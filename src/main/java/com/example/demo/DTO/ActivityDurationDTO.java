package com.example.demo.DTO;

import lombok.Data;

@Data
public class ActivityDurationDTO {
    String activityType;
    long duration;

    public ActivityDurationDTO(String activityType, Long duration) {
        this.activityType = activityType;
        this.duration = duration;
    }
}
