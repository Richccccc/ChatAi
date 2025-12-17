package com.over.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.over.dto.ModelInfo;
import com.over.dto.PredictionRequest;
import com.over.dto.PredictionResponse;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

@Service
public class ModelService {

    @Autowired
    private ObjectMapper objectMapper;

    // 当前选中的模型名称
    private final AtomicReference<String> currentModelName = new AtomicReference<>("Random_Forest");
    
    // 模型初始化状态
    private boolean modelsInitialized = false;

    // 可用的模型列表
    private static final String[] MODEL_NAMES = {
        "Random_Forest",
        "Gradient_Boosting",
        "Logistic_Regression"
    };

    private static final String[] MODEL_DISPLAY_NAMES = {
        "随机森林",
        "梯度提升",
        "逻辑回归"
    };

    private static final String[] MODEL_DESCRIPTIONS = {
        "基于随机森林算法的分类模型，适合处理复杂的非线性关系",
        "基于梯度提升算法的集成学习模型，具有较高的预测精度",
        "基于逻辑回归的线性分类模型，速度快且易于解释"
    };

    // 动态获取模型目录，根据工作目录自动调整
    private static String getModelDir() {
        // 优先检查当前目录下的 model/model
        File localModel = new File("model" + File.separator + "model");
        if (localModel.exists()) {
            return "model" + File.separator + "model";
        }
        // 其次检查 backend/model/model
        return "backend" + File.separator + "model" + File.separator + "model";
    }
    
    private static String getPredictScript() {
        // 优先检查当前目录下的 model/predict.py
        File localScript = new File("model" + File.separator + "predict.py");
        if (localScript.exists()) {
            return "model" + File.separator + "predict.py";
        }
        // 其次检查 backend/model/predict.py
        return "backend" + File.separator + "model" + File.separator + "predict.py";
    }

    /**
     * 应用启动时检查模型文件可用性
     */
    @PostConstruct
    public void init() {
        System.out.println("============================================================");
        System.out.println("正在检查模型文件...");
        System.out.println("============================================================");
        
        new Thread(() -> {
            try {
                Thread.sleep(2000); // 等待2秒确保系统就绪
                
                // 打印当前工作目录和模型目录路径，便于调试
                String userDir = System.getProperty("user.dir");
                String modelDir = getModelDir();
                System.out.println(String.format("当前工作目录: %s", userDir));
                System.out.println(String.format("检测到的模型目录路径: %s", modelDir));
                
                File modelDirFile = new File(modelDir);
                File absoluteModelDir = new File(userDir, modelDir);
                System.out.println(String.format("模型目录（相对路径）: %s, 存在: %s", modelDirFile.getAbsolutePath(), modelDirFile.exists()));
                System.out.println(String.format("模型目录（绝对路径）: %s, 存在: %s", absoluteModelDir.getAbsolutePath(), absoluteModelDir.exists()));
                
                boolean allModelsAvailable = true;
                for (String modelName : MODEL_NAMES) {
                    boolean available = isModelAvailable(modelName);
                    String status = available ? "✓ 可用" : "✗ 不可用";
                    if (!available) {
                        // 如果不可用，打印详细的路径信息
                        System.out.println(String.format("  模型 %s: %s", modelName, status));
                        // 使用上面已经定义的 modelDir 变量，不要重复定义
                        File testFile1 = new File(modelDir, modelName + ".pkl");
                        File testFile2 = new File(userDir, modelDir + File.separator + modelName + ".pkl");
                        System.out.println(String.format("    尝试路径1: %s, 存在: %s", testFile1.getAbsolutePath(), testFile1.exists()));
                        System.out.println(String.format("    尝试路径2: %s, 存在: %s", testFile2.getAbsolutePath(), testFile2.exists()));
                    } else {
                        System.out.println(String.format("  模型 %s: %s", modelName, status));
                    }
                    if (!available) {
                        allModelsAvailable = false;
                    }
                }
                
                // 检查预测脚本
                String predictScriptPath = getPredictScript();
                File scriptFile = new File(predictScriptPath);
                if (!scriptFile.exists()) {
                    File absoluteFile = new File(userDir, predictScriptPath);
                    scriptFile = absoluteFile;
                }
                
                if (scriptFile.exists()) {
                    System.out.println(String.format("  预测脚本: ✓ 可用 (%s)", scriptFile.getAbsolutePath()));
                } else {
                    System.out.println(String.format("  预测脚本: ✗ 不可用 (%s)", predictScriptPath));
                    allModelsAvailable = false;
                }
                
                if (allModelsAvailable) {
                    System.out.println("============================================================");
                    System.out.println("所有模型文件检查完成，模型服务已就绪！");
                    System.out.println(String.format("当前默认模型: %s", currentModelName.get()));
                    System.out.println("============================================================");
                } else {
                    System.out.println("============================================================");
                    System.out.println("警告：部分模型文件缺失，请确保模型文件已正确放置！");
                    System.out.println("============================================================");
                }
                
                modelsInitialized = true;
            } catch (Exception e) {
                System.err.println("模型初始化检查失败: " + e.getMessage());
                e.printStackTrace();
            }
        }).start();
    }

    /**
     * 获取所有可用的模型列表
     */
    public List<ModelInfo> getAllModels() {
        List<ModelInfo> models = new ArrayList<>();
        String currentModel = currentModelName.get();

        for (int i = 0; i < MODEL_NAMES.length; i++) {
            String modelName = MODEL_NAMES[i];
            boolean available = isModelAvailable(modelName);
            boolean selected = modelName.equals(currentModel);

            ModelInfo modelInfo = new ModelInfo(
                modelName,
                MODEL_DISPLAY_NAMES[i],
                MODEL_DESCRIPTIONS[i],
                available,
                selected
            );
            models.add(modelInfo);
        }

        return models;
    }

    /**
     * 检查模型文件是否存在
     */
    private boolean isModelAvailable(String modelName) {
        try {
            String fileName = modelName + ".pkl";
            String modelDir = getModelDir();
            String userDir = System.getProperty("user.dir");
            
            // 方式1：尝试相对路径（相对于当前工作目录）
            File modelFile = new File(modelDir, fileName);
            if (modelFile.exists()) {
                return true;
            }
            
            // 方式2：尝试绝对路径（基于工作目录）
            File absoluteFile = new File(userDir, modelDir + File.separator + fileName);
            if (absoluteFile.exists()) {
                return true;
            }
            
            return false;
        } catch (Exception e) {
            System.err.println("检查模型文件时出错: " + modelName + ", 错误: " + e.getMessage());
            return false;
        }
    }

    /**
     * 切换当前使用的模型
     */
    public boolean switchModel(String modelName) {
        if (!isModelAvailable(modelName)) {
            return false;
        }

        // 验证模型名称是否在可用列表中
        boolean isValid = false;
        for (String name : MODEL_NAMES) {
            if (name.equals(modelName)) {
                isValid = true;
                break;
            }
        }

        if (isValid) {
            currentModelName.set(modelName);
            return true;
        }

        return false;
    }

    /**
     * 获取当前选中的模型
     */
    public String getCurrentModel() {
        return currentModelName.get();
    }

    /**
     * 使用当前模型进行预测
     */
    public PredictionResponse predict(PredictionRequest request) throws Exception {
        // 确定使用的模型：优先使用请求中指定的，否则使用当前选中的
        String modelToUse = request.getModelName();
        if (modelToUse == null || modelToUse.trim().isEmpty()) {
            modelToUse = currentModelName.get();
        }

        // 验证模型是否可用
        if (!isModelAvailable(modelToUse)) {
            throw new Exception("模型不可用: " + modelToUse);
        }

        // 准备输入数据
        String jsonData = objectMapper.writeValueAsString(request);

        // 调用Python脚本进行预测
        String result = executePythonPrediction(modelToUse, jsonData);

        // 解析结果
        try {
            var resultMap = objectMapper.readValue(result, java.util.Map.class);
            
            if (Boolean.FALSE.equals(resultMap.get("success"))) {
                throw new Exception((String) resultMap.get("error"));
            }

            PredictionResponse response = new PredictionResponse();
            response.setModelName((String) resultMap.get("model_name"));
            response.setPrediction((Integer) resultMap.get("prediction"));
            response.setPredictionLabel((String) resultMap.get("prediction_label"));
            response.setProbability(((Number) resultMap.get("probability")).doubleValue());
            response.setProbabilityPercent((String) resultMap.get("probability_percent"));
            response.setRiskScore((Integer) resultMap.get("risk_score"));
            response.setRiskLevel((String) resultMap.get("risk_level"));

            return response;
        } catch (Exception e) {
            throw new Exception("解析预测结果失败: " + e.getMessage() + ", 原始结果: " + result);
        }
    }

    /**
     * 执行Python预测脚本
     */
    private String executePythonPrediction(String modelName, String jsonData) throws Exception {
        StringBuilder output = new StringBuilder();

        try {
            // 查找Python脚本
            String predictScriptPath = getPredictScript();
            File scriptFile = new File(predictScriptPath);
            if (!scriptFile.exists()) {
                File absoluteFile = new File(System.getProperty("user.dir"), predictScriptPath);
                if (!absoluteFile.exists()) {
                    throw new Exception("预测脚本不存在: " + predictScriptPath);
                }
                scriptFile = absoluteFile;
            }

            // 构建命令：python predict.py <model_name>
            ProcessBuilder processBuilder = new ProcessBuilder(
                "python",
                scriptFile.getAbsolutePath(),
                modelName
            );
            processBuilder.redirectErrorStream(true);
            processBuilder.environment().put("PYTHONIOENCODING", "utf-8");

            Process process = processBuilder.start();

            // 通过stdin写入JSON数据
            try (java.io.OutputStreamWriter writer = new java.io.OutputStreamWriter(
                process.getOutputStream(), "UTF-8")) {
                writer.write(jsonData);
                writer.flush();
            }

            // 读取输出
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), "UTF-8")
            );
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new Exception("Python脚本执行失败，退出码: " + exitCode + ", 输出: " + output.toString());
            }

        } catch (IOException | InterruptedException e) {
            throw new Exception("执行Python脚本失败: " + e.getMessage());
        }

        return output.toString();
    }
}

