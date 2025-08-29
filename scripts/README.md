# 工具脚本说明

这个目录包含了Locust测试框架的实用工具脚本。

## 脚本列表

### 🚀 start_mock_server.py
启动Mock HTTP服务器，用于测试和开发。

**功能特点:**
- 自动检查依赖（Flask、Flask-CORS）
- 健康检查和服务启动验证
- 命令行参数配置主机和端口
- 优雅的错误处理和用户提示

**使用方法:**
```bash
# 使用默认配置启动
python scripts/start_mock_server.py

# 自定义主机和端口
python scripts/start_mock_server.py --host 0.0.0.0 --port 8080

# 通过Makefile启动
make mock-server
make mock-server-background  # 后台运行
```

**API端点:**
- `GET /health` - 健康检查
- `GET /api/products` - 商品列表
- `POST /api/auth/login` - 用户登录
- 更多端点请查看 `mock_server/app.py`

### 📋 run_examples.py
快速运行locustfiles/examples中的示例测试。

**功能特点:**
- 自动发现和列出所有可用示例
- 支持Web UI和无头模式
- 自动启动Mock服务器
- 灵活的参数配置

**使用方法:**
```bash
# 列出所有示例
python scripts/run_examples.py --list
make examples

# 运行指定示例（按编号）
python scripts/run_examples.py 1
make run-example example=1

# Web UI模式运行
python scripts/run_examples.py 1 --web
make run-example-web example=1

# 自定义测试参数
python scripts/run_examples.py 2 -u 20 -r 5 -t 120s
make run-example example=2 u=20 r=5 t=120s

# 按文件名部分匹配
python scripts/run_examples.py basic
```

**示例编号对照:**
1. `01_basic_test.py` - 基础HTTP测试
2. `02_custom_params.py` - 自定义参数和集合点
3. `03_data_driven.py` - 数据驱动测试
4. `04_performance_analysis.py` - 性能分析集成
5. `05_monitoring_alerts.py` - 监控和告警
6. `06_load_shapes.py` - 负载模式演示
7. `07_ecommerce_scenario.py` - 电商综合场景

### 🎲 generate_test_data.py
生成各种类型的测试数据。

**功能特点:**
- 支持多种数据类型（用户、商品、订单等）
- CSV和JSON输出格式
- 本地化支持（中文数据）
- Locust专用数据集生成

**使用方法:**
```bash
# 生成基础测试数据
python scripts/generate_test_data.py --type users --count 100 --format json
make test-data type=users count=100 format=json

# 生成Locust专用测试数据
python scripts/generate_test_data.py --type locust --count 500
make test-data-locust count=500

# 指定输出文件
python scripts/generate_test_data.py --type products --output data/products.csv

# 使用随机种子（可重现数据）
python scripts/generate_test_data.py --seed 12345
```

**支持的数据类型:**
- `users` - 用户资料数据
- `products` - 商品数据
- `orders` - 订单数据
- `mixed` - 混合类型数据
- `test_dataset` - 结构化测试数据集
- `locust` - Locust测试专用数据包

### 📊 analyze_results.py
分析Locust测试结果并生成报告。

**功能特点:**
- 自动解析Locust生成的CSV报告
- 计算性能指标和等级评分（A-F）
- 趋势分析和失败原因统计
- 智能化优化建议
- 多种输出格式

**使用方法:**
```bash
# 分析指定目录的结果
python scripts/analyze_results.py --results-dir reports
make analyze-results results_dir=reports

# 分析特定文件
python scripts/analyze_results.py --stats-file reports/stats.csv

# 不同输出格式
python scripts/analyze_results.py --format json    # 仅JSON文件
python scripts/analyze_results.py --format console # 仅控制台
python scripts/analyze_results.py --format both    # 默认，两种都输出

# 包含趋势分析
python scripts/analyze_results.py --with-trends --detailed
```

**报告内容:**
- 性能等级评分（A-F）
- 请求成功率和失败率
- 响应时间统计
- 主要失败原因
- 性能趋势分析
- 优化建议

## 快速开始工作流

### 方式一：使用Makefile命令
```bash
# 查看所有可用命令
make help

# 快速开始（推荐新用户）
make quick-start

# 完整测试流程
make full-test
```

### 方式二：手动步骤
```bash
# 1. 启动Mock服务器
python scripts/start_mock_server.py &

# 2. 生成测试数据（可选）
python scripts/generate_test_data.py --type locust --count 100

# 3. 运行示例测试
python scripts/run_examples.py 1 --web

# 4. 分析结果
python scripts/analyze_results.py --with-trends
```

## 集成到CI/CD

所有脚本都支持非交互式执行，适合集成到CI/CD管道：

```yaml
# GitHub Actions 示例
- name: Run Load Test
  run: |
    python scripts/start_mock_server.py &
    sleep 5
    python scripts/run_examples.py 7 -u 50 -r 10 -t 300s
    python scripts/analyze_results.py --format json
```

## 故障排除

### Mock服务器启动失败
- 检查端口是否被占用：`lsof -i :5000`
- 安装依赖：`pip install flask flask-cors`

### 示例运行失败
- 确保Mock服务器正在运行
- 检查Python环境和依赖
- 使用 `--skip-mock` 跳过服务器检查

### 数据生成问题
- 检查输出目录权限
- 确保有足够磁盘空间
- 验证locale设置

### 结果分析问题
- 确保CSV文件格式正确
- 检查文件路径是否存在
- 使用绝对路径避免路径问题

## 扩展开发

如需添加新的工具脚本：

1. 在scripts/目录创建新脚本
2. 添加执行权限：`chmod +x scripts/new_script.py`
3. 在Makefile中添加对应命令
4. 更新此README文档

脚本开发建议：
- 使用argparse处理命令行参数
- 提供清晰的帮助信息和错误提示
- 支持通过Makefile调用
- 遵循项目的错误处理模式
