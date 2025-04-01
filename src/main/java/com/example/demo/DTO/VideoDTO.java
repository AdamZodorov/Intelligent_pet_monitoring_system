package com.example.demo.DTO;

import com.example.demo.entities.Video;
import lombok.Data;
import org.springframework.core.io.Resource;

@Data
public class VideoDTO {
    private Long videoId;
    private Resource videoResource;

    public VideoDTO(Long videoId, Resource videoResource) {
        this.videoId = videoId;
        this.videoResource = videoResource;
    }
    public VideoDTO(Video video) {}
}
