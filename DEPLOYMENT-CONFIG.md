# Deployment Configuration Guide

## Overview
This guide covers various deployment scenarios for the interior design image transformation service.

## Deployment Scenarios

### Scenario 1: Local Development
**Best for:** Testing and development

**Setup:**
```bash
# Terminal 1: Start API
python app.py

# Terminal 2: Serve frontend
python -m http.server 8000
```

**Configuration:**
- `script.js`: `const API_BASE_URL = 'http://localhost:5000'`
- No special environment variables needed

---

### Scenario 2: Docker Single Container
**Best for:** Quick deployment, CI/CD pipelines

**Prerequisites:**
- Docker installed
- Docker GPU support (nvidia-docker)

**Commands:**
```bash
# Build image
docker build -t interior-design-api:latest .

# Run container
docker run -p 5000:5000 \
  --gpus all \
  -v $(pwd)/prompt_history:/app/prompt_history \
  -v $(pwd)/generated_images:/app/generated_images \
  --name interior-api \
  interior-design-api:latest

# Frontend access
# Update script.js: const API_BASE_URL = 'http://docker-host:5000'
```

**Environment Variables:**
```bash
-e FLASK_ENV=production
-e CUDA_VISIBLE_DEVICES=0
-e HUGGINGFACE_HUB_CACHE=/root/.cache/huggingface
```

---

### Scenario 3: Docker Compose (Recommended)
**Best for:** Production-ready deployments

**Setup:**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

**Access:**
- Frontend: `http://localhost:8000`
- API: `http://localhost:5000`

**Configuration (`docker-compose.yml`):**
- Auto-setup frontend and API
- GPU support enabled
- Persistent volumes for cache
- Health checks configured

**Scale Services:**
```bash
# Use multiple GPU workers (requires load balancer)
docker-compose up -d --scale api=2
```

---

### Scenario 4: Kubernetes Deployment
**Best for:** Enterprise/cloud deployments

**Create namespace:**
```bash
kubectl create namespace interior-design
```

**Deploy API:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: interior-api
  namespace: interior-design
spec:
  replicas: 1
  selector:
    matchLabels:
      app: interior-api
  template:
    metadata:
      labels:
        app: interior-api
    spec:
      containers:
      - name: api
        image: interior-design-api:latest
        ports:
        - containerPort: 5000
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
          requests:
            nvidia.com/gpu: 1
            memory: "12Gi"
        volumeMounts:
        - name: cache
          mountPath: /root/.cache/huggingface
        - name: outputs
          mountPath: /app/generated_images
      volumes:
      - name: cache
        persistentVolumeClaim:
          claimName: hf-cache-pvc
      - name: outputs
        persistentVolumeClaim:
          claimName: output-pvc
```

**Deploy Frontend:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: interior-frontend
  namespace: interior-design
spec:
  replicas: 2
  selector:
    matchLabels:
      app: interior-frontend
  template:
    metadata:
      labels:
        app: interior-frontend
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html
      volumes:
      - name: html
        configMap:
          name: frontend-files
```

**Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: interior-api-service
  namespace: interior-design
spec:
  type: LoadBalancer
  ports:
  - port: 5000
    targetPort: 5000
  selector:
    app: interior-api
```

---

### Scenario 5: Cloud Deployment (AWS EC2)
**Best for:** Scalable production

**Instance Setup:**
```bash
# EC2 Instance with GPU (e.g., p3.2xlarge)
ubuntu 22.04 LTS
NVIDIA Driver: 535+
```

**Installation:**
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nvidia-docker2

# Clone repo
git clone <repo-url>
cd interior-design-site

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/interior-api.service
```

**Systemd Service File:**
```ini
[Unit]
Description=Interior Design API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/interior-design-site
Environment="PATH=/home/ubuntu/interior-design-site/venv/bin"
ExecStart=/home/ubuntu/interior-design-site/venv/bin/gunicorn \
  -w 1 \
  -b 0.0.0.0:5000 \
  app:app \
  --timeout 300
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start interior-api
sudo systemctl enable interior-api
```

**Update Frontend:**
- Point `API_BASE_URL` to EC2 public IP or domain

---

### Scenario 6: AWS Lambda + S3 (Serverless)
**Best for:** Minimal ops, cost-effective

**Deployment:**
```bash
# Package for Lambda
pip install -r requirements-lambda.txt -t package/
cd package
zip -r ../function.zip .
cd ..
zip -g function.zip app.py image_service.py

# Create Lambda function
aws lambda create-function \
  --function-name interior-design \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler app.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 300 \
  --memory-size 3008
```

**API Gateway Setup:**
```bash
# Create API Gateway integration
aws apigateway create-rest-api \
  --name interior-design-api

# Configure endpoints
# POST /transform
# POST /generate-prompt
# GET /health
```

---

### Scenario 7: Azure Container Instances
**Best for:** Easy Azure integration

**Create container:**
```bash
# Build and push image
docker build -t interior-design-api:latest .
docker tag interior-design-api:latest myregistry.azurecr.io/interior-design-api:latest
docker push myregistry.azurecr.io/interior-design-api:latest

# Deploy
az container create \
  --resource-group myresourcegroup \
  --name interior-api \
  --image myregistry.azurecr.io/interior-design-api:latest \
  --cpu 4 \
  --memory 16 \
  --ports 5000 \
  --environment-variables FLASK_ENV=production
```

---

### Scenario 8: GCP Cloud Run
**Best for:** Google Cloud integration

**Deployment:**
```bash
# Configure credentials
gcloud auth configure-docker

# Build and push
docker build -t interior-design-api .
docker tag interior-design-api gcr.io/PROJECT_ID/interior-design-api
docker push gcr.io/PROJECT_ID/interior-design-api

# Deploy to Cloud Run
gcloud run deploy interior-design \
  --image gcr.io/PROJECT_ID/interior-design-api \
  --platform managed \
  --region us-central1 \
  --memory 16Gi \
  --timeout 300 \
  --set-env-vars FLASK_ENV=production
```

---

## Configuration Files

### Environment Variables

**Development:**
```bash
FLASK_ENV=development
FLASK_DEBUG=1
MAX_FILE_SIZE=52428800
```

**Production:**
```bash
FLASK_ENV=production
FLASK_DEBUG=0
MAX_FILE_SIZE=52428800
HUGGINGFACE_HUB_CACHE=/persistent/cache
API_PORT=5000
WORKERS=1
```

### Frontend Configuration

**script.js:**
```javascript
// Development
const API_BASE_URL = 'http://localhost:5000';

// Production
const API_BASE_URL = 'https://api.youromain.com';

// Docker
const API_BASE_URL = 'http://docker-host:5000';

// AWS
const API_BASE_URL = 'https://your-api-id.execute-api.region.amazonaws.com';
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_request_buffering off;
        proxy_buffering off;
        proxy_read_timeout 300s;
    }

    location /static/ {
        alias /var/www/interior-design/;
        expires 30d;
    }
}
```

---

## Performance Tuning

### For High Load

**Gunicorn Configuration:**
```bash
gunicorn \
  -w 4 \
  -b 0.0.0.0:5000 \
  -k uvicorn.workers.UvicornWorker \
  --timeout 300 \
  --max-requests 100 \
  app:app
```

### For Low-Resource Systems

```python
# In image_service.py
self.pipeline.enable_attention_slicing()
self.pipeline.enable_memory_efficient_attention()
```

### Caching

**Redis Setup (optional):**
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/generate-prompt')
@cache.cached(timeout=3600)
def generate_prompt():
    ...
```

---

## Monitoring & Logging

### Logs

**Docker:**
```bash
docker logs -f interior-api
```

**Systemd:**
```bash
journalctl -u interior-api -f
```

### Monitoring

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Prometheus Metrics (optional):**
```python
from prometheus_client import Counter, Histogram

transform_requests = Counter('transform_requests', 'Image transformations')
transform_duration = Histogram('transform_duration', 'Transformation time')
```

---

## Security Considerations

### API Key Authentication

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/transform', methods=['POST'])
@require_api_key
def transform_image():
    ...
```

### SSL/TLS

```nginx
listen 443 ssl http2;
ssl_certificate /etc/ssl/certs/domain.crt;
ssl_certificate_key /etc/ssl/private/domain.key;
ssl_protocols TLSv1.2 TLSv1.3;
```

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/transform', methods=['POST'])
@limiter.limit("5 per hour")
def transform_image():
    ...
```

---

## Backup & Recovery

### Persistent Storage

**Volumes to backup:**
- `prompt_history/` - Design briefs
- `generated_images/` - Generated room images
- Huggingface cache (optional, can be re-downloaded)

**Automated Backup:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/interior-design"
DATE=$(date +%Y%m%d_%H%M%S)

tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" \
  ./prompt_history \
  ./generated_images

# Upload to S3/Cloud Storage
aws s3 cp "$BACKUP_DIR/backup_$DATE.tar.gz" s3://backups/
```

---

## Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| Cannot connect to API | Check firewall, ensure port 5000 is open |
| Out of GPU memory | Enable attention slicing, reduce workers |
| Slow generation | Check GPU utilization, add more workers |
| Models not downloading | Check internet, increase timeout |
| CORS errors | Update API_BASE_URL in frontend |

---

## Cost Estimation

| Deployment | Monthly Cost |
|---|---|
| Local Dev | $0 |
| EC2 p3.2xlarge | ~$3,000 |
| AWS Lambda | ~$50-200 |
| GCP Cloud Run | ~$100-300 |
| Azure Container | ~$200-400 |

---

## Next Steps

1. Choose appropriate scenario for your use case
2. Follow setup instructions
3. Test with sample images
4. Monitor performance
5. Adjust configuration as needed
