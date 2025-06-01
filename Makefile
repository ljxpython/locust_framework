# 默认参数
product_id ?= 0
loop_num ?= 1
rendezvous_num ?= 0
is_rendezvous ?= false
script ?= locustfile.py
u ?= 1000
r ?= 100
t ?= 5m
s ?= 100
power_on_off_pod ?= pod_name  # 替换为实际值

# 动态生成报告名和目录
timestamp := $(shell date +"%Y%m%d_%H%M%S")
report_dir := logs/$(script)/user_$(u)_loop_num_$(loop_num)_$(timestamp)
report_prefix := $(report_dir)/user_$(u)_loop_$(loop_num)_rdv_$(rendezvous_num)_$(timestamp)

.PHONY: run clean

run:
	@echo $(script)
	@echo $(report_prefix)
	locust -f $(script) --headless \
		--product_id $(product_id) \
		--loop_num $(loop_num) \
		--rendezvous_num $(rendezvous_num) \
		--is_rendezvous $(is_rendezvous) \
		--csv=$(report_prefix) \
		--html=$(report_prefix)_report.html \
		-u $(u) -r $(r) -t $(t) -s $(s)

run-web:
	@echo $(script)
	@echo $(report_prefix)
	@locust -f $(script) \
		--product_id $(product_id) \
		--loop_num $(loop_num) \
		--rendezvous_num $(rendezvous_num) \
		--is_rendezvous $(is_rendezvous) \
		--csv=$(report_prefix) \
		--html=$(report_prefix)_report.html \
		-u $(u) -r $(r) -t $(t) -s $(s)

run-distributed-web:
	@echo $(script)
	@echo $(report_prefix)
	@locust -f $(script) --master \
		--product_id $(product_id) \
		--loop_num $(loop_num) \
		--rendezvous_num $(rendezvous_num) \
		--is_rendezvous $(is_rendezvous) \
		--csv=$(report_prefix) \
		--html=$(report_prefix)_report.html \
		-u $(u) -r $(r) -t $(t) -s $(s)

clean:
	@rm -rf logs/*  # 清理所有日志目录下的文件
