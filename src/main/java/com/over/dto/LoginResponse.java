package com.over.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Date;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponse {
    private Boolean success;
    private LoginData data;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LoginData {
        private String avatar;
        private String username;
        private String nickname;
        private List<String> roles;
        private List<String> permissions;
        private String accessToken;
        private String refreshToken;
        private Date expires;
    }
}

