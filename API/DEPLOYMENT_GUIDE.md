# Stock Screener API - Deployment Guide

This guide covers deploying the Stock Screener API to production environments.

## 🎯 **Deployment Overview**

The Stock Screener API is designed to be production-ready with minimal configuration. It can be deployed on various platforms including cloud servers, VPS, or on-premises infrastructure.

## 🛠️ **Production Requirements**

### System Requirements
- **CPU**: 2+ cores (4+ recommended for high traffic)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 10GB+ (SSD recommended)
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, or similar)
- **PostgreSQL**: 16+ with connection pooling
- **Python**: 3.8+ with production WSGI server

### Network Requirements
- **Port 8000**: API access (or custom port)
- **Port 5432**: PostgreSQL (internal access only)
- **HTTPS**: SSL/TLS termination (recommended)
- **Firewall**: Proper security rules

## 🚀 **Deployment Options**

### Option 1: Traditional Server Deployment

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# Create application user
sudo useradd -m -s /bin/bash screener
sudo usermod -aG sudo screener
```

#### 2. Application Setup
```bash
# Switch to application user
sudo su - screener

# Clone repository
git clone <your-repo-url> stock-screener
cd stock-screener

# Create virtual environment
python3 -m venv trade_env
source trade_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production WSGI server
pip install gunicorn
```

#### 3. Database Setup
```bash
# Configure PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE screener_prod;
CREATE USER screener_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE screener_prod TO screener_user;
ALTER USER screener_user CREATEDB;
\q

# Restore database
psql -U screener_user -h localhost screener_prod < "screener_db 16th June.sql"
```

#### 4. Environment Configuration
```bash
# Create production environment file
cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=screener_prod
DB_USER=screener_user
DB_PASSWORD=your_secure_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your_secret_key_here

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/screener/app.log
EOF
```

#### 5. Systemd Service
```bash
# Create systemd service
sudo tee /etc/systemd/system/stock-screener.service << EOF
[Unit]
Description=Stock Screener API
After=network.target postgresql.service

[Service]
Type=exec
User=screener
Group=screener
WorkingDirectory=/home/screener/stock-screener
Environment=PATH=/home/screener/stock-screener/trade_env/bin
ExecStart=/home/screener/stock-screener/trade_env/bin/gunicorn main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable stock-screener
sudo systemctl start stock-screener
```

#### 6. Nginx Reverse Proxy
```bash
# Configure Nginx
sudo tee /etc/nginx/sites-available/stock-screener << EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/stock-screener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 screener && chown -R screener:screener /app
USER screener

# Expose port
EXPOSE 8000

# Start application
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

#### 2. Docker Compose Setup
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=screener_db
      - DB_USER=screener_user
      - DB_PASSWORD=secure_password
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=screener_db
      - POSTGRES_USER=screener_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./screener_db_16th_June.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

### Option 3: Cloud Platform Deployment

#### AWS EC2 Deployment
```bash
# Launch EC2 instance (t3.medium or larger)
# Configure security groups: 80, 443, 22

# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Follow traditional server setup steps above
# Configure RDS for PostgreSQL (recommended)
```

#### Google Cloud Platform
```bash
# Create Compute Engine instance
gcloud compute instances create stock-screener \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud

# Setup firewall rules
gcloud compute firewall-rules create allow-stock-screener \
    --allow tcp:80,tcp:443 \
    --target-tags stock-screener

# Follow traditional setup or use Cloud SQL
```

## 🔒 **Security Configuration**

### SSL/TLS Setup
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Configure auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration
```bash
# Configure UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# For PostgreSQL (if external access needed)
sudo ufw allow from trusted_ip to any port 5432
```

### Application Security
```bash
# Set secure environment variables
export SECRET_KEY=$(openssl rand -hex 32)
export DB_PASSWORD=$(openssl rand -base64 32)

# Restrict file permissions
chmod 600 .env
chmod 755 /home/screener/stock-screener
```

## 📊 **Performance Optimization**

### Database Optimization
```sql
-- Create performance indexes
CREATE INDEX idx_indicators_symbol_datetime ON indicators (symbol, datetime);
CREATE INDEX idx_indicators_rsi_14 ON indicators (rsi_14);
CREATE INDEX idx_indicators_volume_sma_20 ON indicators (volume_sma_20);
CREATE INDEX idx_candles_symbol_datetime ON one_min_candle_data (symbol, datetime);

-- Configure PostgreSQL settings
-- Edit /etc/postgresql/16/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
max_connections = 100
```

### Application Performance
```bash
# Configure Gunicorn for production
# Create gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 30
keepalive = 2
```

### Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client

# System monitoring
sudo apt install htop iotop nethogs

# Log monitoring
sudo apt install logrotate
```

## 🔍 **Health Checks & Monitoring**

### Application Health Check
```bash
# Create health check script
cat > health_check.sh << EOF
#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
if [ $RESPONSE -eq 200 ]; then
    echo "API is healthy"
    exit 0
else
    echo "API is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
EOF

chmod +x health_check.sh

# Add to crontab for monitoring
*/5 * * * * /home/screener/stock-screener/health_check.sh
```

### Log Configuration
```python
# Add to main.py for production logging
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        '/var/log/screener/app.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

## 🔄 **Backup & Recovery**

### Database Backup
```bash
# Create backup script
cat > backup_db.sh << EOF
#!/bin/bash
BACKUP_DIR="/backup/screener"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U screener_user -h localhost screener_prod > $BACKUP_DIR/screener_backup_$DATE.sql
gzip $BACKUP_DIR/screener_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup_db.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /home/screener/stock-screener/backup_db.sh
```

### Application Backup
```bash
# Backup application code and configuration
tar -czf screener_app_$(date +%Y%m%d).tar.gz \
    /home/screener/stock-screener \
    --exclude='trade_env' \
    --exclude='__pycache__'
```

## 📈 **Scaling Considerations**

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Multiple API instances
- Read replicas for PostgreSQL
- Redis caching layer

### Vertical Scaling
- Increase server resources
- Optimize database configuration
- Tune application workers

### Caching Strategy
```python
# Add Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## 🎯 **Production Checklist**

### Pre-Deployment
- [ ] Set secure environment variables
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Create database backups
- [ ] Configure monitoring
- [ ] Set up log rotation
- [ ] Test health checks

### Post-Deployment
- [ ] Verify API endpoints work
- [ ] Check database connectivity
- [ ] Test SSL certificate
- [ ] Monitor system resources
- [ ] Verify backup scripts
- [ ] Document deployment

### Ongoing Maintenance
- [ ] Regular security updates
- [ ] Database maintenance
- [ ] Log monitoring
- [ ] Performance monitoring
- [ ] Backup verification
- [ ] SSL certificate renewal

Your Stock Screener API is now ready for production! 🚀 