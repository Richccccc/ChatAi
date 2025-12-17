# Spring Boot 后端项目

## 项目说明

这是一个基于Spring Boot 3.2.0和JDK 17的后端项目，提供用户登录和菜单管理功能。

## 技术栈

- Spring Boot 3.2.0
- Spring Data JPA
- MySQL 8.0+
- JWT (JSON Web Token)
- BCrypt 密码加密
- JDK 17

## 数据库配置

项目使用MySQL数据库，配置信息在 `application.yml` 中：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/over?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=UTF-8&useUnicode=true
    username: root
    password: 123456
```

**注意：** 请确保：
1. MySQL服务已启动
2. 数据库 `over` 已创建
3. 已运行 `database-initializer` 项目初始化数据库表和数据

## 运行步骤

### 1. 初始化数据库

首先运行 `database-initializer` 项目来创建数据库表结构和初始数据：

```bash
cd database-initializer
mvn clean compile exec:java -Dexec.mainClass="com.over.database.DatabaseInitializer"
```

### 2. 启动后端服务

```bash
cd backend
mvn clean install
mvn spring-boot:run
```

或者使用IDE直接运行 `BackendApplication.java`

### 3. 验证服务

服务启动后，访问：
- 后端API地址：http://localhost:8080/api
- 登录接口：POST http://localhost:8080/api/login
- 菜单接口：GET http://localhost:8080/api/get-async-routes

## API接口

### 1. 用户登录

**接口：** `POST /api/login`

**请求体：**
```json
{
  "username": "admin",
  "password": "123456"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "avatar": "https://avatars.githubusercontent.com/u/44761321",
    "username": "admin",
    "nickname": "管理员",
    "roles": ["admin"],
    "permissions": ["*:*:*"],
    "accessToken": "eyJhbGci...",
    "refreshToken": "eyJhbGci...",
    "expires": "2024-12-31T23:59:59.000+00:00"
  }
}
```

### 2. 刷新Token

**接口：** `POST /api/refresh-token`

**请求体：**
```json
{
  "refreshToken": "eyJhbGci..."
}
```

### 3. 获取菜单

**接口：** `GET /api/get-async-routes`

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "path": "/dashboard",
      "name": "可视化大屏",
      "component": "layout",
      "meta": {
        "title": "可视化大屏",
        "icon": "el-icon-data-analysis",
        "rank": 1
      },
      "children": []
    }
  ]
}
```

## 测试账号

- **管理员账号：**
  - 用户名：`admin`
  - 密码：`123456`

- **普通用户：**
  - 用户名：`common`
  - 密码：`123456`

## 注意事项

1. 确保JDK版本为17或更高
2. 确保MySQL版本为8.0或更高
3. 首次运行前必须执行数据库初始化脚本
4. 密码使用BCrypt加密存储，默认测试密码为 `123456`

