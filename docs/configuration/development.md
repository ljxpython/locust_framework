# 开发环境配置

本文档详细介绍如何配置Locust性能测试框架的开发环境，包括本地开发、调试配置和开发工具设置。

## 🛠️ 开发环境要求

### 系统要求

```yaml
# development/requirements.yml
system_requirements:
  operating_system:
    - "macOS 10.15+"
    - "Ubuntu 18.04+"
    - "Windows 10+"
    - "CentOS 7+"

  python:
    version: "3.8+"
    recommended: "3.9+"

  memory: "4GB+"
  disk_space: "2GB+"

  optional_tools:
    - docker
    - docker-compose
    - git
    - make
```

### 开发工具推荐

```yaml
# development/tools.yml
recommended_tools:
  ide:
    - "PyCharm Professional"
    - "Visual Studio Code"
    - "Sublime Text"
    - "Vim/Neovim"

  version_control:
    - "Git"
    - "GitHub Desktop"
    - "SourceTree"

  api_testing:
    - "Postman"
    - "Insomnia"
    - "curl"
    - "HTTPie"

  monitoring:
    - "htop"
    - "iotop"
    - "netstat"
    - "tcpdump"
```

## 🐍 Python环境配置

### 1. 虚拟环境设置

```bash
# 使用venv创建虚拟环境
python -m venv locust-dev
source locust-dev/bin/activate  # Linux/Mac
# 或
locust-dev\Scripts\activate  # Windows

# 使用conda创建环境
conda create -n locust-dev python=3.9
conda activate locust-dev

# 使用pyenv管理Python版本
pyenv install 3.9.16
pyenv virtualenv 3.9.16 locust-dev
pyenv activate locust-dev
```

### 2. 依赖安装

```bash
# 安装基础依赖
pip install --upgrade pip setuptools wheel

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装项目（可编辑模式）
pip install -e .

# 验证安装
locust --version
python -c "import locust; print(locust.__version__)"
```

### 3. 开发依赖文件

```txt
# requirements-dev.txt
# 基础框架
locust>=2.14.0
gevent>=21.12.0
requests>=2.25.0

# 开发工具
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-xdist>=3.2.0

# 代码质量
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0

# 文档工具
sphinx>=6.0.0
sphinx-rtd-theme>=1.2.0
myst-parser>=0.19.0

# 性能分析
memory-profiler>=0.60.0
line-profiler>=4.0.0
py-spy>=0.3.14

# 数据生成
faker>=18.0.0
factory-boy>=3.2.0

# 网络工具
websocket-client>=1.5.0
paho-mqtt>=1.6.0

# 监控集成
prometheus-client>=0.16.0
grafana-api>=1.0.3

# 通知集成
slack-sdk>=3.20.0
requests-oauthlib>=1.3.0

# 数据库支持
sqlalchemy>=2.0.0
redis>=4.5.0
pymongo>=4.3.0

# 云服务
boto3>=1.26.0
google-cloud-storage>=2.7.0
azure-storage-blob>=12.14.0
```

## 🔧 IDE配置

### 1. VS Code配置

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./locust-dev/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false
}
```

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Locust Master",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/locust-dev/bin/locust",
            "args": [
                "-f", "locustfiles/example.py",
                "--master",
                "--master-bind-host=0.0.0.0"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Locust Worker",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/locust-dev/bin/locust",
            "args": [
                "-f", "locustfiles/example.py",
                "--worker",
                "--master-host=localhost"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Debug Test",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/locust-dev/bin/python",
            "args": [
                "-m", "pytest",
                "tests/",
                "-v"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### 2. PyCharm配置

```python
# .idea/runConfigurations/Locust_Master.xml
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="Locust Master" type="PythonConfigurationType" factoryName="Python">
    <module name="locust-framework" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <envs>
      <env name="PYTHONUNBUFFERED" value="1" />
    </envs>
    <option name="SDK_HOME" value="$PROJECT_DIR$/locust-dev/bin/python" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="IS_MODULE_SDK" value="false" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <option name="SCRIPT_NAME" value="locust" />
    <option name="PARAMETERS" value="-f locustfiles/example.py --master --master-bind-host=0.0.0.0" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="false" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>
```

## 🐳 Docker开发环境

### 1. 开发用Docker配置

```dockerfile
# Dockerfile.dev
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    curl \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements-dev.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-dev.txt

# 复制源码
COPY . .

# 安装项目（开发模式）
RUN pip install -e .

# 设置环境变量
ENV PYTHONPATH=/app
ENV LOCUST_HOST=http://localhost:8080

# 暴露端口
EXPOSE 8089 5557

# 默认命令
CMD ["bash"]
```

### 2. Docker Compose开发配置

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  locust-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: locust-dev
    ports:
      - "8089:8089"
      - "5557:5557"
    volumes:
      - .:/app
      - locust-dev-cache:/root/.cache
    environment:
      - PYTHONPATH=/app
      - LOCUST_HOST=http://target-app:8080
    command: tail -f /dev/null  # 保持容器运行
    networks:
      - dev-network

  target-app:
    image: nginx:alpine
    container_name: target-app
    ports:
      - "8080:80"
    volumes:
      - ./test-data/nginx.conf:/etc/nginx/nginx.conf
    networks:
      - dev-network

  redis:
    image: redis:alpine
    container_name: redis-dev
    ports:
      - "6379:6379"
    networks:
      - dev-network

  postgres:
    image: postgres:13
    container_name: postgres-dev
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=locust_dev
      - POSTGRES_USER=locust
      - POSTGRES_PASSWORD=locust123
    volumes:
      - postgres-dev-data:/var/lib/postgresql/data
    networks:
      - dev-network

networks:
  dev-network:
    driver: bridge

volumes:
  locust-dev-cache:
  postgres-dev-data:
```

### 3. 开发脚本

```bash
#!/bin/bash
# scripts/dev-setup.sh

set -e

echo "Setting up Locust development environment..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is required but not installed."
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is required but not installed."
    exit 1
fi

# 构建开发环境
echo "Building development containers..."
docker-compose -f docker-compose.dev.yml build

# 启动服务
echo "Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# 等待服务启动
echo "Waiting for services to start..."
sleep 10

# 检查服务状态
echo "Checking service status..."
docker-compose -f docker-compose.dev.yml ps

# 运行测试
echo "Running tests..."
docker-compose -f docker-compose.dev.yml exec locust-dev pytest tests/ -v

echo "Development environment is ready!"
echo "Access Locust Web UI at: http://localhost:8089"
echo "Target app is available at: http://localhost:8080"

# 显示有用的命令
cat << EOF

Useful commands:
  # Enter development container
  docker-compose -f docker-compose.dev.yml exec locust-dev bash

  # Run Locust master
  docker-compose -f docker-compose.dev.yml exec locust-dev locust -f locustfiles/example.py --master

  # Run tests
  docker-compose -f docker-compose.dev.yml exec locust-dev pytest

  # Stop environment
  docker-compose -f docker-compose.dev.yml down
EOF
```

## 🧪 测试配置

### 1. pytest配置

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --durations=10

markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
    network: Tests requiring network access

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### 2. 测试环境变量

```bash
# .env.test
# 测试环境配置
LOCUST_HOST=http://localhost:8080
LOCUST_USERS=10
LOCUST_SPAWN_RATE=2
LOCUST_RUN_TIME=60s

# 数据库配置
DATABASE_URL=postgresql://locust:locust123@localhost:5432/locust_test
REDIS_URL=redis://localhost:6379/1

# 日志配置
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed

# 测试数据
TEST_DATA_DIR=tests/fixtures
FAKE_DATA_LOCALE=zh_CN

# API配置
API_BASE_URL=http://localhost:8080/api
API_TIMEOUT=30
API_RETRIES=3
```

### 3. 测试辅助工具

```python
# tests/conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

@pytest.fixture(scope="session")
def temp_dir():
    """创建临时目录"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def mock_locust_env():
    """模拟Locust环境"""
    with patch('locust.env.Environment') as mock_env:
        mock_env.stats = Mock()
        mock_env.runner = Mock()
        yield mock_env

@pytest.fixture
def sample_config():
    """示例配置"""
    return {
        "framework": {
            "name": "test_framework",
            "version": "1.0.0"
        },
        "load_shapes": {
            "test_shape": {
                "type": "linear",
                "config": {
                    "max_users": 100,
                    "duration": 300
                }
            }
        }
    }

@pytest.fixture
def mock_http_response():
    """模拟HTTP响应"""
    response = Mock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.json.return_value = {"status": "success"}
    response.text = '{"status": "success"}'
    response.content = b'{"status": "success"}'
    return response
```

## 🔍 调试配置

### 1. 日志配置

```python
# config/logging_dev.py
import logging
import sys
from pathlib import Path

def setup_development_logging():
    """设置开发环境日志"""

    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器
    file_handler = logging.FileHandler(log_dir / "locust_dev.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # 设置第三方库日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('gevent').setLevel(logging.WARNING)

    return root_logger

# 使用示例
if __name__ == "__main__":
    logger = setup_development_logging()
    logger.info("Development logging configured")
```

### 2. 性能分析配置

```python
# tools/profiling.py
import cProfile
import pstats
import io
from functools import wraps
from memory_profiler import profile as memory_profile
from line_profiler import LineProfiler

def cpu_profile(func):
    """CPU性能分析装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()

            # 输出分析结果
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.sort_stats('cumulative')
            ps.print_stats(20)  # 显示前20个函数

            print(f"\n=== CPU Profile for {func.__name__} ===")
            print(s.getvalue())

        return result
    return wrapper

def line_profile(func):
    """行级性能分析装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = LineProfiler()
        profiler.add_function(func)
        profiler.enable_by_count()

        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable_by_count()

            print(f"\n=== Line Profile for {func.__name__} ===")
            profiler.print_stats()

        return result
    return wrapper

# 使用示例
@cpu_profile
@memory_profile
def performance_test_function():
    """性能测试函数"""
    import time
    time.sleep(1)
    data = [i for i in range(100000)]
    return sum(data)
```

## 🛠️ 开发工具脚本

### 1. Makefile

```makefile
# Makefile
.PHONY: help install test lint format clean dev-setup

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean build artifacts"
	@echo "  dev-setup   Setup development environment"

install:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest tests/ -v --cov=src

test-fast:
	pytest tests/ -v -x --ff

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

dev-setup:
	python -m venv locust-dev
	./locust-dev/bin/pip install --upgrade pip
	./locust-dev/bin/pip install -r requirements-dev.txt
	./locust-dev/bin/pip install -e .
	./locust-dev/bin/pre-commit install

docker-dev:
	docker-compose -f docker-compose.dev.yml up -d

docker-test:
	docker-compose -f docker-compose.dev.yml exec locust-dev pytest

docker-clean:
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f
```

### 2. 开发脚本

```bash
#!/bin/bash
# scripts/dev-commands.sh

# 快速启动开发环境
dev_start() {
    echo "Starting development environment..."
    source locust-dev/bin/activate
    export PYTHONPATH=$(pwd)
    export LOCUST_HOST=http://localhost:8080
    echo "Development environment ready!"
}

# 运行代码质量检查
quality_check() {
    echo "Running code quality checks..."
    black --check src/ tests/
    isort --check-only src/ tests/
    flake8 src/ tests/
    mypy src/
    echo "Quality checks completed!"
}

# 运行完整测试套件
full_test() {
    echo "Running full test suite..."
    pytest tests/ -v --cov=src --cov-report=html
    echo "Tests completed! Check htmlcov/index.html for coverage report."
}

# 性能基准测试
benchmark() {
    echo "Running performance benchmarks..."
    python -m pytest tests/performance/ -v --benchmark-only
    echo "Benchmarks completed!"
}

# 根据参数执行相应命令
case "$1" in
    "start")
        dev_start
        ;;
    "check")
        quality_check
        ;;
    "test")
        full_test
        ;;
    "benchmark")
        benchmark
        ;;
    *)
        echo "Usage: $0 {start|check|test|benchmark}"
        exit 1
        ;;
esac
```

## 🎉 总结

开发环境配置包括：

1. **Python环境**: 虚拟环境、依赖管理
2. **IDE配置**: VS Code、PyCharm设置
3. **Docker环境**: 容器化开发
4. **测试配置**: pytest、覆盖率
5. **调试工具**: 日志、性能分析
6. **开发脚本**: 自动化工具

## 📚 相关文档

- [贡献指南](../development/contributing.md) - 代码贡献流程
- [测试指南](../development/testing.md) - 测试编写指南
- [生产环境配置](production.md) - 生产部署配置
- [故障排除](../examples/troubleshooting.md) - 开发问题排查
