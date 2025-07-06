# 安装指南

本指南将帮助您在不同环境中安装和配置Locust性能测试框架。

## 系统要求

### 最低要求
- **Python**: 3.7 或更高版本
- **内存**: 最少 2GB RAM
- **磁盘空间**: 最少 1GB 可用空间
- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+, CentOS 7+)

### 推荐配置
- **Python**: 3.9 或更高版本
- **内存**: 8GB RAM 或更多
- **磁盘空间**: 5GB 可用空间
- **CPU**: 多核处理器（用于分布式测试）

## 安装方式

### 方式一：使用pip安装（推荐）

```bash
# 创建虚拟环境（推荐）
python -m venv locust_env
source locust_env/bin/activate  # Linux/macOS
# 或
locust_env\Scripts\activate     # Windows

# 安装核心依赖
pip install locust>=2.0.0
pip install dynaconf>=3.1.0
pip install peewee>=3.14.0
pip install loguru>=0.6.0
pip install faker>=15.0.0
pip install jinja2>=3.0.0
pip install requests>=2.28.0
pip install psutil>=5.8.0

# 安装可选依赖
pip install pandas>=1.3.0        # 数据分析功能
pip install matplotlib>=3.5.0    # 图表生成
pip install seaborn>=0.11.0      # 高级图表
pip install openpyxl>=3.0.0      # Excel支持
```

### 方式二：从源码安装

```bash
# 克隆项目
git clone https://github.com/your-repo/locust_framework.git
cd locust_framework

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 方式三：使用Docker

```bash
# 拉取镜像
docker pull locust-framework:latest

# 运行容器
docker run -it --rm \
  -p 8089:8089 \
  -v $(pwd):/workspace \
  locust-framework:latest
```

## 依赖说明

### 核心依赖
```
locust>=2.0.0           # 核心测试引擎
dynaconf>=3.1.0         # 配置管理
peewee>=3.14.0          # 数据库ORM
loguru>=0.6.0           # 日志管理
faker>=15.0.0           # 测试数据生成
jinja2>=3.0.0           # 模板引擎
requests>=2.28.0        # HTTP客户端
psutil>=5.8.0           # 系统监控
```

### 可选依赖
```
pandas>=1.3.0           # 数据分析
matplotlib>=3.5.0       # 基础图表
seaborn>=0.11.0         # 高级图表
openpyxl>=3.0.0         # Excel文件支持
redis>=4.0.0            # Redis缓存
pymongo>=4.0.0          # MongoDB支持
mysql-connector-python>=8.0.0  # MySQL支持
psycopg2-binary>=2.9.0  # PostgreSQL支持
```

## 环境配置

### 1. 创建配置文件

```bash
# 复制配置模板
cp plugin_config.template.json plugin_config.json
cp conf/settings.toml.example conf/settings.toml
```

### 2. 配置环境变量

```bash
# Linux/macOS
export LOCUST_ENV=development
export LOCUST_CONFIG_PATH=./conf

# Windows
set LOCUST_ENV=development
set LOCUST_CONFIG_PATH=./conf
```

### 3. 初始化数据库（可选）

```bash
# 创建数据库表
python -c "
from src.utils.database import init_database
init_database()
"
```

## 验证安装

### 1. 检查Python版本
```bash
python --version
# 应该显示 Python 3.7+ 版本
```

### 2. 检查依赖安装
```bash
python -c "
import locust
import dynaconf
import peewee
import loguru
import faker
print('所有核心依赖安装成功！')
"
```

### 3. 运行测试示例
```bash
# 运行框架功能演示
python examples/enhanced_framework_demo.py

# 启动Locust Web界面
locust -f examples/basic_test.py --host=http://localhost:8080
```

### 4. 检查插件系统
```bash
python -c "
from src.plugins.plugin_manager import PluginManager
pm = PluginManager()
print(f'发现插件: {pm.get_available_plugins()}')
"
```

## 常见问题

### Q1: 安装时出现权限错误
```bash
# 解决方案：使用用户安装
pip install --user locust

# 或者使用虚拟环境
python -m venv locust_env
source locust_env/bin/activate
pip install locust
```

### Q2: 依赖版本冲突
```bash
# 解决方案：创建干净的虚拟环境
python -m venv fresh_env
source fresh_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Q3: Windows下安装失败
```bash
# 可能需要安装Visual C++ Build Tools
# 下载并安装：https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 或者使用预编译包
pip install --only-binary=all locust
```

### Q4: macOS下SSL证书问题
```bash
# 更新证书
/Applications/Python\ 3.x/Install\ Certificates.command

# 或者使用conda
conda install -c conda-forge locust
```

## 开发环境配置

### 1. 安装开发工具
```bash
pip install pytest>=6.0.0
pip install pytest-cov>=3.0.0
pip install black>=22.0.0
pip install flake8>=4.0.0
pip install mypy>=0.950
pip install pre-commit>=2.15.0
```

### 2. 配置代码格式化
```bash
# 安装pre-commit钩子
pre-commit install

# 手动运行格式化
black src/ tests/
flake8 src/ tests/
```

### 3. 运行测试
```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行特定测试
pytest tests/test_analysis.py
```

## 生产环境部署

### 1. 系统优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化网络参数
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
sysctl -p
```

### 2. 服务配置
```bash
# 创建systemd服务文件
sudo tee /etc/systemd/system/locust.service > /dev/null <<EOF
[Unit]
Description=Locust Performance Testing Framework
After=network.target

[Service]
Type=simple
User=locust
WorkingDirectory=/opt/locust_framework
ExecStart=/opt/locust_framework/venv/bin/python -m locust -f main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl enable locust
sudo systemctl start locust
```

### 3. 监控配置
```bash
# 配置日志轮转
sudo tee /etc/logrotate.d/locust > /dev/null <<EOF
/var/log/locust/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 locust locust
}
EOF
```

## 下一步

安装完成后，您可以：

1. [快速入门](quickstart.md) - 学习基础使用方法
2. [基础概念](concepts.md) - 了解核心概念
3. [第一个测试](first-test.md) - 创建您的第一个测试
4. [配置指南](../configuration/framework-config.md) - 详细配置说明

## 获取帮助

如果在安装过程中遇到问题：

- 查看 [故障排除指南](../examples/troubleshooting.md)
- 提交 [GitHub Issue](https://github.com/your-repo/issues)
- 发送邮件至 support@example.com
