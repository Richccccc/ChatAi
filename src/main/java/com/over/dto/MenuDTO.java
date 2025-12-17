package com.over.dto;

import lombok.Data;
import java.util.List;

@Data
public class MenuDTO {
    private String path;
    private String name;
    private String component;
    private Meta meta;
    private List<MenuDTO> children;

    @Data
    public static class Meta {
        private String title;
        private String icon;
        private Integer rank;
        private List<String> roles;
        private List<String> auths;
    }
}

