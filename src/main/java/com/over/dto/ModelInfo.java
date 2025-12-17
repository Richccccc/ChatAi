package com.over.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ModelInfo {
    private String name;           // 模型名称，如 "Random_Forest", "Gradient_Boosting", "Logistic_Regression"
    private String displayName;    // 显示名称，如 "随机森林", "梯度提升", "逻辑回归"
    private String description;    // 模型描述
    private Boolean available;     // 是否可用（模型文件是否存在）
    private Boolean isSelected;    // 是否为当前选中的模型
}

