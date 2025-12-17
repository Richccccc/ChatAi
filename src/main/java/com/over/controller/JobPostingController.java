package com.over.controller;

import com.over.entity.JobPosting;
import com.over.service.JobPostingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/job-postings")
public class JobPostingController {

    @Autowired
    private JobPostingService jobPostingService;

    @GetMapping
    public ResponseEntity<Map<String, Object>> getAllJobPostings(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "jobId") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir) {

        Sort sort = sortDir.equalsIgnoreCase(Sort.Direction.ASC.name()) ? Sort.by(sortBy).ascending()
                : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page - 1, size, sort); // Frontend usually sends 1-based page index

        Page<JobPosting> jobPostingPage = jobPostingService.getJobPostings(pageable);

        Map<String, Object> response = new HashMap<>();
        response.put("list", jobPostingPage.getContent());
        response.put("total", jobPostingPage.getTotalElements());
        response.put("pageSize", size);
        response.put("currentPage", page);
        
        // Wrap in standard response structure if needed, but for now returning direct map
        // Matching common pure-admin response format: { success: true, data: { ... } }
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("data", response);

        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getJobPostingById(@PathVariable Integer id) {
        return jobPostingService.getJobPostingById(id)
                .map(jobPosting -> {
                    Map<String, Object> result = new HashMap<>();
                    result.put("success", true);
                    result.put("data", jobPosting);
                    return ResponseEntity.ok(result);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> createJobPosting(@RequestBody JobPosting jobPosting) {
        JobPosting created = jobPostingService.createJobPosting(jobPosting);
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("data", created);
        return ResponseEntity.ok(result);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateJobPosting(@PathVariable Integer id, @RequestBody JobPosting jobPostingDetails) {
        try {
            JobPosting updated = jobPostingService.updateJobPosting(id, jobPostingDetails);
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", updated);
            return ResponseEntity.ok(result);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteJobPosting(@PathVariable Integer id) {
        jobPostingService.deleteJobPosting(id);
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "Job posting deleted successfully");
        return ResponseEntity.ok(result);
    }
}
