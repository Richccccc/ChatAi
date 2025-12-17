# Build stage
FROM maven:3.9.6-eclipse-temurin-17-alpine AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# Run stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip build-base python3-dev
# Install data science libraries (this might be slow on alpine, consider using pre-built wheels or a different base image if too slow, but sticking to alpine for now for consistency)
# Using --break-system-packages for recent alpine python versions
RUN pip3 install --break-system-packages pandas scikit-learn numpy joblib mysql-connector-python sqlalchemy pymysql

COPY --from=build /app/target/*.jar app.jar
# Copy model scripts
COPY model ./model

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
