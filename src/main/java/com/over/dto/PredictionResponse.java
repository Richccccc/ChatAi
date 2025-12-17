package com.over.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PredictionResponse {
    private String modelName;           // 使用的模型名称
    private Integer prediction;         // 预测结果：0=真实职位，1=虚假职位
    private String predictionLabel;     // 预测结果标签："真实职位" 或 "虚假职位"
    private Double probability;         // 虚假概率（0-1之间）
    private String probabilityPercent;  // 虚假概率百分比字符串
    private Integer riskScore;          // 风险评分（0-7）
    private String riskLevel;           // 风险等级："低风险"、"中风险"、"高风险"
}

