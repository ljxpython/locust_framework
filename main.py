from subprocess import PIPE, STDOUT, Popen
import click
import os
import signal
import time

from conf.config import settings
from src.utils.log_moudle import logger

@click.command()
@click.option('--title', help='The title of the test')
@click.option('--report_dir', help='The directory to save the report')
@click.option('--case_ids', help='The case ids to be executed')
@click.option('--port', type=int,default=8090, help='The port of the locust web UI')
@click.option('--users', default=1, help='The number of users to simulate')
@click.option('--spawn-rate', default=1, help='The rate at which users are spawned')
@click.option('--run-time', default=60, help='The duration of the test in seconds')
def run_test(title,report_dir,case_ids:str=None,port:int=8090,users:int=None,spawn_rate:float=None,run_time:str=None):
    '''
    Run the locust test with the given parameters.
    CSV文件及HTML,LOG文件名方式,
    放在title的文件夹下以title.html,titile.csv,title.log来进行命名
    '''
    cmd = f"{settings.locust_stress.locust_env} -f  {case_ids}  --html {report_dir}/{title}.html --csv {report_dir}/{title}.csv --csv-full-history --logfile {report_dir}/{title}.log --port {port} "
    if users:
        cmd += f"--users {users} "
    if spawn_rate:
        cmd += f"--spawn-rate {spawn_rate} "
    if run_time:
        cmd += f"--run-time {run_time} "
    logger.info(f"Running command: {cmd}")

    process = Popen(cmd, shell=True)
    stdout, _ = process.communicate()

    process.wait()
    if process.returncode != 0:
        logger.info("Error occurred:", process.returncode)
    logger.info(f"Test finished with return code: {process.returncode}")

    return process.returncode


if __name__ == "__main__":
    run_test()
