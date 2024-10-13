import requests
import os
import signal
import subprocess
import time
import click

from loguru import logger

def stop_locust():
    # 假设 Locust 运行在 localhost:8089
    url = 'http://0.0.0.0:8089/stop'
    response = requests.post(url)

    if response.status_code == 200:
        logger.info("Locust is stopping...")
    else:
        logger.info("Failed to stop Locust:", response.text)




def get_locust_pids():
    """查找所有 Locust 进程的 PID"""
    try:
        # 使用 ps 查找进程
        command = "ps -ef | grep locustfiles | grep -v grep | awk '{print $2}'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logger.info(result.stdout)
        return result.stdout.splitlines()  # 返回 PID 列表
    except Exception as e:
        logger.error(f"Failed to find Locust processes: {e}")
        return []

@click.command()
def stop_locust_process():
    logger.info("find locust process")
    # 查找 Locust 进程
    locust_pids = get_locust_pids()
    logger.info(locust_pids)

    if not locust_pids:
        logger.warning("No Locust processes found.")
        return

    for pid in locust_pids:
        try:
            os.kill(int(pid), signal.SIGINT)  # 发送 SIGINT 信号
            logger.info(f"Locust process with PID {pid} has been stopped.")
        except ProcessLookupError:
            logger.error(f"Process with PID {pid} does not exist.")
        except Exception as e:
            logger.error(f"Failed to stop process with PID {pid}: {e}")

if __name__ == '__main__':
    stop_locust_process()
