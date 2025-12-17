package com.over.controller;

import com.over.dto.ApiResponse;
import com.over.dto.MenuDTO;
import com.over.service.MenuService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping
@CrossOrigin(origins = "*", maxAge = 3600)
public class MenuController {
    
    @Autowired
    private MenuService menuService;

    @GetMapping("/get-async-routes")
    public ApiResponse<List<MenuDTO>> getAsyncRoutes() {
        try {
            List<MenuDTO> menus = menuService.getMenuTree();
            return ApiResponse.success(menus);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
}

