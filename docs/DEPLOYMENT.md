# Deployment Guide

## 🚀 Deployment Overview

This guide covers deploying the Equity Research Dashboard to various environments, from development to production. The modern implementation (v2) is designed for easy deployment with modern DevOps practices.

## 🏗️ Architecture Overview

### **Frontend (React TypeScript)**
- **Build**: Vite for fast builds and development
- **Hosting**: Static files served from CDN
- **Domain**: `https://dashboard.equity-research.com`

### **Backend (RESTful API)**
- **Runtime**: Node.js with Express/FastAPI
- **Hosting**: Cloud platform (AWS, GCP, Azure)
- **Domain**: `https://api.equity-research.com`

### **Database**
- **Primary**: PostgreSQL for production data
- **Cache**: Redis for session and data caching
- **Files**: S3-compatible storage for reports and assets

## 🛠️ Prerequisites

### **Development Environment**
- **Node.js**: 18+ (LTS recommended)
- **npm**: 9+ or **yarn**: 1.22+
- **Git**: Latest version
- **Docker**: 20+ (optional, for containerized deployment)

### **Production Environment**
- **Cloud Platform**: AWS, GCP, or Azure
- **Domain**: Custom domain with SSL certificate
- **CI/CD**: GitHub Actions, GitLab CI, or similar
- **Monitoring**: Application and infrastructure monitoring

## 🏠 Local Development

### **Frontend Development**

```bash
# Navigate to the modern implementation
cd v2-modern

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### **Backend Development**

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5000
```

### **Full Stack Development**

```bash
# Start both frontend and backend
npm run dev:full

# Or use Docker Compose
docker-compose up -d
```

## 🐳 Docker Deployment

### **Frontend Dockerfile**

```dockerfile
# v2-modern/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### **Backend Dockerfile**

```dockerfile
# backend/Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 5000
CMD ["npm", "start"]
```

### **Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./v2-modern
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:5000/api
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/equity_dashboard
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=equity_dashboard
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### **Deploy with Docker**

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### **AWS Deployment**

#### **Frontend (S3 + CloudFront)**

```bash
# Build the frontend
cd v2-modern
npm run build

# Upload to S3
aws s3 sync dist/ s3://equity-dashboard-frontend

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

#### **Backend (ECS + Fargate)**

```yaml
# ecs-task-definition.json
{
  "family": "equity-dashboard-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/equity-dashboard-backend:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/equity_dashboard"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/equity-dashboard-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### **Database (RDS)**

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier equity-dashboard-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password your-password \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-12345678
```

### **Google Cloud Platform**

#### **Frontend (Cloud Storage + CDN)**

```bash
# Build the frontend
cd v2-modern
npm run build

# Upload to Cloud Storage
gsutil -m rsync -r dist/ gs://equity-dashboard-frontend

# Set up Cloud CDN
gcloud compute url-maps create equity-dashboard-map \
  --default-backend-bucket=equity-dashboard-frontend
```

#### **Backend (Cloud Run)**

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/equity-dashboard-backend', './backend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/equity-dashboard-backend']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: [
      'run', 'deploy', 'equity-dashboard-backend',
      '--image', 'gcr.io/$PROJECT_ID/equity-dashboard-backend',
      '--region', 'us-central1',
      '--platform', 'managed',
      '--allow-unauthenticated'
    ]
```

### **Azure Deployment**

#### **Frontend (Static Web Apps)**

```bash
# Install Azure CLI
npm install -g @azure/static-web-apps-cli

# Deploy to Azure Static Web Apps
swa deploy --app-location v2-modern --output-location dist
```

#### **Backend (Container Instances)**

```yaml
# azure-container-instance.yaml
apiVersion: 2021-07-01
location: eastus
name: equity-dashboard-backend
properties:
  containers:
  - name: backend
    properties:
      image: your-registry.azurecr.io/equity-dashboard-backend:latest
      ports:
      - port: 5000
      environmentVariables:
      - name: NODE_ENV
        value: production
      - name: DATABASE_URL
        secureValue: postgresql://user:pass@server:5432/equity_dashboard
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 5000
```

## 🔄 CI/CD Pipeline

### **GitHub Actions**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          cd v2-modern
          npm ci
          cd ../backend
          npm ci
      
      - name: Run tests
        run: |
          cd v2-modern
          npm test
          cd ../backend
          npm test

  build-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Build frontend
        run: |
          cd v2-modern
          npm ci
          npm run build
      
      - name: Deploy to S3
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Upload to S3
        run: |
          aws s3 sync v2-modern/dist/ s3://equity-dashboard-frontend
      
      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} --paths "/*"

  build-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Build backend
        run: |
          cd backend
          npm ci
          npm run build
      
      - name: Build Docker image
        run: |
          cd backend
          docker build -t equity-dashboard-backend .
      
      - name: Push to ECR
        uses: aws-actions/amazon-ecr-login@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster equity-dashboard-cluster --service equity-dashboard-backend --force-new-deployment
```

### **GitLab CI**

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  NODE_VERSION: "18"

test:
  stage: test
  image: node:${NODE_VERSION}-alpine
  script:
    - cd v2-modern && npm ci && npm test
    - cd ../backend && npm ci && npm test

build-frontend:
  stage: build
  image: node:${NODE_VERSION}-alpine
  script:
    - cd v2-modern
    - npm ci
    - npm run build
  artifacts:
    paths:
      - v2-modern/dist/
    expire_in: 1 hour

build-backend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - cd backend
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache aws-cli
    - aws s3 sync v2-modern/dist/ s3://equity-dashboard-frontend
    - aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
  only:
    - main
```

## 🔧 Environment Configuration

### **Environment Variables**

#### **Frontend (.env)**

```env
# API Configuration
VITE_API_BASE_URL=https://api.equity-research.com/api
VITE_WS_URL=wss://api.equity-research.com/ws

# Application Configuration
VITE_APP_NAME=Equity Research Dashboard
VITE_APP_VERSION=2.0.0

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=false

# External Services
VITE_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
VITE_SENTRY_DSN=https://your-sentry-dsn
```

#### **Backend (.env)**

```env
# Server Configuration
NODE_ENV=production
PORT=5000
HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/equity_dashboard
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET=your-jwt-secret
JWT_EXPIRES_IN=1h
REFRESH_TOKEN_SECRET=your-refresh-token-secret
REFRESH_TOKEN_EXPIRES_IN=7d

# External APIs
YAHOO_FINANCE_API_KEY=your-yahoo-finance-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
NEWS_API_KEY=your-news-api-key

# File Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=equity-dashboard-files

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=info
```

### **Configuration Management**

#### **Development**
```bash
# Use .env.local for local development
cp .env.example .env.local
# Edit .env.local with your local configuration
```

#### **Staging**
```bash
# Use environment-specific configuration
export NODE_ENV=staging
export DATABASE_URL=postgresql://user:pass@staging-db:5432/equity_dashboard
```

#### **Production**
```bash
# Use secure configuration management
# AWS Systems Manager Parameter Store
aws ssm put-parameter --name "/equity-dashboard/prod/database-url" --value "postgresql://..." --type "SecureString"
```

## 📊 Monitoring and Logging

### **Application Monitoring**

#### **Frontend Monitoring**

```typescript
// src/utils/monitoring.ts
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.NODE_ENV,
  tracesSampleRate: 1.0,
});

// Performance monitoring
export const trackPerformance = (metric: string, value: number) => {
  Sentry.addBreadcrumb({
    category: 'performance',
    message: metric,
    data: { value },
  });
};

// Error tracking
export const trackError = (error: Error, context?: any) => {
  Sentry.captureException(error, { extra: context });
};
```

#### **Backend Monitoring**

```typescript
// backend/src/monitoring.ts
import * as Sentry from '@sentry/node';
import { createLogger, format, transports } from 'winston';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
});

const logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  transports: [
    new transports.File({ filename: 'error.log', level: 'error' }),
    new transports.File({ filename: 'combined.log' }),
    new transports.Console({
      format: format.simple()
    })
  ]
});

export { logger, Sentry };
```

### **Infrastructure Monitoring**

#### **AWS CloudWatch**

```yaml
# cloudwatch-config.yml
Resources:
  DashboardAlarms:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighCPUUsage
      MetricName: CPUUtilization
      Namespace: AWS/ECS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SNSTopic
```

#### **Prometheus + Grafana**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'equity-dashboard-backend'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

## 🔒 Security Configuration

### **SSL/TLS Configuration**

#### **Nginx Configuration**

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.equity-research.com;
    
    ssl_certificate /etc/ssl/certs/api.equity-research.com.crt;
    ssl_certificate_key /etc/ssl/private/api.equity-research.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Security Headers**

```typescript
// backend/src/middleware/security.ts
import helmet from 'helmet';

export const securityMiddleware = helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
});
```

## 🚀 Deployment Checklist

### **Pre-Deployment**

- [ ] **Code Review**: All code reviewed and approved
- [ ] **Tests**: All tests passing (unit, integration, e2e)
- [ ] **Security Scan**: Security vulnerabilities addressed
- [ ] **Performance Test**: Performance benchmarks met
- [ ] **Documentation**: Documentation updated
- [ ] **Backup**: Database and files backed up

### **Deployment**

- [ ] **Environment**: Production environment configured
- [ ] **Database**: Database migrations applied
- [ ] **Secrets**: Environment variables and secrets configured
- [ ] **SSL**: SSL certificates installed and configured
- [ ] **DNS**: DNS records updated
- [ ] **CDN**: CDN configured and cache invalidated

### **Post-Deployment**

- [ ] **Health Check**: Application health checks passing
- [ ] **Monitoring**: Monitoring and alerting configured
- [ ] **Logs**: Log aggregation working
- [ ] **Performance**: Performance metrics within acceptable ranges
- [ ] **User Testing**: Critical user flows tested
- [ ] **Rollback Plan**: Rollback plan ready if needed

## 🔄 Rollback Procedures

### **Frontend Rollback**

```bash
# Rollback to previous version
aws s3 sync s3://equity-dashboard-frontend-backup/ s3://equity-dashboard-frontend/
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
```

### **Backend Rollback**

```bash
# Rollback ECS service to previous task definition
aws ecs update-service --cluster equity-dashboard-cluster --service equity-dashboard-backend --task-definition equity-dashboard-backend:PREVIOUS_REVISION
```

### **Database Rollback**

```bash
# Restore database from backup
pg_restore --host=localhost --port=5432 --username=admin --dbname=equity_dashboard backup.sql
```

## 📚 Additional Resources

- **[Architecture Guide](ARCHITECTURE.md)** - System architecture details
- **[API Documentation](API.md)** - API endpoints and usage
- **[Monitoring Guide](MONITORING.md)** - Monitoring and observability
- **[Security Guide](SECURITY.md)** - Security best practices
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions

---

For deployment support, please refer to the [Troubleshooting Guide](TROUBLESHOOTING.md) or contact our DevOps team.
