

# 移除默认参数赋值
# 动态生成报告名和目录
timestamp := $(shell date +"%Y%m%d_%H%M%S")
report_dir := $(if $(script),logs/$(script)/user_$(u)_loop_num_$(loop_num)_$(timestamp),)
report_prefix := $(if $(report_dir),$(report_dir)/user_$(u)_loop_$(loop_num)_rdv_$(rendezvous_num)_$(timestamp),)

.PHONY: run clean stop

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
	@./stop_locust.sh  # 使用相对路径调用脚本
	@echo "所有 locust 进程已停止。"

clean:
	@rm -rf logs/*  # 清理所有日志目录下的文件
