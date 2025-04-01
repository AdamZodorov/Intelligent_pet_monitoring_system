package com.example.demo.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.ArrayList;

@Data
public class PetStatDTO {
    private Long petId;
    private Long videoId;
    private Double videoFps;
    private Long frameIndent;
    private ArrayList<FramePrediction> predictions;

    @Data
    public static class FramePrediction {
        @JsonProperty("frame_idx")
        private long frameIndex;
        private ArrayList<ArrayList<Double>> preds;
    }
}
