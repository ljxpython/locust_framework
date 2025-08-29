#!/usr/bin/env python3
"""
运行示例脚本

用于快速运行locustfiles/examples中的示例测试
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

import requests


def check_mock_server(host="localhost", port=5000):
    """检查Mock服务器是否运行"""
    try:
        response = requests.get(f"http://{host}:{port}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def start_mock_server_if_needed(host="localhost", port=5000):
    """如果需要启动Mock服务器"""
    if check_mock_server(host, port):
        print(f"✅ Mock服务器已在运行: http://{host}:{port}")
        return True

    print("🚀 启动Mock服务器...")
    script_dir = Path(__file__).parent
    start_server_script = script_dir / "start_mock_server.py"

    try:
        # 启动服务器（后台运行）
        subprocess.Popen(
            [
                sys.executable,
                str(start_server_script),
                "--host",
                host,
                "--port",
                str(port),
            ]
        )

        # 等待服务器启动
        for i in range(30):
            if check_mock_server(host, port):
                print(f"✅ Mock服务器启动成功: http://{host}:{port}")
                return True
            time.sleep(1)

        print("❌ Mock服务器启动超时")
        return False
    except Exception as e:
        print(f"❌ 启动Mock服务器失败: {e}")
        return False


def get_available_examples():
    """获取可用的示例列表"""
    script_dir = Path(__file__).parent.parent
    examples_dir = script_dir / "locustfiles" / "examples"

    if not examples_dir.exists():
        return []

    examples = []
    for py_file in examples_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
        examples.append(py_file)

    return sorted(examples)


def run_example(
    example_file,
    web_ui=False,
    users=10,
    spawn_rate=2,
    run_time="60s",
    host="localhost",
    port=8089,
):
    """运行指定示例"""
    print(f"🎯 运行示例: {example_file.name}")
    print(f"   文件路径: {example_file}")

    cmd = [
        "locust",
        "-f",
        str(example_file),
        "--host",
        f"http://localhost:5000",  # Mock服务器地址
    ]

    if web_ui:
        cmd.extend(["--web-host", host, "--web-port", str(port)])
        print(f"🌐 Web UI地址: http://{host}:{port}")
        print("💡 在浏览器中打开上述地址开始测试")
        print("   按Ctrl+C停止")
    else:
        cmd.extend(
            ["--headless", "-u", str(users), "-r", str(spawn_rate), "-t", run_time]
        )
        print(f"🏃 无头模式运行:")
        print(f"   用户数: {users}")
        print(f"   启动速率: {spawn_rate} users/s")
        print(f"   运行时间: {run_time}")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行Locust示例测试")

    # 示例选择
    parser.add_argument("example", nargs="?", help="示例文件名或编号")
    parser.add_argument("--list", action="store_true", help="列出所有可用示例")

    # 运行模式
    parser.add_argument("--web", action="store_true", help="启动Web UI模式")
    parser.add_argument("--web-host", default="localhost", help="Web UI主机地址")
    parser.add_argument("--web-port", type=int, default=8089, help="Web UI端口")

    # 测试参数
    parser.add_argument("-u", "--users", type=int, default=10, help="用户数")
    parser.add_argument("-r", "--spawn-rate", type=int, default=2, help="启动速率")
    parser.add_argument("-t", "--run-time", default="60s", help="运行时间")

    # Mock服务器
    parser.add_argument("--mock-host", default="localhost", help="Mock服务器主机")
    parser.add_argument("--mock-port", type=int, default=5000, help="Mock服务器端口")
    parser.add_argument("--skip-mock", action="store_true", help="跳过Mock服务器检查")

    args = parser.parse_args()

    print("🧪 Locust示例运行器")
    print("=" * 50)

    # 获取示例列表
    examples = get_available_examples()
    if not examples:
        print("❌ 未找到示例文件")
        return

    # 列出示例
    if args.list:
        print("📋 可用示例:")
        for i, example in enumerate(examples, 1):
            print(f"   {i:2d}. {example.name}")
        return

    # 选择示例
    example_file = None
    if args.example:
        # 按编号选择
        if args.example.isdigit():
            idx = int(args.example) - 1
            if 0 <= idx < len(examples):
                example_file = examples[idx]
            else:
                print(f"❌ 无效编号: {args.example}")
                return
        else:
            # 按文件名选择
            for example in examples:
                if args.example in example.name:
                    example_file = example
                    break

            if not example_file:
                print(f"❌ 未找到示例: {args.example}")
                return
    else:
        # 默认选择第一个示例
        example_file = examples[0]
        print(f"💡 未指定示例，使用默认: {example_file.name}")

    # 检查Mock服务器
    if not args.skip_mock:
        if not start_mock_server_if_needed(args.mock_host, args.mock_port):
            print("❌ Mock服务器启动失败，请手动启动或使用 --skip-mock 跳过")
            return

    # 运行示例
    run_example(
        example_file=example_file,
        web_ui=args.web,
        users=args.users,
        spawn_rate=args.spawn_rate,
        run_time=args.run_time,
        host=args.web_host,
        port=args.web_port,
    )


if __name__ == "__main__":
    main()
