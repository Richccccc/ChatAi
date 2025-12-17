package com.over.repository;

import com.over.entity.JobPosting;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface JobPostingRepository extends JpaRepository<JobPosting, Integer> {
    // Basic CRUD is provided by JpaRepository
}
