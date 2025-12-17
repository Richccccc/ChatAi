package com.over.controller;

import com.over.dto.ApiResponse;
import com.over.dto.LoginRequest;
import com.over.dto.LoginResponse;
import com.over.service.AuthService;
import jakarta.validation.Valid;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping
@CrossOrigin(origins = "*", maxAge = 3600)
public class AuthController {
    
    @Autowired
    private AuthService authService;

    @PostMapping("/login")
    public ApiResponse<LoginResponse.LoginData> login(@Valid @RequestBody LoginRequest request) {
        try {
            LoginResponse response = authService.login(request);
            return ApiResponse.success(response.getData());
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }

    @PostMapping("/refresh-token")
    public ApiResponse<LoginResponse.LoginData> refreshToken(@RequestBody(required = false) RefreshTokenRequest request) {
        try {
            String refreshToken = request != null && request.getRefreshToken() != null 
                    ? request.getRefreshToken() 
                    : "";
            LoginResponse response = authService.refreshToken(refreshToken);
            return ApiResponse.success(response.getData());
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }

    @Data
    static class RefreshTokenRequest {
        private String refreshToken;
    }
}

