import pandas as pd
from sqlalchemy import create_engine, text, types
import os
import sys

# 配置
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fake_job_postings.csv')
DB_URL = "mysql+pymysql://root:123456@localhost:3306/over?charset=utf8mb4"

def import_data():
    try:
        print(f"Loading data from {DATA_PATH}...")
        df = pd.read_csv(DATA_PATH)
        
        # 简单清洗
        df.fillna('Unknown', inplace=True)
        
        # 创建数据库连接
        engine = create_engine(DB_URL)
        
        print("Importing to MySQL...")
        # 将数据写入 job_postings 表，如果存在则替换
        # chunksize 设置为 1000 以避免一次性写入过多数据导致的问题
        df.to_sql('job_postings', con=engine, if_exists='replace', index=False, chunksize=1000, dtype={
            'job_id': types.Integer,
            'description': types.Text,
            'company_profile': types.Text,
            'requirements': types.Text,
            'benefits': types.Text
        })
        
        # 设置 job_id 为主键
        with engine.connect() as con:
            try:
                con.execute(text("ALTER TABLE job_postings ADD PRIMARY KEY (job_id)"))
            except Exception as e:
                print(f"Warning setting primary key: {e}")
            
        print("Data import completed successfully!")
        
    except Exception as e:
        print(f"Error importing data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import_data()
