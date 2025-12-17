package com.over.entity;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "job_postings")
public class JobPosting {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "job_id")
    private Integer jobId;

    private String title;
    private String location;
    private String department;
    
    @Column(name = "salary_range")
    private String salaryRange;

    @Column(columnDefinition = "TEXT", name = "company_profile")
    private String companyProfile;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(columnDefinition = "TEXT")
    private String requirements;

    @Column(columnDefinition = "TEXT")
    private String benefits;

    private Integer telecommuting;
    
    @Column(name = "has_company_logo")
    private Integer hasCompanyLogo;
    
    @Column(name = "has_questions")
    private Integer hasQuestions;
    
    @Column(name = "employment_type")
    private String employmentType;
    
    @Column(name = "required_experience")
    private String requiredExperience;
    
    @Column(name = "required_education")
    private String requiredEducation;
    
    private String industry;
    
    @Column(name = "function")
    private String jobFunction; // 'function' is a reserved keyword in some contexts, safer to name field jobFunction
    
    private Integer fraudulent;
}
