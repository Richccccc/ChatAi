package com.over.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "menu")
@Data
public class Menu {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "parent_id")
    private Long parentId = 0L;

    @Column(name = "menu_name", nullable = false, length = 50)
    private String menuName;

    @Column(name = "menu_type", columnDefinition = "TINYINT(1) DEFAULT 1")
    private Integer menuType = 1;

    @Column(length = 200)
    private String path;

    @Column(length = 200)
    private String component;

    @Column(length = 50)
    private String icon;

    @Column(name = "sort_order")
    private Integer sortOrder = 0;

    @Column(columnDefinition = "TINYINT(1) DEFAULT 1")
    private Integer status = 1;

    @Column(name = "is_external", columnDefinition = "TINYINT(1) DEFAULT 0")
    private Integer isExternal = 0;

    @Column(length = 100)
    private String permission;

    @Column(name = "create_time", updatable = false)
    private LocalDateTime createTime;

    @Column(name = "update_time")
    private LocalDateTime updateTime;

    @Column(length = 500)
    private String remark;

    @PrePersist
    protected void onCreate() {
        createTime = LocalDateTime.now();
        updateTime = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updateTime = LocalDateTime.now();
    }
}

