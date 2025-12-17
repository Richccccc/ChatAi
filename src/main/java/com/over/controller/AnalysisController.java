package com.over.controller;

import com.over.dto.ApiResponse;
import com.over.service.AnalysisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/analysis")
@CrossOrigin(origins = "*", maxAge = 3600)
public class AnalysisController {

    @Autowired
    private AnalysisService analysisService;

    @PostMapping("/run")
    public ApiResponse<String> runAnalysis() {
        try {
            // 直接返回 JSON 字符串
            String jsonResult = analysisService.runPythonAnalysis();
            return ApiResponse.success(jsonResult);
        } catch (Exception e) {
            return ApiResponse.error("启动分析失败: " + e.getMessage());
        }
    }

    @GetMapping("/images")
    public ApiResponse<List<String>> getAnalysisImages() {
        return ApiResponse.success(analysisService.getAnalysisImageNames());
    }

    @GetMapping(value = "/image/{filename}", produces = MediaType.IMAGE_PNG_VALUE)
    public ResponseEntity<byte[]> getImage(@PathVariable String filename) {
        try {
            byte[] imageBytes = analysisService.getImageBytes(filename);
            return ResponseEntity.ok().contentType(MediaType.IMAGE_PNG).body(imageBytes);
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
}

