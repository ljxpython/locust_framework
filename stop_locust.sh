#!/bin/bash

# 查找所有 Locust 进程的 PID
locust_pids=$(pgrep -f "locustfiles")

if [ -z "$locust_pids" ]; then
    echo "Locust process not found."
else
    # 将每个 PID 分开处理
    for locust_pid in $locust_pids; do
        echo "Sending SIGINT to Locust process with PID: $locust_pid"
        kill -SIGINT "$locust_pid"
    done

    # 可选: 等待进程结束
    sleep 2

    # 检查每个进程是否仍在运行
    for locust_pid in $locust_pids; do
        if ps -p "$locust_pid" > /dev/null; then
            echo "Locust process $locust_pid did not stop, forcing termination."
            kill -9 "$locust_pid"
        else
            echo "Locust process $locust_pid stopped successfully."
        fi
    done
fi