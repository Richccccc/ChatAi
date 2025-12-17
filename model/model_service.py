#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
职位虚假检测模型服务
启动时加载模型到内存，通过HTTP API提供预测服务
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
from pathlib import Path
import threading

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 模型目录
MODEL_DIR = Path(__file__).parent / "model"

# 全局变量存储已加载的模型
loaded_models = {}
current_model_name = "Random_Forest"
artifacts = {}

def load_model(model_name):
    """加载指定的模型到内存"""
    model_path = MODEL_DIR / f"{model_name}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    print(f"正在加载模型: {model_name}...")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print(f"模型 {model_name} 加载完成")
    return model

def load_preprocessing_artifacts():
    """加载预处理所需的文件"""
    print("正在加载预处理工具...")
    artifacts_dict = {}
    
    # 加载标准化器（逻辑回归需要）
    scaler_path = MODEL_DIR / "Logistic_Regression_scaler.pkl"
    if scaler_path.exists():
        with open(scaler_path, 'rb') as f:
            artifacts_dict['scaler'] = pickle.load(f)
        print("  标准化器加载完成")
    
    # 加载标签编码器
    encoders_path = MODEL_DIR / "label_encoders.pkl"
    if encoders_path.exists():
        with open(encoders_path, 'rb') as f:
            artifacts_dict['encoders'] = pickle.load(f)
        print("  标签编码器加载完成")
    
    # 加载特征统计信息
    stats_path = MODEL_DIR / "feature_stats.pkl"
    if stats_path.exists():
        with open(stats_path, 'rb') as f:
            artifacts_dict['stats'] = pickle.load(f)
        print("  特征统计信息加载完成")
    
    return artifacts_dict

def preprocess_features(job_data, artifacts_dict):
    """预处理特征，与训练时保持一致"""
    features = []
    
    # 文本长度特征
    features.append(len(str(job_data.get('title', ''))))
    features.append(len(str(job_data.get('description', ''))))
    features.append(len(str(job_data.get('requirements', ''))))
    features.append(len(str(job_data.get('companyProfile', ''))))
    
    # 数值特征
    features.append(job_data.get('telecommuting', 0))
    features.append(job_data.get('hasCompanyLogo', 0))
    features.append(job_data.get('hasQuestions', 0))
    
    # 是否有薪资范围
    salary_range = job_data.get('salaryRange') or job_data.get('salary_range', '')
    features.append(1 if salary_range and str(salary_range).strip() else 0)
    
    # 使用标签编码器编码分类特征
    encoders = artifacts_dict.get('encoders', {})
    
    # 编码各种分类字段
    field_mapping = {
        'employmentType': 'employment_type',
        'requiredExperience': 'required_experience',
        'requiredEducation': 'required_education',
        'industry': 'industry',
        'function': 'function'
    }
    
    for java_field, python_field in field_mapping.items():
        value = str(job_data.get(java_field, job_data.get(python_field, 'Unknown')))
        if python_field in encoders:
            try:
                encoded = encoders[python_field].transform([value])[0]
            except:
                encoded = 0  # 默认值
        else:
            encoded = 0
        features.append(encoded)
    
    return features

def predict_job(job_data, model_name=None):
    """使用指定模型进行预测"""
    global loaded_models, current_model_name, artifacts
    
    # 使用指定的模型或当前默认模型
    use_model_name = model_name or current_model_name
    
    if use_model_name not in loaded_models:
        # 如果模型未加载，加载它
        loaded_models[use_model_name] = load_model(use_model_name)
    
    model = loaded_models[use_model_name]
    
    # 预处理特征
    features = preprocess_features(job_data, artifacts)
    
    # 如果是逻辑回归，需要标准化
    if use_model_name == "Logistic_Regression" and 'scaler' in artifacts:
        features = artifacts['scaler'].transform([features])[0]
    else:
        features = [features]
    
    # 预测
    prediction = model.predict(features)[0]
    
    # 获取预测概率
    if hasattr(model, 'predict_proba'):
        probability = model.predict_proba(features)[0][1]  # 虚假职位的概率
    else:
        probability = float(prediction)
    
    # 计算风险评分（0-7）
    risk_score = int(probability * 7)
    
    # 确定风险等级
    if probability < 0.3:
        risk_level = "低风险"
    elif probability < 0.7:
        risk_level = "中风险"
    else:
        risk_level = "高风险"
    
    return {
        "success": True,
        "model_name": use_model_name,
        "prediction": int(prediction),
        "prediction_label": "虚假职位" if prediction == 1 else "真实职位",
        "probability": round(probability, 4),
        "probability_percent": f"{probability * 100:.2f}%",
        "risk_score": risk_score,
        "risk_level": risk_level
    }

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "model_loaded": len(loaded_models) > 0,
        "current_model": current_model_name
    })

@app.route('/predict', methods=['POST'])
def predict():
    """单个职位预测"""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "请求体为空"}), 400
        
        # 获取模型名称（可选）
        model_name = data.pop('modelName', None)
        
        result = predict_job(data, model_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/switch', methods=['POST'])
def switch_model():
    """切换当前使用的模型"""
    global current_model_name, loaded_models
    
    try:
        data = request.json
        model_name = data.get('modelName')
        
        if not model_name:
            return jsonify({"success": False, "error": "缺少模型名称"}), 400
        
        # 检查模型是否存在
        model_path = MODEL_DIR / f"{model_name}.pkl"
        if not model_path.exists():
            return jsonify({"success": False, "error": f"模型不存在: {model_name}"}), 404
        
        # 如果模型未加载，加载它
        if model_name not in loaded_models:
            loaded_models[model_name] = load_model(model_name)
        
        current_model_name = model_name
        return jsonify({"success": True, "message": f"已切换到模型: {model_name}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def initialize_models():
    """初始化：加载默认模型和预处理工具"""
    global loaded_models, artifacts, current_model_name
    
    print("============================================================")
    print("启动职位虚假检测模型服务")
    print("============================================================")
    
    try:
        # 加载预处理工具
        artifacts = load_preprocessing_artifacts()
        
        # 加载默认模型
        if current_model_name:
            loaded_models[current_model_name] = load_model(current_model_name)
        
        print("============================================================")
        print(f"模型服务启动成功！默认模型: {current_model_name}")
        print("API接口:")
        print("  GET  /health     - 健康检查")
        print("  POST /predict    - 单个职位预测")
        print("  POST /switch     - 切换模型")
        print("服务地址: http://localhost:5000")
        print("============================================================")
    except Exception as e:
        print(f"模型初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 初始化模型
    initialize_models()
    
    # 启动Flask服务
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

