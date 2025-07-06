# 开发环境搭建

本指南详细介绍如何搭建Locust性能测试框架的开发环境，包括环境准备、依赖安装、IDE配置等。

## 🎯 环境要求

### 系统要求

| 组件 | 最低版本 | 推荐版本 | 说明 |
|------|----------|----------|------|
| Python | 3.7+ | 3.9+ | 核心运行环境 |
| pip | 20.0+ | 最新版本 | 包管理工具 |
| Git | 2.20+ | 最新版本 | 版本控制 |
| 内存 | 4GB | 8GB+ | 开发和测试 |
| 磁盘 | 10GB | 20GB+ | 代码和依赖 |

### 操作系统支持

- ✅ **Linux** (Ubuntu 18.04+, CentOS 7+)
- ✅ **macOS** (10.14+)
- ✅ **Windows** (10+, WSL2推荐)

## 🔧 环境搭建步骤

### 步骤1：Python环境准备

#### 使用pyenv管理Python版本 (推荐)

```bash
# 安装pyenv (Linux/macOS)
curl https://pyenv.run | bash

# 或使用包管理器
# Ubuntu/Debian
sudo apt update && sudo apt install -y pyenv

# macOS
brew install pyenv

# 配置环境变量
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc

# 安装Python 3.9
pyenv install 3.9.16
pyenv global 3.9.16

# 验证安装
python --version
```

#### 直接安装Python

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv python3.9-dev

# CentOS/RHEL
sudo yum install python39 python39-pip python39-devel

# macOS (使用Homebrew)
brew install python@3.9

# Windows
# 从 https://python.org 下载安装包
```

### 步骤2：克隆项目代码

```bash
# 克隆项目
git clone https://github.com/your-org/locust-framework.git
cd locust-framework

# 查看项目结构
tree -L 2
```

### 步骤3：创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# 验证虚拟环境
which python
python --version
```

### 步骤4：安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装项目依赖
pip install -r requirements.txt

# 以开发模式安装项目
pip install -e .

# 验证安装
python -c "import locust; print(locust.__version__)"
```

### 步骤5：配置开发环境

#### 环境变量配置

```bash
# 创建环境配置文件
cp .env.example .env

# 编辑环境配置
vim .env
```

```bash
# .env 文件内容
LOCUST_ENV=development
PYTHONPATH=.
LOG_LEVEL=DEBUG
WEB_PORT=8089
```

#### Git配置

```bash
# 配置Git钩子
cp scripts/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# 配置Git用户信息
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## 🛠️ IDE配置

### VS Code配置

#### 安装扩展

```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.pylint",
        "ms-toolsai.jupyter",
        "redhat.vscode-yaml",
        "ms-vscode.test-adapter-converter"
    ]
}
```

#### 工作区配置

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    },
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### 调试配置

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Locust Web UI",
            "type": "python",
            "request": "launch",
            "module": "locust",
            "args": [
                "-f", "locustfiles/example_test.py",
                "--web-host", "0.0.0.0",
                "--web-port", "8089"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### PyCharm配置

#### 项目设置

1. **解释器配置**
   - File → Settings → Project → Python Interpreter
   - 选择虚拟环境中的Python解释器

2. **代码风格配置**
   - File → Settings → Editor → Code Style → Python
   - 导入配置文件：`setup.cfg`

3. **运行配置**
   ```python
   # 创建运行配置
   # Run → Edit Configurations → Add New → Python

   # Locust Web UI配置
   Script path: venv/bin/locust
   Parameters: -f locustfiles/example_test.py --web-host 0.0.0.0
   Working directory: /path/to/project
   Environment variables: PYTHONPATH=/path/to/project
   ```

## 🧪 开发工具配置

### 代码质量工具

#### Black (代码格式化)

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### isort (导入排序)

```toml
# pyproject.toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src", "locustfiles", "tests"]
```

#### flake8 (代码检查)

```ini
# setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    .venv,
    build,
    dist,
    *.egg-info
```

#### pylint (代码分析)

```ini
# .pylintrc
[MASTER]
init-hook='import sys; sys.path.append(".")'

[MESSAGES CONTROL]
disable=C0330,C0326,R0903,R0913

[FORMAT]
max-line-length=88
```

### 测试工具配置

#### pytest配置

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests"
]
```

#### coverage配置

```ini
# .coveragerc
[run]
source = src
omit =
    */tests/*
    */venv/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## 🔍 开发工作流

### 1. 日常开发流程

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 拉取最新代码
git pull origin main

# 3. 创建功能分支
git checkout -b feature/new-feature

# 4. 开发代码
# ... 编写代码 ...

# 5. 运行代码检查
make lint

# 6. 运行测试
make test

# 7. 提交代码
git add .
git commit -m "feat: add new feature"

# 8. 推送分支
git push origin feature/new-feature
```

### 2. 代码提交规范

```bash
# 提交消息格式
<type>(<scope>): <description>

# 类型说明
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动

# 示例
feat(analysis): add performance grading system
fix(monitoring): resolve memory leak in alert manager
docs(api): update monitoring API documentation
```

### 3. 代码审查清单

- [ ] 代码符合项目编码规范
- [ ] 添加了必要的单元测试
- [ ] 测试覆盖率达到要求
- [ ] 更新了相关文档
- [ ] 没有引入安全漏洞
- [ ] 性能影响可接受
- [ ] 向后兼容性良好

## 🚀 快速开始开发

### 创建第一个功能

```bash
# 1. 创建功能分支
git checkout -b feature/my-first-feature

# 2. 创建模块文件
mkdir -p src/my_module
touch src/my_module/__init__.py
touch src/my_module/my_feature.py

# 3. 编写代码
cat > src/my_module/my_feature.py << 'EOF'
"""我的第一个功能模块"""

def hello_world():
    """返回问候语"""
    return "Hello, Locust Framework!"
EOF

# 4. 创建测试文件
mkdir -p tests/my_module
touch tests/my_module/__init__.py
touch tests/my_module/test_my_feature.py

# 5. 编写测试
cat > tests/my_module/test_my_feature.py << 'EOF'
"""测试我的功能模块"""
import pytest
from src.my_module.my_feature import hello_world

def test_hello_world():
    """测试问候语功能"""
    result = hello_world()
    assert result == "Hello, Locust Framework!"
EOF

# 6. 运行测试
pytest tests/my_module/test_my_feature.py -v

# 7. 提交代码
git add .
git commit -m "feat: add hello world feature"
```

## 🔧 常用开发命令

### Makefile命令

```makefile
# Makefile
.PHONY: help install test lint format clean

help:  ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:  ## 安装依赖
	pip install -r requirements-dev.txt
	pip install -e .

test:  ## 运行测试
	pytest tests/ -v --cov=src

lint:  ## 代码检查
	flake8 src tests
	pylint src
	black --check src tests
	isort --check-only src tests

format:  ## 格式化代码
	black src tests
	isort src tests

clean:  ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
```

### 常用命令

```bash
# 安装依赖
make install

# 运行测试
make test

# 代码检查
make lint

# 格式化代码
make format

# 清理临时文件
make clean

# 启动开发服务器
locust -f locustfiles/example_test.py --web-host 0.0.0.0

# 运行特定测试
pytest tests/test_analysis.py::test_performance_analyzer -v

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html
```

## 🐛 故障排除

### 常见问题

1. **虚拟环境问题**
   ```bash
   # 重新创建虚拟环境
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

2. **依赖冲突**
   ```bash
   # 检查依赖冲突
   pip check

   # 重新安装依赖
   pip freeze > current_requirements.txt
   pip uninstall -r current_requirements.txt -y
   pip install -r requirements-dev.txt
   ```

3. **导入路径问题**
   ```bash
   # 设置PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"

   # 或在代码中添加
   import sys
   sys.path.insert(0, '.')
   ```

### 调试技巧

```python
# 使用pdb调试
import pdb; pdb.set_trace()

# 使用ipdb (更友好的调试器)
import ipdb; ipdb.set_trace()

# 使用logging调试
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("调试信息")
```

## 📚 参考资源

- [Python官方文档](https://docs.python.org/3/)
- [Locust官方文档](https://docs.locust.io/)
- [pytest文档](https://docs.pytest.org/)
- [Black代码格式化](https://black.readthedocs.io/)
- [项目贡献指南](contributing.md)

---

完成环境搭建后，您就可以开始参与框架开发了！建议先阅读[代码规范](coding-standards.md)和[插件开发指南](plugin-development.md)。
