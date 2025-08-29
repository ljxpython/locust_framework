

# 移除默认参数赋值
# 动态生成报告名和目录
timestamp := $(shell date +"%Y%m%d_%H%M%S")
report_dir := $(if $(script),logs/$(script)/user_$(u)_loop_num_$(loop_num)_$(timestamp),)
report_prefix := $(if $(report_dir),$(report_dir)/user_$(u)_loop_$(loop_num)_rdv_$(rendezvous_num)_$(timestamp),)

.PHONY: run clean stop mock-server examples test-data analyze-results help

define LOCUST_ARGS
$(if $(script),-f $(script),) --headless \
	$(if $(product_id),--product_id $(product_id),) \
	$(if $(loop_num),--loop_num $(loop_num),) \
	$(if $(rendezvous_num),--rendezvous_num $(rendezvous_num),) \
	$(if $(is_rendezvous),--is_rendezvous $(is_rendezvous),) \
	$(if $(report_prefix),--csv=$(report_prefix),) \
	$(if $(report_prefix),--html=$(report_prefix)_report.html,) \
	$(if $(u),-u $(u),) \
	$(if $(r),-r $(r),) \
	$(if $(t),-t $(t),) \
	$(if $(s),-s $(s),)
endef

run:
	@echo $(script)
	@echo $(report_prefix)
	@nohup locust $(LOCUST_ARGS) > $(report_prefix).log 2>&1 &
	@echo "Locust is running in the background. Log file: $(report_prefix).log"

run-web:
	@echo $(script)
	@echo $(report_prefix)
	@local_ip=$$(ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $$2}' | head -n 1) ;
	if [ -z "$$local_ip" ]; then \
		local_ip="0.0.0.0"; \
	fi ; \
	echo "Please visit http://$$local_ip:8089" ; \
	locust \
		$(if $(script),-f $(script),) \
		$(if $(product_id),--product_id $(product_id),) \
		$(if $(loop_num),--loop_num $(loop_num),) \
		$(if $(rendezvous_num),--rendezvous_num $(rendezvous_num),) \
		$(if $(is_rendezvous),--is_rendezvous $(is_rendezvous),) \
		$(if $(report_prefix),--csv=$(report_prefix),) \
		$(if $(report_prefix),--html=$(report_prefix)_report.html,) \
		$(if $(u),-u $(u),) \
		$(if $(r),-r $(r),) \
		$(if $(t),-t $(t),) \
		$(if $(s),-s $(s),) > test_web.log 2>&1 &
	@echo "Please visit http://0.0.0.0:8089"
	@echo "Locust web interface is running in the background. Log file: $(report_prefix)_web.log"

run-distributed-web:
	@echo $(script)
	@echo $(report_prefix)
	# 使用 ifconfig 命令获取内网 IP 地址，排除回环地址 127.0.0.1
	@local_ip=$$(ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $$2}' | head -n 1) ; \
	# 若未获取到 IP 地址，使用默认地址
	if [ -z "$$local_ip" ]; then \
		local_ip="0.0.0.0"; \
	fi ; \
	# 输出提示信息
	echo "Please visit http://$$local_ip:8089" ; \
	# 启动 locust 分布式 Web 界面
	nohup locust --master \
		$(if $(script),-f $(script),) \
		$(if $(product_id),--product_id $(product_id),) \
		$(if $(loop_num),--loop_num $(loop_num),) \
		$(if $(rendezvous_num),--rendezvous_num $(rendezvous_num),) \
		$(if $(is_rendezvous),--is_rendezvous $(is_rendezvous),) \
		$(if $(report_prefix),--csv=$(report_prefix),) \
		$(if $(report_prefix),--html=$(report_prefix)_report.html,) \
		$(if $(u),-u $(u),) \
		$(if $(r),-r $(r),) \
		$(if $(t),-t $(t),) \
		$(if $(s),-s $(s),) > $(report_prefix)_distributed_web.log 2>&1 &
	@echo "Locust distributed web interface is running in the background. Log file: $(report_prefix)_distributed_web.log"

stop:
	@echo "正在停止所有 locust 进程..."
	@pkill -f "locust" || echo "没有找到运行中的locust进程"
	@pkill -f "python.*mock_server" || echo "没有找到运行中的mock服务器"
	@echo "所有 locust 和 mock 服务器进程已停止。"

clean:
	@rm -rf logs/*  # 清理所有日志目录下的文件

# 新增工具命令

# Mock服务器管理
mock-server:
	@echo "🚀 启动Mock HTTP服务器..."
	@python scripts/start_mock_server.py

mock-server-background:
	@echo "🚀 后台启动Mock HTTP服务器..."
	@nohup python scripts/start_mock_server.py > logs/mock_server.log 2>&1 &
	@echo "Mock服务器已在后台启动，日志文件: logs/mock_server.log"

# 示例运行
examples:
	@echo "📋 列出所有可用示例:"
	@python scripts/run_examples.py --list

run-example:
	@echo "🧪 运行示例测试..."
	@python scripts/run_examples.py $(if $(example),$(example),1) $(if $(web),--web,) $(if $(u),-u $(u),) $(if $(r),-r $(r),) $(if $(t),-t $(t),)

run-example-web:
	@echo "🌐 Web UI模式运行示例..."
	@python scripts/run_examples.py $(if $(example),$(example),1) --web

# 测试数据生成
test-data:
	@echo "🎲 生成测试数据..."
	@python scripts/generate_test_data.py $(if $(type),--type $(type),) $(if $(count),--count $(count),) $(if $(format),--format $(format),)

test-data-locust:
	@echo "🎯 生成Locust专用测试数据..."
	@python scripts/generate_test_data.py --type locust $(if $(count),--count $(count),)

# 结果分析
analyze-results:
	@echo "📊 分析测试结果..."
	@python scripts/analyze_results.py $(if $(results_dir),--results-dir $(results_dir),) $(if $(format),--format $(format),) --with-trends

# 快速开始命令
quick-start:
	@echo "🚀 快速开始 - 启动Mock服务器和基础示例"
	@echo "1. 启动Mock服务器..."
	@python scripts/start_mock_server.py &
	@sleep 3
	@echo "2. 运行基础示例..."
	@python scripts/run_examples.py 1 --web

# 完整测试流程
full-test:
	@echo "🔄 完整测试流程..."
	@echo "1. 生成测试数据..."
	@python scripts/generate_test_data.py --type locust --count 100
	@echo "2. 启动Mock服务器..."
	@python scripts/start_mock_server.py &
	@sleep 3
	@echo "3. 运行综合场景测试..."
	@python scripts/run_examples.py 7 -u 10 -r 2 -t 30s
	@echo "4. 分析结果..."
	@python scripts/analyze_results.py --format both

# 帮助信息
help:
	@echo "🔧 Locust框架 - 可用命令:"
	@echo ""
	@echo "📊 基础测试命令:"
	@echo "  make run script=<file> u=<users> r=<spawn_rate> t=<time>  - 无头模式运行测试"
	@echo "  make run-web script=<file>                               - Web UI模式运行测试"
	@echo "  make run-distributed-web script=<file>                   - 分布式主节点模式"
	@echo "  make stop                                               - 停止所有locust进程"
	@echo "  make clean                                              - 清理日志文件"
	@echo ""
	@echo "🛠️  工具命令:"
	@echo "  make mock-server                                        - 启动Mock HTTP服务器"
	@echo "  make mock-server-background                             - 后台启动Mock服务器"
	@echo "  make examples                                           - 列出所有示例"
	@echo "  make run-example example=<number>                      - 运行指定示例"
	@echo "  make run-example-web example=<number>                  - Web UI运行示例"
	@echo "  make test-data type=<type> count=<num>                 - 生成测试数据"
	@echo "  make test-data-locust count=<num>                      - 生成Locust测试数据"
	@echo "  make analyze-results results_dir=<dir>                 - 分析测试结果"
	@echo ""
	@echo "🚀 快速命令:"
	@echo "  make quick-start                                        - 快速开始 (Mock服务器 + 基础示例)"
	@echo "  make full-test                                          - 完整测试流程"
	@echo "  make help                                               - 显示此帮助信息"
	@echo ""
	@echo "📝 示例参数:"
	@echo "  make run script=locustfiles/examples/01_basic_test.py u=10 r=2 t=60s"
	@echo "  make run-example example=1 u=20 r=5 t=120s"
	@echo "  make test-data type=users count=500 format=json"
