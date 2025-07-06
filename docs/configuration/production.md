# 生产环境配置

本文档详细介绍如何在生产环境中部署和配置Locust性能测试框架，确保测试的稳定性、安全性和可扩展性。

## 🎯 生产环境要求

### 系统要求

**硬件配置**
```yaml
# 推荐配置
master_node:
  cpu: 4+ cores
  memory: 8GB+
  disk: 100GB+ SSD
  network: 1Gbps+

worker_nodes:
  cpu: 2+ cores per worker
  memory: 4GB+ per worker
  disk: 50GB+ SSD
  network: 1Gbps+

# 最小配置
minimal_setup:
  cpu: 2 cores
  memory: 4GB
  disk: 50GB
  network: 100Mbps
```

**软件环境**
```bash
# 操作系统
Ubuntu 20.04+ / CentOS 8+ / RHEL 8+

# Python版本
Python 3.8+

# 必需软件
- Docker 20.10+
- Docker Compose 2.0+
- Nginx 1.18+
- Redis 6.0+ (可选，用于分布式协调)
- PostgreSQL 13+ (可选，用于结果存储)
```

## 🐳 Docker化部署

### 1. 生产级Dockerfile

```dockerfile
# Dockerfile.production
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY requirements-prod.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-prod.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 locust && \
    chown -R locust:locust /app
USER locust

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8089/stats/requests || exit 1

# 暴露端口
EXPOSE 8089 5557

# 启动命令
CMD ["python", "-m", "locust", "--config", "conf/production.conf"]
```

### 2. Docker Compose配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  locust-master:
    build:
      context: .
      dockerfile: Dockerfile.production
    image: locust-framework:production
    container_name: locust-master
    ports:
      - "8089:8089"
      - "5557:5557"
    environment:
      - LOCUST_MODE=master
      - LOCUST_MASTER_BIND_HOST=0.0.0.0
      - LOCUST_MASTER_BIND_PORT=5557
      - LOCUST_WEB_HOST=0.0.0.0
      - LOCUST_WEB_PORT=8089
      - LOCUST_LOGLEVEL=INFO
    volumes:
      - ./conf:/app/conf:ro
      - ./logs:/app/logs
      - ./reports:/app/reports
    networks:
      - locust-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  locust-worker:
    build:
      context: .
      dockerfile: Dockerfile.production
    image: locust-framework:production
    environment:
      - LOCUST_MODE=worker
      - LOCUST_MASTER_HOST=locust-master
      - LOCUST_MASTER_PORT=5557
      - LOCUST_LOGLEVEL=INFO
    volumes:
      - ./conf:/app/conf:ro
      - ./logs:/app/logs
    networks:
      - locust-network
    depends_on:
      - locust-master
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  nginx:
    image: nginx:alpine
    container_name: locust-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - locust-network
    depends_on:
      - locust-master
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    container_name: locust-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
      - ./redis/redis.conf:/etc/redis/redis.conf:ro
    networks:
      - locust-network
    restart: unless-stopped
    command: redis-server /etc/redis/redis.conf

  postgres:
    image: postgres:13-alpine
    container_name: locust-postgres
    environment:
      - POSTGRES_DB=locust_results
      - POSTGRES_USER=locust
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - locust-network
    restart: unless-stopped

networks:
  locust-network:
    driver: bridge

volumes:
  redis-data:
  postgres-data:
```

## ⚙️ 生产配置文件

### 1. 主配置文件

```ini
# conf/production.conf
[locust]
# 基础配置
locustfile = locustfiles/production_test.py
host = https://api.production.com
web-host = 0.0.0.0
web-port = 8089

# 性能配置
users = 1000
spawn-rate = 50
run-time = 30m
headless = false

# 日志配置
loglevel = INFO
logfile = logs/locust.log

# 报告配置
html = reports/performance_report.html
csv = reports/performance_stats

# 分布式配置
master-bind-host = 0.0.0.0
master-bind-port = 5557
expect-workers = 3

# 高级配置
stop-timeout = 60
reset-stats = false
```

### 2. 环境变量配置

```bash
# .env.production
# 应用配置
LOCUST_ENV=production
LOCUST_LOG_LEVEL=INFO
LOCUST_WEB_AUTH=admin:secure_password_here

# 数据库配置
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=locust_results
POSTGRES_USER=locust
POSTGRES_PASSWORD=your_secure_password_here

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here

# 监控配置
MONITORING_ENABLED=true
ALERT_WEBHOOK_URL=https://hooks.slack.com/your-webhook
METRICS_RETENTION_DAYS=30

# 安全配置
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
ALLOWED_HOSTS=your-domain.com,localhost

# 性能配置
MAX_WORKERS=10
WORKER_MEMORY_LIMIT=2G
MASTER_MEMORY_LIMIT=4G
```

### 3. Nginx反向代理配置

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream locust_backend {
        server locust-master:8089;
    }

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn:10m;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # 安全头
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # 限流
        limit_req zone=api burst=20 nodelay;
        limit_conn conn 10;

        # 代理配置
        location / {
            proxy_pass http://locust_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket支持
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # 超时配置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 静态文件缓存
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## 🔒 安全配置

### 1. 认证和授权

```python
# security/auth.py
import hashlib
import secrets
from functools import wraps
from flask import request, Response

class SecurityManager:
    """安全管理器"""

    def __init__(self):
        self.api_keys = self.load_api_keys()
        self.rate_limits = {}

    def load_api_keys(self):
        """加载API密钥"""
        return {
            "admin": self.hash_password("admin_secure_password"),
            "readonly": self.hash_password("readonly_password")
        }

    def hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256',
                                  password.encode('utf-8'),
                                  salt.encode('utf-8'),
                                  100000).hex() + ':' + salt

    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            hash_part, salt = hashed.split(':')
            return hashlib.pbkdf2_hmac('sha256',
                                      password.encode('utf-8'),
                                      salt.encode('utf-8'),
                                      100000).hex() == hash_part
        except:
            return False

    def require_auth(self, f):
        """认证装饰器"""
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not self.verify_credentials(auth.username, auth.password):
                return Response('Authentication required', 401,
                              {'WWW-Authenticate': 'Basic realm="Locust"'})
            return f(*args, **kwargs)
        return decorated

    def verify_credentials(self, username: str, password: str) -> bool:
        """验证凭据"""
        if username in self.api_keys:
            return self.verify_password(password, self.api_keys[username])
        return False

# 使用安全管理器
security_manager = SecurityManager()

@security_manager.require_auth
def protected_endpoint():
    return "Protected content"
```

### 2. 网络安全配置

```yaml
# security/network-policy.yml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: locust-network-policy
spec:
  podSelector:
    matchLabels:
      app: locust
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8089
    - protocol: TCP
      port: 5557
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: target-system
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
```

## 📊 监控和告警

### 1. Prometheus监控配置

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "locust_rules.yml"

scrape_configs:
  - job_name: 'locust'
    static_configs:
      - targets: ['locust-master:8089']
    metrics_path: '/stats/requests/csv'
    scrape_interval: 30s

  - job_name: 'locust-workers'
    static_configs:
      - targets: ['locust-worker-1:8089', 'locust-worker-2:8089']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 2. 告警规则

```yaml
# monitoring/locust_rules.yml
groups:
- name: locust_alerts
  rules:
  - alert: HighErrorRate
    expr: locust_error_rate > 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }}% for more than 2 minutes"

  - alert: HighResponseTime
    expr: locust_avg_response_time > 2000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "Average response time is {{ $value }}ms"

  - alert: LowThroughput
    expr: locust_rps < 50
    for: 3m
    labels:
      severity: warning
    annotations:
      summary: "Low throughput detected"
      description: "RPS is {{ $value }}"

  - alert: WorkerDown
    expr: up{job="locust-workers"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Locust worker is down"
      description: "Worker {{ $labels.instance }} is not responding"
```

### 3. Grafana仪表板

```json
{
  "dashboard": {
    "title": "Locust Performance Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(locust_requests_total[5m])",
            "legendFormat": "RPS"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "locust_avg_response_time",
            "legendFormat": "Average"
          },
          {
            "expr": "locust_p95_response_time",
            "legendFormat": "95th Percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "locust_error_rate",
            "legendFormat": "Error Rate %"
          }
        ]
      }
    ]
  }
}
```

## 🚀 部署脚本

### 1. 自动化部署脚本

```bash
#!/bin/bash
# deploy.sh

set -e

# 配置变量
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

echo "Deploying Locust Framework to ${ENVIRONMENT} environment..."

# 检查环境
if [ ! -f "${COMPOSE_FILE}" ]; then
    echo "Error: ${COMPOSE_FILE} not found"
    exit 1
fi

# 加载环境变量
if [ -f ".env.${ENVIRONMENT}" ]; then
    source ".env.${ENVIRONMENT}"
fi

# 构建镜像
echo "Building Docker images..."
docker-compose -f ${COMPOSE_FILE} build

# 停止旧服务
echo "Stopping existing services..."
docker-compose -f ${COMPOSE_FILE} down

# 启动新服务
echo "Starting services..."
docker-compose -f ${COMPOSE_FILE} up -d

# 等待服务启动
echo "Waiting for services to start..."
sleep 30

# 健康检查
echo "Performing health checks..."
for i in {1..10}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "Health check passed"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "Health check failed"
        exit 1
    fi
    sleep 10
done

# 显示状态
docker-compose -f ${COMPOSE_FILE} ps

echo "Deployment completed successfully!"
echo "Access the web interface at: https://your-domain.com"
```

### 2. 滚动更新脚本

```bash
#!/bin/bash
# rolling_update.sh

set -e

COMPOSE_FILE="docker-compose.production.yml"
SERVICE_NAME="locust-worker"
NEW_IMAGE="locust-framework:${1:-latest}"

echo "Performing rolling update for ${SERVICE_NAME}..."

# 获取当前副本数
REPLICAS=$(docker-compose -f ${COMPOSE_FILE} ps -q ${SERVICE_NAME} | wc -l)

echo "Current replicas: ${REPLICAS}"

# 逐个更新worker
for i in $(seq 1 ${REPLICAS}); do
    echo "Updating worker ${i}/${REPLICAS}..."

    # 停止一个worker
    CONTAINER_ID=$(docker-compose -f ${COMPOSE_FILE} ps -q ${SERVICE_NAME} | head -n1)
    docker stop ${CONTAINER_ID}

    # 启动新的worker
    docker-compose -f ${COMPOSE_FILE} up -d --scale ${SERVICE_NAME}=${REPLICAS}

    # 等待新worker就绪
    sleep 30

    # 验证worker状态
    if ! docker-compose -f ${COMPOSE_FILE} ps ${SERVICE_NAME} | grep -q "Up"; then
        echo "Error: Worker failed to start"
        exit 1
    fi

    echo "Worker ${i} updated successfully"
done

echo "Rolling update completed successfully!"
```

## 🔧 性能调优

### 1. 系统级优化

```bash
# system_tuning.sh
#!/bin/bash

echo "Applying system-level optimizations..."

# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 网络优化
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
echo "net.core.netdev_max_backlog = 5000" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" >> /etc/sysctl.conf
echo "net.ipv4.tcp_keepalive_time = 600" >> /etc/sysctl.conf

# 应用设置
sysctl -p

echo "System optimization completed"
```

### 2. 应用级优化

```python
# optimization/performance_config.py
import os
import multiprocessing

class ProductionConfig:
    """生产环境性能配置"""

    # 进程配置
    WORKER_PROCESSES = min(multiprocessing.cpu_count(), 8)
    WORKER_CONNECTIONS = 1000
    WORKER_CLASS = "gevent"

    # 内存配置
    MAX_MEMORY_PER_WORKER = "2G"
    PRELOAD_APP = True

    # 网络配置
    KEEPALIVE = 2
    TIMEOUT = 30
    GRACEFUL_TIMEOUT = 30

    # 日志配置
    ACCESS_LOG = "/app/logs/access.log"
    ERROR_LOG = "/app/logs/error.log"
    LOG_LEVEL = "info"

    @classmethod
    def apply_optimizations(cls):
        """应用性能优化"""
        # 设置环境变量
        os.environ.update({
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "GEVENT_RESOLVER": "ares",
            "LOCUST_WORKER_PROCESSES": str(cls.WORKER_PROCESSES)
        })

        # 配置垃圾回收
        import gc
        gc.set_threshold(700, 10, 10)

        print(f"Applied optimizations: {cls.WORKER_PROCESSES} workers")
```

## 📚 运维手册

### 1. 日常维护检查清单

```markdown
## 日常检查 (每日)
- [ ] 检查服务状态
- [ ] 查看错误日志
- [ ] 监控资源使用率
- [ ] 验证备份完整性

## 周检查
- [ ] 更新安全补丁
- [ ] 清理旧日志文件
- [ ] 检查磁盘空间
- [ ] 性能趋势分析

## 月检查
- [ ] 容量规划评估
- [ ] 安全审计
- [ ] 灾难恢复测试
- [ ] 配置备份验证
```

### 2. 故障处理流程

```bash
# troubleshooting.sh
#!/bin/bash

echo "Locust Framework Troubleshooting Guide"
echo "======================================"

# 检查服务状态
echo "1. Checking service status..."
docker-compose ps

# 检查日志
echo "2. Checking recent logs..."
docker-compose logs --tail=50 locust-master
docker-compose logs --tail=50 locust-worker

# 检查资源使用
echo "3. Checking resource usage..."
docker stats --no-stream

# 检查网络连接
echo "4. Checking network connectivity..."
curl -I http://localhost/health

# 生成诊断报告
echo "5. Generating diagnostic report..."
{
    echo "=== System Information ==="
    uname -a
    echo "=== Docker Version ==="
    docker version
    echo "=== Disk Usage ==="
    df -h
    echo "=== Memory Usage ==="
    free -h
} > diagnostic_report.txt

echo "Diagnostic report saved to: diagnostic_report.txt"
```

## 🎉 总结

生产环境部署的关键要点：

1. **容器化部署**: 使用Docker确保环境一致性
2. **安全配置**: 实施认证、授权和网络安全
3. **监控告警**: 建立完善的监控和告警体系
4. **性能优化**: 系统和应用级别的性能调优
5. **自动化运维**: 部署、更新和维护的自动化

## 📚 相关文档

- [框架配置](framework-config.md) - 基础配置说明
- [监控配置](monitoring-config.md) - 监控系统配置
- [分布式配置](distributed.md) - 分布式部署配置
- [最佳实践](../examples/best-practices.md) - 性能测试最佳实践
