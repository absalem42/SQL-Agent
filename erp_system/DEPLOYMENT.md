# 🚀 ERP System Deployment Guide

This guide covers different deployment options for the Intelligent ERP Agent System.

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- Google API Key (recommended) or Ollama for local LLM

## 🐳 Docker Deployment (Recommended)

### Quick Start
```bash
# Clone and navigate to project
git clone <repository-url>
cd erp_system

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Build and run
docker-compose up --build
```

### Services
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

### Docker Configuration

#### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./databases:/app/databases
      - ./logs:/app/logs
    environment:
      - DB_PATH=databases/erp_sample.db
    network_mode: host  # For Ollama connectivity
    
  frontend:
    build: .
    command: streamlit run frontend/streamlit_app.py --server.port=8501
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "backend/api.py"]
```

## 💻 Local Development

### Setup Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
```bash
# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_google_api_key_here
DB_PATH=databases/erp_sample.db
OLLAMA_BASE_URL=http://localhost:11434
EOF
```

### Running Services

#### Backend (FastAPI)
```bash
cd backend
python api.py
```

#### Frontend (Streamlit)
```bash
cd frontend
streamlit run streamlit_app.py
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS
```yaml
# ecs-task-definition.json
{
  "family": "erp-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "erp-backend",
      "image": "your-ecr-repo/erp-system:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GOOGLE_API_KEY",
          "value": "your-api-key"
        }
      ]
    }
  ]
}
```

#### Deployment Commands
```bash
# Build and push to ECR
docker build -t erp-system .
docker tag erp-system:latest your-account.dkr.ecr.region.amazonaws.com/erp-system:latest
docker push your-account.dkr.ecr.region.amazonaws.com/erp-system:latest

# Create ECS service
aws ecs create-service --cluster erp-cluster --service-name erp-service --task-definition erp-system:1 --desired-count 1
```

### Google Cloud Platform

#### Cloud Run Deployment
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/erp-system
gcloud run deploy erp-system --image gcr.io/YOUR_PROJECT_ID/erp-system --platform managed --region us-central1
```

#### Cloud Run Configuration
```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: erp-system
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/YOUR_PROJECT_ID/erp-system
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: erp-secrets
              key: api-key
```

## 🔧 Configuration Options

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_google_gemini_api_key
DB_PATH=databases/erp_sample.db

# Optional
OLLAMA_BASE_URL=http://localhost:11434  # For local LLM fallback
LOG_LEVEL=INFO
MAX_WORKERS=4
```

### Database Configuration
```python
# For production PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/erp_db

# For SQLite (default)
DB_PATH=databases/erp.db
```

## 🔒 Security Considerations

### API Security
```python
# Add API key authentication
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/protected")
async def protected_route(token: str = Security(security)):
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Access granted"}
```

### Environment Security
```bash
# Use secrets management
# AWS Secrets Manager
aws secretsmanager create-secret --name erp-google-api-key --secret-string "your-api-key"

# Google Secret Manager
gcloud secrets create erp-google-api-key --data-file=api-key.txt
```

## 📊 Monitoring and Logging

### Health Checks
```python
# Built-in health endpoint
GET /health
{
  "status": "healthy",
  "database": "connected",
  "agents": {
    "router": "available",
    "sales": "available"
  }
}
```

### Logging Configuration
```python
# logging.conf
[loggers]
keys=root,erp

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_erp]
level=DEBUG
handlers=fileHandler
qualname=erp
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=simpleFormatter
args=('/app/logs/erp.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy ERP System

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest backend/tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build and push Docker image
      run: |
        docker build -t erp-system .
        docker tag erp-system ${{ secrets.DOCKER_REGISTRY }}/erp-system:latest
        docker push ${{ secrets.DOCKER_REGISTRY }}/erp-system:latest
    - name: Deploy to production
      run: |
        # Your deployment commands here
```

## 🚨 Troubleshooting

### Common Issues

#### Docker Build Fails
```bash
# Clear docker cache
docker system prune -a

# Rebuild with no cache
docker-compose build --no-cache
```

#### Database Connection Issues
```bash
# Check database file permissions
chmod 664 databases/erp_sample.db

# Verify database path in .env
DB_PATH=databases/erp_sample.db  # Relative to project root
```

#### LLM Connection Issues
```bash
# Test Google API
curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models

# Test Ollama (if using)
curl http://localhost:11434/api/tags
```

### Performance Optimization

#### Database Optimization
```sql
-- Add indexes for better query performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_leads_status ON leads(status);
```

#### Memory Management
```python
# Adjust connection pool settings
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancers for multiple backend instances
- Implement database connection pooling
- Cache frequently accessed data with Redis

### Vertical Scaling
- Increase container CPU/memory limits
- Optimize database queries
- Use async processing for long-running tasks

---

**For additional support, please refer to the main README.md or create an issue in the repository.**
