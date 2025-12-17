package com.over.service;

import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Service
public class AnalysisService {

    private static final String SCRIPT_PATH = "model/analysis/realtime_analysis.py";

    // 可以在应用启动时自动运行分析
    @PostConstruct
    public void init() {
        // 使用新线程异步启动，避免阻塞 Spring Boot 启动
        new Thread(() -> {
            try {
                // 等待几秒，确保数据库连接等资源就绪
                Thread.sleep(5000); 
                String result = runPythonAnalysis();
                System.out.println("启动时自动分析完成，结果长度: " + (result != null ? result.length() : "null"));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

    public String runPythonAnalysis() {
        StringBuilder output = new StringBuilder();
        try {
            File scriptFile = new File(SCRIPT_PATH);
            if (!scriptFile.exists()) {
                // Try absolute path if relative fails
                File absoluteFile = new File(System.getProperty("user.dir"), SCRIPT_PATH);
                if (!absoluteFile.exists()) {
                    return "{\"error\": \"Script not found: " + SCRIPT_PATH + "\"}";
                }
                scriptFile = absoluteFile;
            }

            ProcessBuilder processBuilder = new ProcessBuilder("python", scriptFile.getAbsolutePath());
            processBuilder.redirectErrorStream(true);
            
            // Set encoding to UTF-8 to handle Chinese characters correctly
            processBuilder.environment().put("PYTHONIOENCODING", "utf-8");
            
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"));
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                return "{\"error\": \"Analysis script failed with exit code " + exitCode + "\", \"details\": \"" + output.toString().replace("\"", "'") + "\"}";
            }

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            return "{\"error\": \"Execution failed: " + e.getMessage() + "\"}";
        }
        
        // Find the JSON part if there are other logs
        String result = output.toString();
        int jsonStart = result.indexOf("{");
        int jsonEnd = result.lastIndexOf("}");
        if (jsonStart != -1 && jsonEnd != -1) {
            return result.substring(jsonStart, jsonEnd + 1);
        }
        
        return result;
    }

    public List<String> getAnalysisImageNames() {
        return Collections.emptyList();
    }

    public byte[] getImageBytes(String filename) throws IOException {
        return new byte[0];
    }
}
