#!/usr/bin/env python3
"""
启动Mock服务器脚本

用于启动测试用的Mock HTTP服务
"""

import subprocess
import sys
import time
from pathlib import Path

import requests


def check_dependencies():
    """检查依赖"""
    try:
        import flask
        import flask_cors

        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("💡 请运行: pip install flask flask-cors")
        return False


def start_server(host="localhost", port=5000):
    """启动Mock服务器"""
    script_dir = Path(__file__).parent.parent
    mock_server_path = script_dir / "mock_server" / "app.py"

    if not mock_server_path.exists():
        print(f"❌ Mock服务文件不存在: {mock_server_path}")
        return False

    print(f"🚀 启动Mock服务器...")
    print(f"   主机: {host}")
    print(f"   端口: {port}")
    print(f"   文件: {mock_server_path}")

    try:
        # 启动服务器进程
        import os

        env = os.environ.copy()
        env.update({"FLASK_HOST": host, "FLASK_PORT": str(port)})
        process = subprocess.Popen([sys.executable, str(mock_server_path)], env=env)

        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        for i in range(30):  # 等待最多30秒
            try:
                response = requests.get(f"http://{host}:{port}/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Mock服务器启动成功!")
                    print(f"🌐 访问地址: http://{host}:{port}")
                    print(f"📊 健康检查: http://{host}:{port}/health")
                    print(f"📈 系统指标: http://{host}:{port}/metrics")
                    return True
            except requests.exceptions.RequestException:
                pass

            time.sleep(1)

        print("❌ Mock服务器启动超时")
        process.terminate()
        return False

    except Exception as e:
        print(f"❌ 启动Mock服务器失败: {e}")
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="启动Mock HTTP服务器")
    parser.add_argument("--host", default="localhost", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=5000, help="服务器端口")

    args = parser.parse_args()

    print("🔧 Mock服务器启动脚本")
    print("=" * 50)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 启动服务器
    if start_server(args.host, args.port):
        print("\n💡 使用方法:")
        print("   - Ctrl+C 停止服务器")
        print("   - 在另一个终端运行Locust测试")
        print("   - locust -f locustfiles/examples/01_basic_test.py")

        try:
            # 保持脚本运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止Mock服务器...")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
