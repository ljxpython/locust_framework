from subprocess import PIPE, STDOUT, Popen


def run_test():
    # cmd = ["locust", "-f", "locustfiles", "--host=http://localhost:8000"]
    cmd = f"/Users/xxxx/PycharmProjects/my_best/locust_framework/.venv/bin/locust -f locustfiles -t 10"
    process = Popen(cmd, shell=True)
    # stdout, _ = process.communicate()

    # print(stdout.decode())
    process.wait()
    if process.returncode != 0:
        print("Error occurred:", process.returncode)

    return process.returncode


if __name__ == "__main__":
    run_test()
