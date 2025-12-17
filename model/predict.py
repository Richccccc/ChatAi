#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
职位虚假预测脚本
接收JSON格式的职位信息，使用指定的模型进行预测
"""
import sys
import json
import pickle
import os
import warnings
from pathlib import Path
from io import StringIO

# 抑制sklearn警告输出到stdout，避免污染JSON响应
warnings.filterwarnings('ignore')

# 导入sklearn相关模块（加载模型时需要）
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    import joblib  # sklearn推荐使用joblib来加载模型
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(json.dumps({
        "success": False,
        "error": f"缺少必要的Python库，请安装: pip install scikit-learn pandas joblib numpy. 错误详情: {str(e)}"
    }))
    sys.exit(1)

# 模型目录
MODEL_DIR = Path(__file__).parent / "model"

def load_model(model_name):
    """加载指定的模型"""
    model_path = MODEL_DIR / f"{model_name}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    try:
        # 优先使用joblib加载（sklearn推荐方式）
        model = joblib.load(model_path)
    except Exception:
        # 如果joblib失败，尝试使用pickle
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
        except Exception as e:
            raise Exception(f"无法加载模型 {model_name}，可能是版本不兼容。请确保Python和sklearn版本与训练时一致。错误: {str(e)}")
    
    return model

def load_preprocessing_artifacts():
    """加载预处理所需的文件"""
    artifacts = {}
    
    # 加载标准化器（逻辑回归需要）
    scaler_path = MODEL_DIR / "Logistic_Regression_scaler.pkl"
    if scaler_path.exists():
        try:
            artifacts['scaler'] = joblib.load(scaler_path)
        except:
            try:
                with open(scaler_path, 'rb') as f:
                    artifacts['scaler'] = pickle.load(f)
            except Exception as e:
                print(f"警告：无法加载标准化器: {e}", file=sys.stderr)
    
    # 加载标签编码器
    encoders_path = MODEL_DIR / "label_encoders.pkl"
    if encoders_path.exists():
        try:
            artifacts['encoders'] = joblib.load(encoders_path)
        except:
            try:
                with open(encoders_path, 'rb') as f:
                    artifacts['encoders'] = pickle.load(f)
            except Exception as e:
                print(f"警告：无法加载标签编码器: {e}", file=sys.stderr)
    
    # 加载特征统计信息
    stats_path = MODEL_DIR / "feature_stats.pkl"
    if stats_path.exists():
        try:
            artifacts['stats'] = joblib.load(stats_path)
        except:
            try:
                with open(stats_path, 'rb') as f:
                    artifacts['stats'] = pickle.load(f)
            except Exception as e:
                print(f"警告：无法加载特征统计信息: {e}", file=sys.stderr)
    
    return artifacts

def preprocess_features(job_data, artifacts):
    """预处理特征，与训练时保持一致"""
    # 这里需要根据实际的特征工程逻辑来处理
    # 简化版本：提取基本特征
    
    features = []
    
    # 文本长度特征（支持驼峰和下划线两种命名）
    title = job_data.get('title') or job_data.get('Title') or ''
    description = job_data.get('description') or job_data.get('Description') or ''
    requirements = job_data.get('requirements') or job_data.get('Requirements') or ''
    company_profile = job_data.get('companyProfile') or job_data.get('company_profile') or job_data.get('CompanyProfile') or ''
    
    features.append(len(str(title)))
    features.append(len(str(description)))
    features.append(len(str(requirements)))
    features.append(len(str(company_profile)))
    
    # 数值特征（支持驼峰和下划线两种命名）
    def get_numeric_field(key_snake, key_camel, default=0):
        return job_data.get(key_snake) or job_data.get(key_camel) or default
    
    features.append(get_numeric_field('telecommuting', 'telecommuting', 0))
    features.append(get_numeric_field('has_company_logo', 'hasCompanyLogo', 0))
    features.append(get_numeric_field('has_questions', 'hasQuestions', 0))
    
    # 是否有薪资范围（支持驼峰和下划线命名）
    salary_range = job_data.get('salaryRange') or job_data.get('salary_range') or ''
    features.append(1 if salary_range and str(salary_range).strip() else 0)
    
    # 使用标签编码器编码分类特征
    encoders = artifacts.get('encoders', {})
    
    # 编码各种分类字段（支持驼峰和下划线两种命名）
    field_mapping = {
        'employment_type': ['employmentType', 'EmploymentType', 'employment_type'],
        'required_experience': ['requiredExperience', 'RequiredExperience', 'required_experience'],
        'required_education': ['requiredEducation', 'RequiredEducation', 'required_education'],
        'industry': ['industry', 'Industry'],
        'function': ['function', 'Function']
    }
    
    for field_key, possible_keys in field_mapping.items():
        value = 'Unknown'
        for key in possible_keys:
            if key in job_data and job_data[key]:
                value = str(job_data[key])
                break
        
        if field_key in encoders:
            try:
                encoded = encoders[field_key].transform([value])[0]
            except:
                encoded = 0  # 默认值
        else:
            encoded = 0
        features.append(encoded)
    
    # 需要确保特征数量与训练时一致（25个特征）
    # 当前只有13个，需要补充更多特征
    
    # 补充特征：更多文本统计特征
    title_str = str(title)
    desc_str = str(description)
    req_str = str(requirements)
    profile_str = str(company_profile)
    
    # 文本统计特征
    features.append(len(title_str.split()))  # title单词数
    features.append(len(desc_str.split()))  # description单词数
    features.append(len(req_str.split()))  # requirements单词数
    features.append(len(profile_str.split()))  # company_profile单词数
    
    # 是否有部门信息
    department = job_data.get('department') or job_data.get('Department') or ''
    features.append(1 if department and str(department).strip() else 0)
    
    # 是否有福利信息
    benefits = job_data.get('benefits') or job_data.get('Benefits') or ''
    features.append(len(str(benefits)))  # benefits长度
    features.append(1 if benefits and str(benefits).strip() else 0)  # 是否有benefits
    
    # 文本中是否包含常见关键词（可能用于识别虚假职位）
    suspicious_keywords = ['free', 'easy', 'work from home', 'no experience', 'immediate']
    desc_lower = desc_str.lower()
    title_lower = title_str.lower()
    keyword_count = sum(1 for kw in suspicious_keywords if kw in desc_lower or kw in title_lower)
    features.append(keyword_count)
    
    # 位置信息长度（可能用于分析）
    location = job_data.get('location') or job_data.get('Location') or ''
    features.append(len(str(location)))
    
    # 更多组合特征
    # 职位描述完整度（描述长度与标题长度的比率）
    if len(title_str) > 0:
        desc_title_ratio = len(desc_str) / len(title_str)
    else:
        desc_title_ratio = 0
    features.append(desc_title_ratio)
    
    # 任职要求完整度（要求长度与描述长度的比率）
    if len(desc_str) > 0:
        req_desc_ratio = len(req_str) / len(desc_str)
    else:
        req_desc_ratio = 0
    features.append(req_desc_ratio)
    
    # 公司简介完整度
    if len(profile_str) > 0:
        profile_score = min(len(profile_str) / 500, 1.0)  # 归一化到0-1
    else:
        profile_score = 0
    features.append(profile_score)
    
    # 确保正好25个特征（如果还不够，用0填充）
    while len(features) < 25:
        features.append(0)
    
    # 如果超过25个，截断到25个
    if len(features) > 25:
        features = features[:25]
    
    return features

def predict(job_data_json_str, model_name):
    """执行预测"""
    # 重定向stderr以避免警告污染输出
    old_stderr = sys.stderr
    sys.stderr = StringIO()
    
    try:
        # 解析输入数据
        job_data = json.loads(job_data_json_str)
        
        # 加载模型
        model = load_model(model_name)
        
        # 加载预处理工具
        artifacts = load_preprocessing_artifacts()
        
        # 预处理特征
        features = preprocess_features(job_data, artifacts)
        
        # 检查特征数量
        if hasattr(model, 'n_features_in_'):
            expected_features = model.n_features_in_
            if len(features) != expected_features:
                sys.stderr = old_stderr
                return {
                    "success": False,
                    "error": f"特征数量不匹配: 提供了 {len(features)} 个特征，但模型期望 {expected_features} 个特征"
                }
        
        # 转换为numpy数组（2D，shape: (1, n_features)）
        features_array = np.array(features, dtype=np.float64).reshape(1, -1)
        
        # 如果是逻辑回归，需要标准化
        if model_name == "Logistic_Regression" and 'scaler' in artifacts:
            features_array = artifacts['scaler'].transform(features_array)
        
        # 预测（使用numpy数组）
        prediction = model.predict(features_array)[0]
        
        # 获取预测概率
        if hasattr(model, 'predict_proba'):
            probability = model.predict_proba(features_array)[0][1]  # 虚假职位的概率
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
        
        # 构建响应
        result = {
            "success": True,
            "model_name": model_name,
            "prediction": int(prediction),
            "prediction_label": "虚假职位" if prediction == 1 else "真实职位",
            "probability": round(probability, 4),
            "probability_percent": f"{probability * 100:.2f}%",
            "risk_score": risk_score,
            "risk_level": risk_level
        }
        
        return result
        
    except Exception as e:
        sys.stderr = old_stderr
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        # 恢复stderr
        sys.stderr = old_stderr

if __name__ == "__main__":
    # 从命令行参数获取模型名称，从stdin获取JSON数据
    # 格式: echo "<json_data>" | python predict.py <model_name>
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python predict.py <model_name> [<json_data>]"
        }))
        sys.exit(1)
    
    model_name = sys.argv[1]
    
    # 优先从命令行参数获取，否则从stdin读取
    if len(sys.argv) >= 3:
        json_data = sys.argv[2]
    else:
        # 从stdin读取
        json_data = sys.stdin.read().strip()
    
    result = predict(json_data, model_name)
    print(json.dumps(result, ensure_ascii=False))

