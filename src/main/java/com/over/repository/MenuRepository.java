package com.over.repository;

import com.over.entity.Menu;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface MenuRepository extends JpaRepository<Menu, Long> {
    List<Menu> findByStatusOrderBySortOrderAsc(Integer status);
    
    @Query("SELECT m FROM Menu m WHERE m.status = 1 ORDER BY m.sortOrder ASC")
    List<Menu> findAllActiveMenus();
}

