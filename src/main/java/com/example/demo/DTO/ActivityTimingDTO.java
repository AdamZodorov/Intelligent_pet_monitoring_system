package com.example.demo.DTO;

import lombok.Data;
import com.example.demo.model.ActivityType;

import java.util.List;

@Data
public class ActivityTimingDTO {
    private String startTime;
    private String activityType;
}