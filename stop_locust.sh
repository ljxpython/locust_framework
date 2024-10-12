#!/bin/bash

# 查找 Locust 进程的 PID
locust_pid=$(pgrep -f "locustfiles")

if [ -z "$locust_pid" ]; then
    echo "Locust process not found."
else
    echo "Sending SIGINT to Locust process with PID: $locust_pid"
    kill -SIGINT "$locust_pid"

    # 可选: 等待进程结束
    sleep 2
    if ps -p "$locust_pid" > /dev/null; then
        echo "Locust process did not stop, forcing termination."
        kill -9 "$locust_pid"
    else
        echo "Locust process stopped successfully."
    fi
fi