package com.over.service;

import com.over.dto.MenuDTO;
import com.over.entity.Menu;
import com.over.repository.MenuRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class MenuService {
    
    @Autowired
    private MenuRepository menuRepository;

    public List<MenuDTO> getMenuTree() {
        List<Menu> menus = menuRepository.findAllActiveMenus();
        return buildMenuTree(menus, 0L);
    }

    private String formatPathToName(String path) {
        if (path == null || path.isEmpty()) return "";
        String[] parts = path.split("/");
        StringBuilder name = new StringBuilder();
        for (String part : parts) {
            if (!part.isEmpty()) {
                // 首字母大写
                name.append(part.substring(0, 1).toUpperCase());
                if (part.length() > 1) {
                    name.append(part.substring(1));
                }
            }
        }
        return name.toString();
    }

    private List<MenuDTO> buildMenuTree(List<Menu> menus, Long parentId) {
        return menus.stream()
                .filter(menu -> parentId.equals(menu.getParentId()))
                .map(menu -> {
                    MenuDTO dto = new MenuDTO();
                    dto.setPath(menu.getPath());
                    // 生成name，使用Path去除开头的/并转驼峰，或者直接使用Menu + ID
                    String name = menu.getPath() != null ? 
                        formatPathToName(menu.getPath()) : 
                        "Menu" + menu.getId();
                    dto.setName(name);
                    dto.setComponent(menu.getComponent() != null ? menu.getComponent() : "layout");
                    
                    MenuDTO.Meta meta = new MenuDTO.Meta();
                    meta.setTitle(menu.getMenuName());
                    meta.setIcon(menu.getIcon());
                    meta.setRank(menu.getSortOrder());
                    // 可以根据需要设置roles和auths
                    dto.setMeta(meta);
                    
                    // 递归构建子菜单
                    List<MenuDTO> children = buildMenuTree(menus, menu.getId());
                    // 确保children不为null，如果为空则设置为空列表
                    dto.setChildren(children != null && !children.isEmpty() ? children : new ArrayList<>());
                    
                    return dto;
                })
                .sorted((a, b) -> {
                    int rankA = a.getMeta() != null && a.getMeta().getRank() != null ? a.getMeta().getRank() : 0;
                    int rankB = b.getMeta() != null && b.getMeta().getRank() != null ? b.getMeta().getRank() : 0;
                    return Integer.compare(rankA, rankB);
                })
                .collect(Collectors.toList());
    }
}

