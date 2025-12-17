import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# 设置中文字体，防止乱码
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 配置
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fake_job_postings.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis_results')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_data():
    try:
        print(f"Loading data from {DATA_PATH}...")
        df = pd.read_csv(DATA_PATH)
        # 简单清洗
        df.fillna('Unknown', inplace=True)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def save_plot(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Saved {filename}")

def analysis_1_fraud_distribution(df):
    plt.figure(figsize=(10, 6))
    counts = df['fraudulent'].value_counts()
    plt.pie(counts, labels=['真实职位', '虚假职位'], autopct='%1.1f%%', colors=['#66b3ff', '#ff9999'])
    plt.title('(1) 真假职位分布分析')
    save_plot('analysis_1_fraud_distribution.png')

def analysis_2_location_distribution(df):
    plt.figure(figsize=(12, 6))
    top_locations = df['location'].value_counts().head(10)
    sns.barplot(x=top_locations.values, y=top_locations.index, palette='viridis')
    plt.title('(2) 职位地理位置分布分析 (Top 10)')
    plt.xlabel('职位数量')
    save_plot('analysis_2_location_distribution.png')

def analysis_3_company_size_fraud(df):
    plt.figure(figsize=(12, 6))
    # 过滤掉Unknown
    data = df[df['company_profile'] != 'Unknown']
    # 这里用是否包含logo作为规模的一个简单代理，或者如果有company_profile长度
    # 由于原始csv没有明确company_size列，我们用has_company_logo来分析
    sns.countplot(x='has_company_logo', hue='fraudulent', data=df)
    plt.title('(3) 公司Logo与真实性关联分析')
    plt.xticks([0, 1], ['无Logo', '有Logo'])
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_3_company_size_fraud.png')

def analysis_4_salary_anomaly(df):
    # 提取薪资范围，这里做简单处理，只分析是否有薪资范围
    df['has_salary'] = df['salary_range'] != 'Unknown'
    plt.figure(figsize=(10, 6))
    sns.countplot(x='has_salary', hue='fraudulent', data=df)
    plt.title('(4) 薪资范围标注与真实性分析')
    plt.xticks([0, 1], ['未标注薪资', '已标注薪资'])
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_4_salary_anomaly.png')

def analysis_5_title_features(df):
    # 简单分析标题长度
    df['title_len'] = df['title'].apply(len)
    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x='title_len', hue='fraudulent', kde=True, bins=30)
    plt.title('(5) 职位标题长度特征分析')
    save_plot('analysis_5_title_features.png')

def analysis_6_description_complexity(df):
    df['desc_len'] = df['description'].apply(len)
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='fraudulent', y='desc_len', data=df)
    plt.title('(6) 职位描述长度(复杂度)分析')
    plt.xticks([0, 1], ['真实', '虚假'])
    save_plot('analysis_6_description_complexity.png')

def analysis_7_requirements_reasonableness(df):
    # 分析是否有任职要求
    df['has_req'] = df['requirements'] != 'Unknown'
    plt.figure(figsize=(10, 6))
    sns.countplot(x='has_req', hue='fraudulent', data=df)
    plt.title('(7) 任职要求有无与风险分析')
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_7_requirements_reasonableness.png')

def analysis_8_contact_completeness(df):
    # 数据集中没有直接的contact列，假设has_questions代表联系/反馈机制
    plt.figure(figsize=(10, 6))
    sns.countplot(x='has_questions', hue='fraudulent', data=df)
    plt.title('(8) 申请问题(联系机制)完整性分析')
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_8_contact_completeness.png')

def analysis_9_industry_risk(df):
    plt.figure(figsize=(12, 8))
    top_industries = df['industry'].value_counts().head(10).index
    data = df[df['industry'].isin(top_industries)]
    sns.countplot(y='industry', hue='fraudulent', data=data)
    plt.title('(9) 热门行业领域风险分析')
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_9_industry_risk.png')

def analysis_10_post_time_pattern(df):
    # 模拟数据，假设telecommuting代表某种模式
    plt.figure(figsize=(10, 6))
    sns.countplot(x='telecommuting', hue='fraudulent', data=df)
    plt.title('(10) 远程办公(发布模式)分析')
    plt.xticks([0, 1], ['非远程', '远程'])
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_10_post_time_pattern.png')

def analysis_11_benefits_authenticity(df):
    df['has_benefits'] = df['benefits'] != 'Unknown'
    plt.figure(figsize=(10, 6))
    sns.countplot(x='has_benefits', hue='fraudulent', data=df)
    plt.title('(11) 福利待遇描述分析')
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_11_benefits_authenticity.png')

def analysis_12_company_profile_credibility(df):
    df['profile_len'] = df['company_profile'].apply(len)
    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x='profile_len', hue='fraudulent', kde=True, bins=30)
    plt.title('(12) 公司简介可信度(长度)分析')
    save_plot('analysis_12_company_profile_credibility.png')

def analysis_13_application_complexity(df):
    # 用 employment_type 代替申请复杂度维度展示
    plt.figure(figsize=(12, 6))
    sns.countplot(y='employment_type', hue='fraudulent', data=df)
    plt.title('(13) 雇用类型风险分析')
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_13_application_complexity.png')

def analysis_14_multi_feature_risk(df):
    # required_experience 与 fraudulent
    plt.figure(figsize=(12, 6))
    sns.countplot(y='required_experience', hue='fraudulent', data=df)
    plt.title('(14) 所需经验与风险关联分析')
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_14_multi_feature_risk.png')

def analysis_15_time_trend(df):
    # 由于没有具体时间戳，我们用 required_education 代替趋势/类别演变
    plt.figure(figsize=(12, 6))
    sns.countplot(y='required_education', hue='fraudulent', data=df)
    plt.title('(15) 学历要求风险分布分析')
    plt.legend(title='是否虚假', labels=['真实', '虚假'])
    save_plot('analysis_15_time_trend.png')

if __name__ == "__main__":
    df = load_data()
    print("Starting Analysis...")
    
    analysis_1_fraud_distribution(df)
    analysis_2_location_distribution(df)
    analysis_3_company_size_fraud(df)
    analysis_4_salary_anomaly(df)
    analysis_5_title_features(df)
    analysis_6_description_complexity(df)
    analysis_7_requirements_reasonableness(df)
    analysis_8_contact_completeness(df)
    analysis_9_industry_risk(df)
    analysis_10_post_time_pattern(df)
    analysis_11_benefits_authenticity(df)
    analysis_12_company_profile_credibility(df)
    analysis_13_application_complexity(df)
    analysis_14_multi_feature_risk(df)
    analysis_15_time_trend(df)
    
    print("All analysis completed.")

