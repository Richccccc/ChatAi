import pandas as pd
import json
import sys
from sqlalchemy import create_engine
import os

# 配置
import re

def get_db_connection_url():
    # 尝试从环境变量获取
    db_url_env = os.environ.get("DB_URL")
    db_user = os.environ.get("DB_USERNAME", "root")
    db_pass = os.environ.get("DB_PASSWORD", "123456")
    
    # 默认值 (本地开发)
    host = "localhost"
    port = "3306"
    database = "over"
    
    if db_url_env:
        # 解析 JDBC URL
        # 格式: jdbc:mysql://host:port/database?params
        match = re.search(r"jdbc:mysql://([^:/]+):(\d+)/([^?]+)", db_url_env)
        if match:
            host = match.group(1)
            port = match.group(2)
            database = match.group(3)
    
    # 构建 SQLAlchemy URL
    # 格式: mysql+pymysql://user:password@host:port/database
    # TiDB Cloud 需要 SSL 连接。在 Alpine 容器中，系统 CA 证书通常位于 /etc/ssl/certs/ca-certificates.crt
    ssl_params = "?charset=utf8mb4&ssl_ca=/etc/ssl/certs/ca-certificates.crt&ssl_verify_cert=true"
    return f"mysql+pymysql://{db_user}:{db_pass}@{host}:{port}/{database}{ssl_params}"

def get_data_from_db():
    try:
        url = get_db_connection_url()
        # print(f"Connecting to DB: {url.split('@')[1]}") 
        engine = create_engine(url)
        query = "SELECT * FROM job_postings"
        df = pd.read_sql(query, engine)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

def analyze():
    df, error = get_data_from_db()
    results = {}

    if error:
        print(json.dumps({"error": f"Database connection failed: {error}"}))
        return

    if df.empty:
        print(json.dumps({"error": "No data found in database"}))
        return

    # 1. 真假职位分布
    counts = df['fraudulent'].value_counts()
    results['fraud_distribution'] = {
        'labels': ['真实职位', '虚假职位'],
        'values': [int(counts.get(0, 0)), int(counts.get(1, 0))]
    }

    # 2. 职位地理位置分布 (Top 10)
    top_locations = df['location'].value_counts().head(10)
    results['location_distribution'] = {
        'labels': top_locations.index.tolist(),
        'values': top_locations.values.tolist()
    }

    # 3. 公司规模(Logo)与真实性
    # 统计有Logo和无Logo中虚假职位的比例
    # 分组统计：logo -> fraudulent -> count
    # 0: 无logo, 1: 有logo
    # fraudulent: 0: 真实, 1: 虚假
    logo_stats = df.groupby(['has_company_logo', 'fraudulent']).size().unstack(fill_value=0)
    # logo_stats 结构:
    # fraudulent      0      1
    # has_company_logo
    # 0             100    20
    # 1             500    10
    results['company_logo_risk'] = {
        'categories': ['无Logo', '有Logo'],
        'real': [int(logo_stats.loc[0, 0] if 0 in logo_stats.index else 0), int(logo_stats.loc[1, 0] if 1 in logo_stats.index else 0)],
        'fake': [int(logo_stats.loc[0, 1] if 0 in logo_stats.index else 0), int(logo_stats.loc[1, 1] if 1 in logo_stats.index else 0)]
    }

    # 4. 薪资范围异常检测
    df['has_salary'] = df['salary_range'].apply(lambda x: 0 if x == 'Unknown' or pd.isna(x) else 1)
    salary_stats = df.groupby(['has_salary', 'fraudulent']).size().unstack(fill_value=0)
    results['salary_anomaly'] = {
        'categories': ['未标注薪资', '已标注薪资'],
        'real': [int(salary_stats.loc[0, 0] if 0 in salary_stats.index else 0), int(salary_stats.loc[1, 0] if 1 in salary_stats.index else 0)],
        'fake': [int(salary_stats.loc[0, 1] if 0 in salary_stats.index else 0), int(salary_stats.loc[1, 1] if 1 in salary_stats.index else 0)]
    }

    # 5. 职位标题长度特征
    # 简单起见，返回平均长度
    df['title_len'] = df['title'].apply(lambda x: len(str(x)))
    avg_len = df.groupby('fraudulent')['title_len'].mean()
    results['title_length'] = {
        'labels': ['真实职位', '虚假职位'],
        'values': [float(avg_len.get(0, 0)), float(avg_len.get(1, 0))]
    }

    # 6. 职位描述复杂度 (平均长度)
    df['desc_len'] = df['description'].apply(lambda x: len(str(x)))
    avg_desc_len = df.groupby('fraudulent')['desc_len'].mean()
    results['description_complexity'] = {
        'labels': ['真实职位', '虚假职位'],
        'values': [float(avg_desc_len.get(0, 0)), float(avg_desc_len.get(1, 0))]
    }

    # 7. 任职要求合理性 (有无要求)
    df['has_req'] = df['requirements'].apply(lambda x: 0 if x == 'Unknown' or pd.isna(x) else 1)
    req_stats = df.groupby(['has_req', 'fraudulent']).size().unstack(fill_value=0)
    results['requirements_risk'] = {
        'categories': ['无任职要求', '有任职要求'],
        'real': [int(req_stats.loc[0, 0] if 0 in req_stats.index else 0), int(req_stats.loc[1, 0] if 1 in req_stats.index else 0)],
        'fake': [int(req_stats.loc[0, 1] if 0 in req_stats.index else 0), int(req_stats.loc[1, 1] if 1 in req_stats.index else 0)]
    }

    # 8. 联系方式完整性 (has_questions)
    q_stats = df.groupby(['has_questions', 'fraudulent']).size().unstack(fill_value=0)
    results['contact_completeness'] = {
        'categories': ['无筛选问题', '有筛选问题'],
        'real': [int(q_stats.loc[0, 0] if 0 in q_stats.index else 0), int(q_stats.loc[1, 0] if 1 in q_stats.index else 0)],
        'fake': [int(q_stats.loc[0, 1] if 0 in q_stats.index else 0), int(q_stats.loc[1, 1] if 1 in q_stats.index else 0)]
    }

    # 9. 行业领域风险 (Top 10)
    top_industries = df['industry'].value_counts().head(10).index
    ind_data = df[df['industry'].isin(top_industries)]
    ind_stats = ind_data.groupby(['industry', 'fraudulent']).size().unstack(fill_value=0)
    # 填充缺失列
    if 0 not in ind_stats.columns: ind_stats[0] = 0
    if 1 not in ind_stats.columns: ind_stats[1] = 0
    
    results['industry_risk'] = {
        'categories': ind_stats.index.tolist(),
        'real': ind_stats[0].tolist(),
        'fake': ind_stats[1].tolist()
    }

    # 10. 发布时间模式 (这里用telecommuting代替，原需求)
    tele_stats = df.groupby(['telecommuting', 'fraudulent']).size().unstack(fill_value=0)
    results['telecommuting_risk'] = {
        'categories': ['非远程', '远程'],
        'real': [int(tele_stats.loc[0, 0] if 0 in tele_stats.index else 0), int(tele_stats.loc[1, 0] if 1 in tele_stats.index else 0)],
        'fake': [int(tele_stats.loc[0, 1] if 0 in tele_stats.index else 0), int(tele_stats.loc[1, 1] if 1 in tele_stats.index else 0)]
    }

    # 11. 福利待遇真实性
    df['has_benefits'] = df['benefits'].apply(lambda x: 0 if x == 'Unknown' or pd.isna(x) else 1)
    ben_stats = df.groupby(['has_benefits', 'fraudulent']).size().unstack(fill_value=0)
    results['benefits_risk'] = {
        'categories': ['无福利', '有福利'],
        'real': [int(ben_stats.loc[0, 0] if 0 in ben_stats.index else 0), int(ben_stats.loc[1, 0] if 1 in ben_stats.index else 0)],
        'fake': [int(ben_stats.loc[0, 1] if 0 in ben_stats.index else 0), int(ben_stats.loc[1, 1] if 1 in ben_stats.index else 0)]
    }

    # 12. 公司简介可信度 (平均长度)
    df['profile_len'] = df['company_profile'].apply(lambda x: len(str(x)))
    avg_profile_len = df.groupby('fraudulent')['profile_len'].mean()
    results['profile_credibility'] = {
        'labels': ['真实职位', '虚假职位'],
        'values': [float(avg_profile_len.get(0, 0)), float(avg_profile_len.get(1, 0))]
    }

    # 13. 申请流程复杂度 (Employment Type)
    emp_stats = df.groupby(['employment_type', 'fraudulent']).size().unstack(fill_value=0)
    # 填充
    if 0 not in emp_stats.columns: emp_stats[0] = 0
    if 1 not in emp_stats.columns: emp_stats[1] = 0
    results['employment_type_risk'] = {
        'categories': emp_stats.index.tolist(),
        'real': emp_stats[0].tolist(),
        'fake': emp_stats[1].tolist()
    }

    # 14. 多特征组合 (Required Experience)
    exp_stats = df.groupby(['required_experience', 'fraudulent']).size().unstack(fill_value=0)
    if 0 not in exp_stats.columns: exp_stats[0] = 0
    if 1 not in exp_stats.columns: exp_stats[1] = 0
    results['experience_risk'] = {
        'categories': exp_stats.index.tolist(),
        'real': exp_stats[0].tolist(),
        'fake': exp_stats[1].tolist()
    }

    # 15. 时间趋势 (Required Education)
    edu_stats = df.groupby(['required_education', 'fraudulent']).size().unstack(fill_value=0)
    if 0 not in edu_stats.columns: edu_stats[0] = 0
    if 1 not in edu_stats.columns: edu_stats[1] = 0
    results['education_risk'] = {
        'categories': edu_stats.index.tolist(),
        'real': edu_stats[0].tolist(),
        'fake': edu_stats[1].tolist()
    }

    print(json.dumps(results, ensure_ascii=False))

if __name__ == "__main__":
    analyze()

