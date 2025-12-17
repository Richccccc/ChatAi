package com.over.controller;

import com.over.dto.ApiResponse;
import com.over.dto.ModelInfo;
import com.over.dto.PredictionRequest;
import com.over.dto.PredictionResponse;
import com.over.service.ModelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/model")
public class ModelController {

    @Autowired
    private ModelService modelService;

    /**
     * 获取所有可用模型列表
     */
    @GetMapping("/list")
    public ApiResponse<List<ModelInfo>> getAllModels() {
        try {
            List<ModelInfo> models = modelService.getAllModels();
            return ApiResponse.success(models);
        } catch (Exception e) {
            return ApiResponse.error("获取模型列表失败: " + e.getMessage());
        }
    }

    /**
     * 获取当前选中的模型
     */
    @GetMapping("/current")
    public ApiResponse<String> getCurrentModel() {
        try {
            String currentModel = modelService.getCurrentModel();
            return ApiResponse.success(currentModel);
        } catch (Exception e) {
            return ApiResponse.error("获取当前模型失败: " + e.getMessage());
        }
    }

    /**
     * 切换模型
     */
    @PostMapping("/switch")
    public ApiResponse<String> switchModel(@RequestBody SwitchModelRequest request) {
        try {
            boolean success = modelService.switchModel(request.getModelName());
            if (success) {
                return ApiResponse.success("模型切换成功: " + request.getModelName());
            } else {
                return ApiResponse.error("模型切换失败: 模型不可用或不存在");
            }
        } catch (Exception e) {
            return ApiResponse.error("模型切换失败: " + e.getMessage());
        }
    }

    /**
     * 使用模型进行预测
     */
    @PostMapping("/predict")
    public ApiResponse<PredictionResponse> predict(@RequestBody PredictionRequest request) {
        try {
            PredictionResponse response = modelService.predict(request);
            return ApiResponse.success(response);
        } catch (Exception e) {
            return ApiResponse.error("预测失败: " + e.getMessage());
        }
    }

    /**
     * 内部请求类
     */
    public static class SwitchModelRequest {
        private String modelName;

        public String getModelName() {
            return modelName;
        }

        public void setModelName(String modelName) {
            this.modelName = modelName;
        }
    }
}

