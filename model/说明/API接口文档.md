# Python模型服务API接口文档

## 基础信息

- **服务地址**: `http://localhost:5000`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON

---

## 接口列表

### 1. 健康检查

检查服务状态和模型是否加载成功。

**请求**
```http
GET /health
```

**响应**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

**字段说明**
- `status`: 服务状态，固定为 "ok"
- `model_loaded`: 模型是否加载成功，true/false

---

### 2. 单个职位预测

预测单个职位是否为虚假职位。

**请求**
```http
POST /predict
Content-Type: application/json
```

**请求体**
```json
{
  "title": "Software Engineer",
  "location": "US, CA, San Francisco",
  "department": "",
  "salary_range": "120000-180000",
  "company_profile": "We are a leading technology company...",
  "description": "We are looking for an experienced engineer...",
  "requirements": "Bachelor degree, 3+ years experience...",
  "benefits": "Health insurance, 401k",
  "telecommuting": 0,
  "has_company_logo": 1,
  "has_questions": 1,
  "employment_type": "Full-time",
  "required_experience": "Mid-Senior level",
  "required_education": "Bachelor's Degree",
  "industry": "Computer Software",
  "function": "Engineering"
}
```

**字段说明**

| 字段名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| title | string | 是 | 职位标题 |
| location | string | 是 | 位置，格式："国家, 州, 城市" |
| department | string | 否 | 部门，可为空字符串 |
| salary_range | string | 是 | 薪资范围，格式："最低-最高" 或 "" |
| company_profile | string | 是 | 公司简介 |
| description | string | 是 | 职位描述 |
| requirements | string | 是 | 任职要求 |
| benefits | string | 否 | 福利待遇，可为空字符串 |
| telecommuting | integer | 是 | 是否远程工作，0=否，1=是 |
| has_company_logo | integer | 是 | 是否有公司logo，0=否，1=是 |
| has_questions | integer | 是 | 是否有申请问题，0=否，1=是 |
| employment_type | string | 是 | 就业类型，如 "Full-time" |
| required_experience | string | 是 | 所需经验，如 "Mid-Senior level" |
| required_education | string | 是 | 所需教育，如 "Bachelor's Degree" |
| industry | string | 是 | 行业，如 "Computer Software" |
| function | string | 是 | 职能，如 "Engineering" |

**成功响应**
```json
{
  "success": true,
  "data": {
    "prediction": 0,
    "prediction_label": "真实职位",
    "probability": 0.15,
    "probability_percent": "15.00%",
    "risk_score": 2,
    "risk_level": "低风险"
  }
}
```

**错误响应**
```json
{
  "success": false,
  "error": "缺少必需字段: title, location"
}
```

**响应字段说明**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 请求是否成功 |
| error | string | 错误信息（仅失败时） |
| data | object | 预测结果（仅成功时） |
| data.prediction | integer | 预测结果，0=真实，1=虚假 |
| data.prediction_label | string | 预测结果标签 |
| data.probability | float | 虚假概率，0-1之间 |
| data.probability_percent | string | 虚假概率百分比 |
| data.risk_score | integer | 风险评分，0-7 |
| data.risk_level | string | 风险等级：低风险/中风险/高风险 |

---

### 3. 批量预测

批量预测多个职位。

**请求**
```http
POST /predict/batch
Content-Type: application/json
```

**请求体**
```json
{
  "jobs": [
    {
      "title": "Software Engineer",
      "location": "US, CA, San Francisco",
      "salary_range": "120000-180000",
      ...
    },
    {
      "title": "Data Scientist",
      "location": "US, NY, New York",
      "salary_range": "150000-200000",
      ...
    }
  ]
}
```

**字段说明**
- `jobs`: 职位数组，每个元素格式同单个预测接口

**成功响应**
```json
{
  "success": true,
  "total": 2,
  "results": [
    {
      "index": 0,
      "success": true,
      "prediction": 0,
      "prediction_label": "真实职位",
      "probability": 0.15,
      "probability_percent": "15.00%",
      "risk_score": 2,
      "risk_level": "低风险"
    },
    {
      "index": 1,
      "success": true,
      "prediction": 1,
      "prediction_label": "虚假职位",
      "probability": 0.85,
      "probability_percent": "85.00%",
      "risk_score": 6,
      "risk_level": "高风险"
    }
  ]
}
```

**部分失败响应**
```json
{
  "success": true,
  "total": 2,
  "results": [
    {
      "index": 0,
      "success": true,
      "prediction": 0,
      ...
    },
    {
      "index": 1,
      "success": false,
      "error": "缺少必需字段: title"
    }
  ]
}
```

**响应字段说明**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 请求是否成功 |
| total | integer | 总职位数 |
| results | array | 预测结果数组 |
| results[].index | integer | 职位在数组中的索引 |
| results[].success | boolean | 该职位预测是否成功 |
| results[].error | string | 错误信息（仅失败时） |
| results[].prediction | integer | 预测结果（仅成功时） |
| ... | ... | 其他字段同单个预测接口 |

---

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

---

## 使用示例

### cURL示例

```bash
# 健康检查
curl http://localhost:5000/health

# 单个预测
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Software Engineer",
    "location": "US, CA, San Francisco",
    "department": "",
    "salary_range": "120000-180000",
    "company_profile": "We are a leading company...",
    "description": "We are looking for...",
    "requirements": "Bachelor degree...",
    "benefits": "Health insurance",
    "telecommuting": 0,
    "has_company_logo": 1,
    "has_questions": 1,
    "employment_type": "Full-time",
    "required_experience": "Mid-Senior level",
    "required_education": "Bachelor'\''s Degree",
    "industry": "Computer Software",
    "function": "Engineering"
  }'
```

### Python示例

```python
import requests

url = "http://localhost:5000/predict"
data = {
    "title": "Software Engineer",
    "location": "US, CA, San Francisco",
    "salary_range": "120000-180000",
    "company_profile": "We are a leading company...",
    "description": "We are looking for...",
    "requirements": "Bachelor degree...",
    "benefits": "Health insurance",
    "telecommuting": 0,
    "has_company_logo": 1,
    "has_questions": 1,
    "employment_type": "Full-time",
    "required_experience": "Mid-Senior level",
    "required_education": "Bachelor's Degree",
    "industry": "Computer Software",
    "function": "Engineering"
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### JavaScript示例

```javascript
fetch('http://localhost:5000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Software Engineer',
    location: 'US, CA, San Francisco',
    salary_range: '120000-180000',
    company_profile: 'We are a leading company...',
    description: 'We are looking for...',
    requirements: 'Bachelor degree...',
    benefits: 'Health insurance',
    telecommuting: 0,
    has_company_logo: 1,
    has_questions: 1,
    employment_type: 'Full-time',
    required_experience: 'Mid-Senior level',
    required_education: "Bachelor's Degree",
    industry: 'Computer Software',
    function: 'Engineering'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 注意事项

1. 所有时间字段使用ISO 8601格式
2. 布尔字段使用整数：0表示否，1表示是
3. 字符串字段不能为null，空值使用空字符串""
4. 请求体必须是有效的JSON格式
5. Content-Type必须设置为application/json

