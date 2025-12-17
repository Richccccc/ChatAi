package com.over.service;

import com.over.entity.JobPosting;
import com.over.repository.JobPostingRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class JobPostingService {

    @Autowired
    private JobPostingRepository jobPostingRepository;

    public Page<JobPosting> getJobPostings(Pageable pageable) {
        return jobPostingRepository.findAll(pageable);
    }

    public Optional<JobPosting> getJobPostingById(Integer id) {
        return jobPostingRepository.findById(id);
    }

    public JobPosting createJobPosting(JobPosting jobPosting) {
        return jobPostingRepository.save(jobPosting);
    }

    public JobPosting updateJobPosting(Integer id, JobPosting jobPostingDetails) {
        return jobPostingRepository.findById(id).map(jobPosting -> {
            jobPosting.setTitle(jobPostingDetails.getTitle());
            jobPosting.setLocation(jobPostingDetails.getLocation());
            jobPosting.setDepartment(jobPostingDetails.getDepartment());
            jobPosting.setSalaryRange(jobPostingDetails.getSalaryRange());
            jobPosting.setCompanyProfile(jobPostingDetails.getCompanyProfile());
            jobPosting.setDescription(jobPostingDetails.getDescription());
            jobPosting.setRequirements(jobPostingDetails.getRequirements());
            jobPosting.setBenefits(jobPostingDetails.getBenefits());
            jobPosting.setTelecommuting(jobPostingDetails.getTelecommuting());
            jobPosting.setHasCompanyLogo(jobPostingDetails.getHasCompanyLogo());
            jobPosting.setHasQuestions(jobPostingDetails.getHasQuestions());
            jobPosting.setEmploymentType(jobPostingDetails.getEmploymentType());
            jobPosting.setRequiredExperience(jobPostingDetails.getRequiredExperience());
            jobPosting.setRequiredEducation(jobPostingDetails.getRequiredEducation());
            jobPosting.setIndustry(jobPostingDetails.getIndustry());
            jobPosting.setJobFunction(jobPostingDetails.getJobFunction());
            jobPosting.setFraudulent(jobPostingDetails.getFraudulent());
            return jobPostingRepository.save(jobPosting);
        }).orElseThrow(() -> new RuntimeException("Job posting not found with id " + id));
    }

    public void deleteJobPosting(Integer id) {
        jobPostingRepository.deleteById(id);
    }
}
