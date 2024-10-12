import requests
import os
import signal
import time
import click

from src.utils.log_moudle import logger


def stop_locust():
    # 假设 Locust 运行在 localhost:8089
    url = 'http://0.0.0.0:8089/stop'
    response = requests.post(url)

    if response.status_code == 200:
        print("Locust is stopping...")
    else:
        print("Failed to stop Locust:", response.text)


@click.command()
@click.option('--pid', default=0, help='The process id of the locust process')
def stop_locust_process(pid):
    os.kill(pid, signal.SIGINT)  # 发送 SIGINT 信号
    logger.info(f"Locust process with PID {pid} has been stopped.")



if __name__ == '__main__':
    # stop_locust()
    stop_locust_process()




# 调用停止函数
# stop_locust()