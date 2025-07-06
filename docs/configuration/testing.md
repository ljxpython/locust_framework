# 测试环境配置

本文档详细介绍如何配置Locust性能测试框架的测试环境，包括测试环境搭建、配置管理和测试数据准备。

## 🎯 测试环境架构

### 环境分层

```yaml
# testing/environment_layers.yml
environment_layers:
  unit_testing:
    description: "单元测试环境"
    scope: "单个组件测试"
    isolation: "完全隔离"
    dependencies: "最小化"

  integration_testing:
    description: "集成测试环境"
    scope: "组件间交互测试"
    isolation: "部分隔离"
    dependencies: "真实服务"

  system_testing:
    description: "系统测试环境"
    scope: "完整系统测试"
    isolation: "接近生产"
    dependencies: "完整服务栈"

  performance_testing:
    description: "性能测试环境"
    scope: "性能和负载测试"
    isolation: "独立环境"
    dependencies: "生产级配置"
```

### 测试环境拓扑

```mermaid
graph TD
    A[测试控制器] --> B[Locust Master]
    B --> C[Locust Worker 1]
    B --> D[Locust Worker 2]
    B --> E[Locust Worker N]

    C --> F[目标应用集群]
    D --> F
    E --> F

    F --> G[数据库集群]
    F --> H[缓存集群]
    F --> I[消息队列]

    J[监控系统] --> B
    J --> F
    J --> G
    J --> H
    J --> I

    K[日志收集] --> B
    K --> F
```

## 🏗️ 基础设施配置

### 1. Docker测试环境

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  # Locust Master
  locust-master:
    build:
      context: .
      dockerfile: Dockerfile.test
    container_name: locust-master-test
    ports:
      - "8089:8089"
      - "5557:5557"
    environment:
      - LOCUST_MODE=master
      - LOCUST_MASTER_BIND_HOST=0.0.0.0
      - LOCUST_MASTER_BIND_PORT=5557
      - LOCUST_WEB_HOST=0.0.0.0
      - LOCUST_WEB_PORT=8089
    volumes:
      - ./locustfiles:/app/locustfiles
      - ./test-data:/app/test-data
      - ./logs:/app/logs
    networks:
      - test-network
    depends_on:
      - target-app
      - redis
      - postgres

  # Locust Workers
  locust-worker-1:
    build:
      context: .
      dockerfile: Dockerfile.test
    container_name: locust-worker-1-test
    environment:
      - LOCUST_MODE=worker
      - LOCUST_MASTER_HOST=locust-master
      - LOCUST_MASTER_PORT=5557
    volumes:
      - ./locustfiles:/app/locustfiles
      - ./test-data:/app/test-data
    networks:
      - test-network
    depends_on:
      - locust-master

  locust-worker-2:
    build:
      context: .
      dockerfile: Dockerfile.test
    container_name: locust-worker-2-test
    environment:
      - LOCUST_MODE=worker
      - LOCUST_MASTER_HOST=locust-master
      - LOCUST_MASTER_PORT=5557
    volumes:
      - ./locustfiles:/app/locustfiles
      - ./test-data:/app/test-data
    networks:
      - test-network
    depends_on:
      - locust-master

  # 目标应用
  target-app:
    image: nginx:alpine
    container_name: target-app-test
    ports:
      - "8080:80"
    volumes:
      - ./test-configs/nginx.conf:/etc/nginx/nginx.conf
      - ./test-data/static:/usr/share/nginx/html
    networks:
      - test-network

  # 数据库
  postgres:
    image: postgres:13
    container_name: postgres-test
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=testdb
      - POSTGRES_USER=testuser
      - POSTGRES_PASSWORD=testpass
    volumes:
      - postgres-test-data:/var/lib/postgresql/data
      - ./test-data/sql:/docker-entrypoint-initdb.d
    networks:
      - test-network

  # 缓存
  redis:
    image: redis:alpine
    container_name: redis-test
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-test-data:/data
    networks:
      - test-network

  # 消息队列
  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq-test
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=testuser
      - RABBITMQ_DEFAULT_PASS=testpass
    volumes:
      - rabbitmq-test-data:/var/lib/rabbitmq
    networks:
      - test-network

  # 监控
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus-test
    ports:
      - "9090:9090"
    volumes:
      - ./test-configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-test-data:/prometheus
    networks:
      - test-network

networks:
  test-network:
    driver: bridge

volumes:
  postgres-test-data:
  redis-test-data:
  rabbitmq-test-data:
  prometheus-test-data:
```

### 2. Kubernetes测试环境

```yaml
# k8s/test-namespace.yml
apiVersion: v1
kind: Namespace
metadata:
  name: locust-test
  labels:
    environment: test
    purpose: performance-testing

---
# k8s/locust-master-test.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-master
  namespace: locust-test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: locust-master
  template:
    metadata:
      labels:
        app: locust-master
    spec:
      containers:
      - name: locust-master
        image: locust-framework:test
        ports:
        - containerPort: 8089
        - containerPort: 5557
        env:
        - name: LOCUST_MODE
          value: "master"
        - name: LOCUST_MASTER_BIND_HOST
          value: "0.0.0.0"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        volumeMounts:
        - name: locustfiles
          mountPath: /app/locustfiles
        - name: test-data
          mountPath: /app/test-data
      volumes:
      - name: locustfiles
        configMap:
          name: locustfiles-config
      - name: test-data
        configMap:
          name: test-data-config

---
apiVersion: v1
kind: Service
metadata:
  name: locust-master-service
  namespace: locust-test
spec:
  selector:
    app: locust-master
  ports:
  - name: web
    port: 8089
    targetPort: 8089
  - name: master
    port: 5557
    targetPort: 5557
  type: LoadBalancer

---
# k8s/locust-worker-test.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-worker
  namespace: locust-test
spec:
  replicas: 3
  selector:
    matchLabels:
      app: locust-worker
  template:
    metadata:
      labels:
        app: locust-worker
    spec:
      containers:
      - name: locust-worker
        image: locust-framework:test
        env:
        - name: LOCUST_MODE
          value: "worker"
        - name: LOCUST_MASTER_HOST
          value: "locust-master-service"
        - name: LOCUST_MASTER_PORT
          value: "5557"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: locustfiles
          mountPath: /app/locustfiles
        - name: test-data
          mountPath: /app/test-data
      volumes:
      - name: locustfiles
        configMap:
          name: locustfiles-config
      - name: test-data
        configMap:
          name: test-data-config
```

## ⚙️ 配置管理

### 1. 环境配置文件

```yaml
# config/test.yml
# 测试环境配置
environment:
  name: "test"
  description: "Performance testing environment"

# Locust配置
locust:
  host: "http://target-app:8080"
  users: 100
  spawn_rate: 10
  run_time: "300s"

  # Web UI配置
  web:
    host: "0.0.0.0"
    port: 8089
    auth_credentials: "admin:test123"

  # Master配置
  master:
    bind_host: "0.0.0.0"
    bind_port: 5557
    expect_workers: 2
    expect_workers_max_wait: 60

  # Worker配置
  worker:
    master_host: "locust-master"
    master_port: 5557

# 目标系统配置
target_system:
  base_url: "http://target-app:8080"
  api_version: "v1"
  timeout: 30
  retries: 3

  # 认证配置
  auth:
    type: "bearer_token"
    token_url: "/auth/token"
    username: "testuser"
    password: "testpass"

  # 端点配置
  endpoints:
    health: "/health"
    login: "/auth/login"
    logout: "/auth/logout"
    users: "/api/v1/users"
    orders: "/api/v1/orders"
    products: "/api/v1/products"

# 数据库配置
database:
  host: "postgres"
  port: 5432
  name: "testdb"
  username: "testuser"
  password: "testpass"
  pool_size: 10
  max_overflow: 20

# 缓存配置
cache:
  host: "redis"
  port: 6379
  db: 0
  password: ""
  timeout: 5

# 消息队列配置
message_queue:
  host: "rabbitmq"
  port: 5672
  username: "testuser"
  password: "testpass"
  virtual_host: "/"

# 监控配置
monitoring:
  prometheus:
    host: "prometheus"
    port: 9090
    scrape_interval: "15s"

  metrics:
    enabled: true
    port: 9090
    path: "/metrics"

  logging:
    level: "INFO"
    format: "json"
    file: "/app/logs/locust-test.log"

# 通知配置
notifications:
  enabled: true
  channels:
    - type: "slack"
      webhook_url: "https://hooks.slack.com/test-webhook"
      channel: "#testing"
    - type: "email"
      smtp_host: "smtp.test.com"
      recipients: ["test-team@company.com"]

# 测试数据配置
test_data:
  users:
    count: 1000
    file: "/app/test-data/users.json"

  products:
    count: 500
    file: "/app/test-data/products.json"

  orders:
    count: 2000
    file: "/app/test-data/orders.json"

  # 数据生成配置
  generation:
    locale: "zh_CN"
    seed: 12345
    batch_size: 100
```

### 2. 环境变量配置

```bash
# .env.test
# 基础环境配置
ENVIRONMENT=test
DEBUG=true
LOG_LEVEL=INFO

# Locust配置
LOCUST_HOST=http://target-app:8080
LOCUST_USERS=100
LOCUST_SPAWN_RATE=10
LOCUST_RUN_TIME=300s
LOCUST_WEB_HOST=0.0.0.0
LOCUST_WEB_PORT=8089

# 数据库配置
DATABASE_URL=postgresql://testuser:testpass@postgres:5432/testdb
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# 缓存配置
REDIS_URL=redis://redis:6379/0
REDIS_TIMEOUT=5

# 消息队列配置
RABBITMQ_URL=amqp://testuser:testpass@rabbitmq:5672/
RABBITMQ_EXCHANGE=locust_test

# 监控配置
PROMETHEUS_URL=http://prometheus:9090
METRICS_ENABLED=true
METRICS_PORT=9090

# 测试配置
TEST_DATA_DIR=/app/test-data
TEST_RESULTS_DIR=/app/test-results
TEST_TIMEOUT=3600

# 安全配置
SECRET_KEY=test-secret-key-change-in-production
JWT_SECRET=test-jwt-secret
API_KEY=test-api-key

# 第三方服务配置
SLACK_WEBHOOK_URL=https://hooks.slack.com/test-webhook
EMAIL_SMTP_HOST=smtp.test.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=test@company.com
EMAIL_PASSWORD=test-password
```

## 📊 测试数据管理

### 1. 测试数据生成

```python
# test_data/data_generator.py
import json
import random
from faker import Faker
from datetime import datetime, timedelta
from pathlib import Path

class TestDataGenerator:
    """测试数据生成器"""

    def __init__(self, locale='zh_CN', seed=12345):
        self.fake = Faker(locale)
        Faker.seed(seed)
        random.seed(seed)
        self.output_dir = Path("test-data")
        self.output_dir.mkdir(exist_ok=True)

    def generate_users(self, count=1000):
        """生成用户数据"""
        users = []

        for i in range(count):
            user = {
                "id": i + 1,
                "username": self.fake.user_name(),
                "email": self.fake.email(),
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "phone": self.fake.phone_number(),
                "address": {
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "state": self.fake.state(),
                    "zip_code": self.fake.postcode(),
                    "country": "中国"
                },
                "profile": {
                    "age": random.randint(18, 80),
                    "gender": random.choice(["male", "female"]),
                    "occupation": self.fake.job(),
                    "company": self.fake.company()
                },
                "preferences": {
                    "language": random.choice(["zh", "en"]),
                    "currency": "CNY",
                    "timezone": "Asia/Shanghai"
                },
                "created_at": self.fake.date_time_between(
                    start_date="-2y", end_date="now"
                ).isoformat(),
                "is_active": random.choice([True, True, True, False]),  # 75%活跃
                "last_login": self.fake.date_time_between(
                    start_date="-30d", end_date="now"
                ).isoformat()
            }
            users.append(user)

        # 保存到文件
        with open(self.output_dir / "users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        print(f"Generated {count} users")
        return users

    def generate_products(self, count=500):
        """生成产品数据"""
        categories = ["电子产品", "服装", "家居", "图书", "运动", "美妆", "食品"]
        products = []

        for i in range(count):
            category = random.choice(categories)
            product = {
                "id": i + 1,
                "name": self.fake.catch_phrase(),
                "description": self.fake.text(max_nb_chars=200),
                "category": category,
                "price": round(random.uniform(10, 1000), 2),
                "currency": "CNY",
                "stock": random.randint(0, 1000),
                "sku": f"SKU{i+1:06d}",
                "brand": self.fake.company(),
                "specifications": {
                    "weight": f"{random.uniform(0.1, 10):.2f}kg",
                    "dimensions": f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)}cm",
                    "color": self.fake.color_name(),
                    "material": random.choice(["塑料", "金属", "木材", "布料", "玻璃"])
                },
                "ratings": {
                    "average": round(random.uniform(3.0, 5.0), 1),
                    "count": random.randint(0, 1000)
                },
                "images": [
                    f"https://example.com/images/product_{i+1}_1.jpg",
                    f"https://example.com/images/product_{i+1}_2.jpg"
                ],
                "created_at": self.fake.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat(),
                "is_available": random.choice([True, True, True, False])  # 75%可用
            }
            products.append(product)

        # 保存到文件
        with open(self.output_dir / "products.json", "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        print(f"Generated {count} products")
        return products

    def generate_orders(self, count=2000, users=None, products=None):
        """生成订单数据"""
        if not users:
            with open(self.output_dir / "users.json", "r", encoding="utf-8") as f:
                users = json.load(f)

        if not products:
            with open(self.output_dir / "products.json", "r", encoding="utf-8") as f:
                products = json.load(f)

        orders = []
        statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]

        for i in range(count):
            user = random.choice(users)
            order_products = random.sample(products, random.randint(1, 5))

            total_amount = 0
            order_items = []

            for product in order_products:
                quantity = random.randint(1, 3)
                item_total = product["price"] * quantity
                total_amount += item_total

                order_items.append({
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "price": product["price"],
                    "quantity": quantity,
                    "total": item_total
                })

            order = {
                "id": i + 1,
                "user_id": user["id"],
                "user_email": user["email"],
                "items": order_items,
                "total_amount": round(total_amount, 2),
                "currency": "CNY",
                "status": random.choice(statuses),
                "payment": {
                    "method": random.choice(["credit_card", "alipay", "wechat_pay", "bank_transfer"]),
                    "status": random.choice(["pending", "completed", "failed"]),
                    "transaction_id": f"TXN{i+1:08d}"
                },
                "shipping": {
                    "address": user["address"],
                    "method": random.choice(["standard", "express", "overnight"]),
                    "cost": round(random.uniform(5, 50), 2),
                    "tracking_number": f"TRK{i+1:010d}"
                },
                "created_at": self.fake.date_time_between(
                    start_date="-6m", end_date="now"
                ).isoformat(),
                "updated_at": self.fake.date_time_between(
                    start_date="-6m", end_date="now"
                ).isoformat()
            }
            orders.append(order)

        # 保存到文件
        with open(self.output_dir / "orders.json", "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

        print(f"Generated {count} orders")
        return orders

    def generate_all(self, users_count=1000, products_count=500, orders_count=2000):
        """生成所有测试数据"""
        print("Generating test data...")

        users = self.generate_users(users_count)
        products = self.generate_products(products_count)
        orders = self.generate_orders(orders_count, users, products)

        # 生成汇总信息
        summary = {
            "generated_at": datetime.now().isoformat(),
            "counts": {
                "users": len(users),
                "products": len(products),
                "orders": len(orders)
            },
            "files": {
                "users": "users.json",
                "products": "products.json",
                "orders": "orders.json"
            }
        }

        with open(self.output_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print("Test data generation completed!")
        return summary

# 使用示例
if __name__ == "__main__":
    generator = TestDataGenerator()
    generator.generate_all()
```

### 2. 数据库初始化

```sql
-- test-data/sql/01_init_schema.sql
-- 创建测试数据库架构

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    address JSONB,
    profile JSONB,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP
);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'CNY',
    stock INTEGER DEFAULT 0,
    sku VARCHAR(50) UNIQUE,
    brand VARCHAR(100),
    specifications JSONB,
    ratings JSONB,
    images JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_available BOOLEAN DEFAULT TRUE
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'CNY',
    status VARCHAR(20),
    payment JSONB,
    shipping JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单项表
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    price DECIMAL(10,2),
    total DECIMAL(10,2)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
```

```python
# test-data/sql/02_load_data.py
import json
import psycopg2
from pathlib import Path

def load_test_data():
    """加载测试数据到数据库"""

    # 数据库连接
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        database="testdb",
        user="testuser",
        password="testpass"
    )

    cur = conn.cursor()

    try:
        # 加载用户数据
        with open("/app/test-data/users.json", "r", encoding="utf-8") as f:
            users = json.load(f)

        for user in users:
            cur.execute("""
                INSERT INTO users (
                    id, username, email, first_name, last_name, phone,
                    address, profile, preferences, created_at, is_active, last_login
                ) VALUES (
                    %(id)s, %(username)s, %(email)s, %(first_name)s, %(last_name)s, %(phone)s,
                    %(address)s, %(profile)s, %(preferences)s, %(created_at)s, %(is_active)s, %(last_login)s
                ) ON CONFLICT (id) DO NOTHING
            """, user)

        print(f"Loaded {len(users)} users")

        # 加载产品数据
        with open("/app/test-data/products.json", "r", encoding="utf-8") as f:
            products = json.load(f)

        for product in products:
            cur.execute("""
                INSERT INTO products (
                    id, name, description, category, price, currency, stock,
                    sku, brand, specifications, ratings, images, created_at, is_available
                ) VALUES (
                    %(id)s, %(name)s, %(description)s, %(category)s, %(price)s, %(currency)s, %(stock)s,
                    %(sku)s, %(brand)s, %(specifications)s, %(ratings)s, %(images)s, %(created_at)s, %(is_available)s
                ) ON CONFLICT (id) DO NOTHING
            """, product)

        print(f"Loaded {len(products)} products")

        # 加载订单数据
        with open("/app/test-data/orders.json", "r", encoding="utf-8") as f:
            orders = json.load(f)

        for order in orders:
            # 插入订单
            cur.execute("""
                INSERT INTO orders (
                    id, user_id, total_amount, currency, status,
                    payment, shipping, created_at, updated_at
                ) VALUES (
                    %(id)s, %(user_id)s, %(total_amount)s, %(currency)s, %(status)s,
                    %(payment)s, %(shipping)s, %(created_at)s, %(updated_at)s
                ) ON CONFLICT (id) DO NOTHING
            """, {
                "id": order["id"],
                "user_id": order["user_id"],
                "total_amount": order["total_amount"],
                "currency": order["currency"],
                "status": order["status"],
                "payment": json.dumps(order["payment"]),
                "shipping": json.dumps(order["shipping"]),
                "created_at": order["created_at"],
                "updated_at": order["updated_at"]
            })

            # 插入订单项
            for item in order["items"]:
                cur.execute("""
                    INSERT INTO order_items (
                        order_id, product_id, quantity, price, total
                    ) VALUES (
                        %(order_id)s, %(product_id)s, %(quantity)s, %(price)s, %(total)s
                    )
                """, {
                    "order_id": order["id"],
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "total": item["total"]
                })

        print(f"Loaded {len(orders)} orders")

        # 提交事务
        conn.commit()
        print("Test data loaded successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error loading test data: {e}")
        raise

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    load_test_data()
```
