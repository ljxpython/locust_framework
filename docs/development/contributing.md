# 贡献指南

欢迎为Locust性能测试框架做出贡献！本指南将帮助您了解如何参与项目开发，提交代码和改进建议。

## 🎯 贡献方式

### 代码贡献
- 修复Bug
- 添加新功能
- 性能优化
- 代码重构

### 文档贡献
- 改进文档内容
- 添加使用示例
- 翻译文档
- 修正错误

### 测试贡献
- 编写单元测试
- 添加集成测试
- 性能测试
- 兼容性测试

### 社区贡献
- 回答问题
- 分享经验
- 提供反馈
- 推广项目

## 🚀 开发环境搭建

### 1. 克隆项目

```bash
# 克隆主仓库
git clone https://github.com/your-org/locust-framework.git
cd locust-framework

# 添加上游仓库（如果是fork）
git remote add upstream https://github.com/original-org/locust-framework.git
```

### 2. 环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install
```

### 3. 开发依赖说明

```txt
# requirements-dev.txt
# 基础依赖
locust>=2.0.0
requests>=2.25.0
gevent>=21.0.0

# 开发工具
pytest>=6.0.0
pytest-cov>=2.10.0
pytest-mock>=3.5.0
black>=21.0.0
flake8>=3.8.0
mypy>=0.800
isort>=5.0.0

# 文档工具
sphinx>=4.0.0
sphinx-rtd-theme>=0.5.0
myst-parser>=0.15.0

# 构建工具
build>=0.7.0
twine>=3.4.0

# 测试工具
factory-boy>=3.2.0
faker>=8.0.0
responses>=0.13.0
```

### 4. 开发配置

```python
# setup.cfg
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --strict-markers
    --disable-warnings

[coverage:run]
source = src
omit =
    */tests/*
    */venv/*
    setup.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    venv,
    .venv,
    build,
    dist

[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

## 📝 开发流程

### 1. 分支管理

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 创建修复分支
git checkout -b fix/issue-number-description

# 创建文档分支
git checkout -b docs/documentation-improvement
```

### 2. 代码规范

#### Python代码风格

```python
# 使用Black格式化代码
black src/ tests/

# 使用isort整理导入
isort src/ tests/

# 使用flake8检查代码质量
flake8 src/ tests/

# 使用mypy进行类型检查
mypy src/
```

#### 代码示例

```python
# 好的代码示例
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class LoadShapeManager:
    """负载模式管理器

    管理和创建各种负载模式实例。

    Attributes:
        _shapes: 注册的负载模式字典
        _instances: 创建的实例缓存
    """

    def __init__(self) -> None:
        self._shapes: Dict[str, type] = {}
        self._instances: Dict[str, object] = {}

    def register_shape(self, name: str, shape_class: type) -> None:
        """注册负载模式

        Args:
            name: 负载模式名称
            shape_class: 负载模式类

        Raises:
            ValueError: 当名称已存在时
        """
        if name in self._shapes:
            raise ValueError(f"Shape '{name}' already registered")

        self._shapes[name] = shape_class
        logger.info(f"Registered load shape: {name}")

    def create_shape(self, name: str, **kwargs) -> Optional[object]:
        """创建负载模式实例

        Args:
            name: 负载模式名称
            **kwargs: 初始化参数

        Returns:
            负载模式实例，如果不存在则返回None
        """
        if name not in self._shapes:
            logger.error(f"Unknown load shape: {name}")
            return None

        try:
            instance = self._shapes[name](**kwargs)
            self._instances[name] = instance
            return instance
        except Exception as e:
            logger.error(f"Failed to create shape '{name}': {e}")
            return None
```

### 3. 提交规范

#### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 提交类型

- `feat`: 新功能
- `fix`: 修复Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 提交示例

```bash
# 功能提交
git commit -m "feat(load-shapes): add adaptive load shape

- Implement adaptive load shape based on response time
- Add configuration options for target response time
- Include automatic scaling based on performance metrics

Closes #123"

# 修复提交
git commit -m "fix(plugins): resolve plugin loading issue

- Fix plugin discovery mechanism
- Handle missing plugin dependencies gracefully
- Add better error messages for plugin failures

Fixes #456"

# 文档提交
git commit -m "docs(api): update plugin development guide

- Add comprehensive examples for custom plugins
- Include troubleshooting section
- Fix formatting issues in code blocks"
```

## 🧪 测试指南

### 1. 测试结构

```
tests/
├── unit/                 # 单元测试
│   ├── test_load_shapes.py
│   ├── test_plugins.py
│   └── test_utilities.py
├── integration/          # 集成测试
│   ├── test_framework.py
│   └── test_distributed.py
├── performance/          # 性能测试
│   └── test_benchmarks.py
├── fixtures/            # 测试数据
│   ├── sample_data.json
│   └── test_configs.yaml
└── conftest.py          # pytest配置
```

### 2. 编写测试

#### 单元测试示例

```python
# tests/unit/test_load_shapes.py
import pytest
from unittest.mock import patch, MagicMock
from src.model.load_shapes.linear_shape import LinearLoadShape

class TestLinearLoadShape:
    """线性负载模式测试"""

    def setup_method(self):
        """测试初始化"""
        self.shape = LinearLoadShape(max_users=100, duration=300, spawn_rate=10)

    def test_initialization(self):
        """测试初始化"""
        assert self.shape.max_users == 100
        assert self.shape.duration == 300
        assert self.shape.spawn_rate == 10
        assert self.shape.start_time is None

    def test_tick_initial_call(self):
        """测试首次调用tick"""
        with patch('time.time', return_value=1000):
            result = self.shape.tick()
            assert result is not None
            users, spawn_rate = result
            assert users > 0
            assert spawn_rate == 10
            assert self.shape.start_time == 1000

    def test_tick_progression(self):
        """测试负载进展"""
        with patch('time.time') as mock_time:
            # 初始化
            mock_time.return_value = 1000
            self.shape.tick()

            # 50%进度
            mock_time.return_value = 1150  # 150秒后
            users, spawn_rate = self.shape.tick()
            expected_users = int(100 * 0.5)  # 50%进度
            assert abs(users - expected_users) <= 1  # 允许小误差

    def test_tick_completion(self):
        """测试完成条件"""
        with patch('time.time') as mock_time:
            # 初始化
            mock_time.return_value = 1000
            self.shape.tick()

            # 超过持续时间
            mock_time.return_value = 1301  # 301秒后
            result = self.shape.tick()
            assert result is None

    @pytest.mark.parametrize("max_users,duration,expected_rate", [
        (50, 100, 0.5),
        (200, 400, 0.5),
        (1000, 600, 1.67)
    ])
    def test_different_configurations(self, max_users, duration, expected_rate):
        """测试不同配置"""
        shape = LinearLoadShape(max_users=max_users, duration=duration)
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000
            shape.tick()

            # 测试中间点
            mock_time.return_value = 1000 + duration // 2
            users, _ = shape.tick()
            expected_users = max_users // 2
            assert abs(users - expected_users) <= 2
```

#### 集成测试示例

```python
# tests/integration/test_framework.py
import pytest
import tempfile
import os
from src.core.framework import LocustFramework

class TestFrameworkIntegration:
    """框架集成测试"""

    def setup_method(self):
        """测试初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")

        # 创建测试配置
        config_content = """
        framework:
          name: "test_framework"
          version: "1.0.0"

        load_shapes:
          test_shape:
            type: "linear"
            config:
              max_users: 10
              duration: 60
              spawn_rate: 2

        plugins:
          - name: "test_plugin"
            enabled: true
        """

        with open(self.config_file, 'w') as f:
            f.write(config_content)

    def teardown_method(self):
        """测试清理"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_framework_initialization(self):
        """测试框架初始化"""
        framework = LocustFramework(config_file=self.config_file)
        assert framework.config is not None
        assert framework.config['framework']['name'] == "test_framework"

    def test_load_shape_creation(self):
        """测试负载模式创建"""
        framework = LocustFramework(config_file=self.config_file)
        shape = framework.create_load_shape("test_shape")
        assert shape is not None
        assert hasattr(shape, 'tick')

    def test_plugin_loading(self):
        """测试插件加载"""
        framework = LocustFramework(config_file=self.config_file)
        plugins = framework.load_plugins()
        assert len(plugins) > 0
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_load_shapes.py

# 运行特定测试类
pytest tests/unit/test_load_shapes.py::TestLinearLoadShape

# 运行特定测试方法
pytest tests/unit/test_load_shapes.py::TestLinearLoadShape::test_initialization

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行性能测试
pytest tests/performance/ -v
```

## 📚 文档贡献

### 1. 文档结构

```
docs/
├── getting-started/     # 入门指南
├── architecture/        # 架构文档
├── api/                # API文档
├── development/        # 开发指南
├── examples/           # 示例和最佳实践
├── configuration/      # 配置说明
└── README.md          # 主文档
```

### 2. 文档编写规范

#### Markdown格式

```markdown
# 标题使用H1
## 主要章节使用H2
### 子章节使用H3

**重要内容使用粗体**
*强调内容使用斜体*
`代码片段使用反引号`

```python
# 代码块使用三个反引号并指定语言
def example_function():
    return "Hello, World!"
```

> 引用使用大于号

- 列表项1
- 列表项2
  - 嵌套列表项

1. 有序列表项1
2. 有序列表项2

[链接文本](相对路径或URL)

![图片描述](图片路径)
```

#### 代码文档

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """函数简短描述

    详细描述函数的功能和用途。可以包含多行说明，
    解释函数的工作原理和使用场景。

    Args:
        param1: 参数1的描述
        param2: 参数2的描述，默认值为0

    Returns:
        返回值的描述

    Raises:
        ValueError: 当参数无效时抛出
        TypeError: 当参数类型错误时抛出

    Example:
        >>> result = example_function("test", 5)
        >>> print(result)
        True

    Note:
        这里可以添加额外的注意事项或说明
    """
    if not isinstance(param1, str):
        raise TypeError("param1 must be a string")

    if param2 < 0:
        raise ValueError("param2 must be non-negative")

    return len(param1) > param2
```

### 3. 文档构建

```bash
# 安装文档依赖
pip install -r docs/requirements.txt

# 构建HTML文档
cd docs
make html

# 实时预览（如果使用sphinx-autobuild）
sphinx-autobuild source build/html
```

## 🔄 Pull Request流程

### 1. 准备工作

```bash
# 确保代码是最新的
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/your-feature

# 进行开发...

# 运行测试
pytest
black src/ tests/
flake8 src/ tests/
mypy src/
```

### 2. 提交PR

1. **推送分支**
```bash
git push origin feature/your-feature
```

2. **创建Pull Request**
- 访问GitHub仓库
- 点击"New Pull Request"
- 选择源分支和目标分支
- 填写PR模板

3. **PR模板**
```markdown
## 变更描述
简要描述这个PR的目的和变更内容。

## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能优化
- [ ] 代码重构

## 测试
- [ ] 添加了新的测试
- [ ] 所有测试通过
- [ ] 手动测试完成

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 提交消息符合规范
- [ ] 文档已更新
- [ ] 变更日志已更新

## 相关Issue
Closes #123
Related to #456

## 截图（如适用）
如果有UI变更，请提供截图。
```

### 3. 代码审查

#### 审查要点
- 代码质量和可读性
- 测试覆盖率
- 性能影响
- 安全考虑
- 文档完整性

#### 响应反馈
```bash
# 根据反馈修改代码
git add .
git commit -m "address review comments"
git push origin feature/your-feature
```

## 🎉 发布流程

### 1. 版本管理

```bash
# 更新版本号
# 在setup.py或__init__.py中更新版本

# 更新变更日志
# 在CHANGELOG.md中记录变更

# 创建发布标签
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

### 2. 自动化发布

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## 🤝 社区参与

### 1. 沟通渠道
- GitHub Issues: 报告Bug和功能请求
- GitHub Discussions: 技术讨论和问答
- Slack/Discord: 实时交流
- 邮件列表: 重要公告

### 2. 行为准则
- 尊重他人
- 建设性反馈
- 包容性环境
- 专业态度

### 3. 获得帮助
- 查看文档
- 搜索已有Issue
- 提问时提供详细信息
- 参与社区讨论

## 📚 相关资源

- [开发环境配置](../getting-started/installation.md)
- [API文档](../api/README.md)
- [测试指南](testing.md)
- [代码规范](documentation-standards.md)

感谢您的贡献！🎉
