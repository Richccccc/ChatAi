package com.over.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PredictionRequest {
    private String modelName;      // 可选：指定使用的模型，如果不指定则使用当前选中的模型
    
    // 职位信息字段
    private String title;
    private String location;
    private String department;
    private String salaryRange;
    private String companyProfile;
    private String description;
    private String requirements;
    private String benefits;
    private Integer telecommuting;
    private Integer hasCompanyLogo;
    private Integer hasQuestions;
    private String employmentType;
    private String requiredExperience;
    private String requiredEducation;
    private String industry;
    private String function;
}

