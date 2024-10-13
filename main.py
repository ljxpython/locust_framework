from subprocess import PIPE, STDOUT, Popen
import click
import os
import sys
import signal
import time
from pathlib import Path
from functools import partial

from conf.config import settings
from src.utils.log_moudle import logger
from src.model.locust_test import LocustTestResult
from src.model.modelsbase import database
from src.utils.file_operation import file_opreator

def on_exit(signo=None, frame=None, service_id=None,report_dir=None,title=None):
    '''
    停止压测脚本后,将测试报告打包,修改locusttestresult的相关状态
    '''
    logger.info(f"locust 任务 {service_id} 已经停止,正在生成测试报告")
    # 连接数据库
    time.sleep(5)
    database.connect()
    result = LocustTestResult.get(LocustTestResult.id == service_id)
    result.status = 1
    result.result = "Done"
    static_dir = settings.nginx.locust_static_dir
    nginx_url = settings.nginx.static_url
    logger.info(static_dir)
    logger.info(nginx_url)
    logger.info(f"{report_dir}/{title}/{title}.html")
    report_link = f"{report_dir}/{title}/{title}.html".replace(static_dir, nginx_url)
    result.report_link = report_link
    # 打包压测相关产物
    file_opreator.tar_packge(
        output_filename=f"{report_dir}/{title}.tar.gz",
        source_dir=f"{report_dir}/{title}/"
    )
    download_file =f"{report_dir}/{title}.tar.gz".replace(static_dir,nginx_url)
    result.report_download = download_file
    result.save()
    logger.info(f"locust 任务 {service_id} 压测报告已经生成,报告地址为{result.report_link}")
    # 关闭数据库连接
    if not database.is_closed():
        database.close()
    sys.exit(0)



@click.command()
@click.option('--id', help='The id of the test')
@click.option('--title', help='The title of the test')
@click.option('--report_dir', help='The directory to save the report')
@click.option('--case_ids', help='The case ids to be executed')
@click.option('--port', type=int,default=8090, help='The port of the locust web UI')
@click.option('--users', default=1, help='The number of users to simulate')
@click.option('--spawn-rate', default=1, help='The rate at which users are spawned')
@click.option('--run-time', default=60, help='The duration of the test in seconds')
@click.option('--headless', is_flag=True, help='Run the test in headless mode')
@click.option('--tags', help='The tags of the test')
@click.option('--exclude_tags', help='The tags of the test to be excluded')
def run_test(id,title,report_dir,case_ids:str=None,port:int=8090,users:int=None,spawn_rate:float=None,run_time:str=None,headless:bool=True,tags:str=None,exclude_tags:str=None):
    '''
    Run the locust test with the given parameters.
    CSV文件及HTML,LOG文件名方式,
    放在title的文件夹下以title.html,titile.csv,title.log来进行命名
    '''
    signal.signal(signal.SIGINT, partial(on_exit, service_id=id,title=title,report_dir=report_dir))
    signal.signal(signal.SIGTERM, partial(on_exit, service_id=id,title=title,report_dir=report_dir))
    # 如果report_dir不存在,则创建
    logger.info(f"report: {os.path.join(report_dir, title)}")
    # if not os.path.exists(os.path.join(report_dir, title)):
    #     os.makedirs(report_dir)
    cmd = f"{settings.locust_stress.locust_env} -f  {case_ids}  --html {report_dir}/{title}/{title}.html --csv {report_dir}/{title}/{title}.csv --csv-full-history  --web-port {port} --class-picker  "
    if users:
        cmd += f"--users {users} "
    if spawn_rate:
        cmd += f"--spawn-rate {spawn_rate} "
    if run_time:
        cmd += f"--run-time {run_time} "
    if headless:
        cmd += "--headless "
    if tags:
        cmd += f"--tags {tags} "
    if exclude_tags:
        cmd += f"--exclude-tags {exclude_tags} "
    logger.info(f"Running command: {cmd}")

    process = Popen(cmd, shell=True)
    stdout, _ = process.communicate()

    if process.returncode != 0:
        logger.info("Error occurred:", process.returncode)
    logger.info(f"Test finished with return code: {process.returncode}")
    logger.info(f"locust is end,report: {report_dir}/{title}.html")
    on_exit(service_id=id,title=title,report_dir=report_dir)

    return process.returncode


if __name__ == "__main__":
    run_test()
