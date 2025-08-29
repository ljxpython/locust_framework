#!/usr/bin/env python3
"""
Mock HTTP服务
用于Locust性能测试框架的示例和测试
"""

import json
import random
import threading
import time
import uuid
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 配置参数
CONFIG = {
    "response_delay_ms": 50,  # 基础响应延时(毫秒)
    "error_rate": 0.05,  # 错误率(5%)
    "slow_request_rate": 0.1,  # 慢请求比例(10%)
    "slow_delay_ms": 2000,  # 慢请求延时(毫秒)
}

# 模拟数据存储
USERS = {}
PRODUCTS = {}
ORDERS = {}
SESSIONS = {}

# 系统指标
METRICS = {
    "requests_total": 0,
    "requests_success": 0,
    "requests_error": 0,
    "response_times": [],
    "active_users": 0,
}


def init_data():
    """初始化模拟数据"""
    global PRODUCTS

    # 初始化商品数据
    categories = ["电子产品", "服装", "图书", "家居", "运动"]
    for i in range(1, 101):
        PRODUCTS[str(i)] = {
            "id": str(i),
            "name": f"商品{i}",
            "category": random.choice(categories),
            "price": round(random.uniform(10, 1000), 2),
            "stock": random.randint(0, 100),
            "description": f"这是商品{i}的详细描述",
            "rating": round(random.uniform(3.0, 5.0), 1),
            "created_at": datetime.now().isoformat(),
        }


def simulate_delay():
    """模拟响应延时"""
    delay = CONFIG["response_delay_ms"] / 1000

    # 随机产生慢请求
    if random.random() < CONFIG["slow_request_rate"]:
        delay = CONFIG["slow_delay_ms"] / 1000

    time.sleep(delay)


def should_return_error():
    """判断是否返回错误"""
    return random.random() < CONFIG["error_rate"]


def update_metrics(success=True, response_time=None):
    """更新系统指标"""
    METRICS["requests_total"] += 1
    if success:
        METRICS["requests_success"] += 1
    else:
        METRICS["requests_error"] += 1

    if response_time:
        METRICS["response_times"].append(response_time)
        # 保持最近1000次请求的响应时间
        if len(METRICS["response_times"]) > 1000:
            METRICS["response_times"] = METRICS["response_times"][-1000:]


@app.before_request
def before_request():
    """请求前处理"""
    request.start_time = time.time()


@app.after_request
def after_request(response):
    """请求后处理"""
    if hasattr(request, "start_time"):
        response_time = (time.time() - request.start_time) * 1000
        success = 200 <= response.status_code < 400
        update_metrics(success, response_time)
    return response


# 健康检查端点
@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    )


@app.route("/metrics", methods=["GET"])
def metrics():
    """系统指标"""
    response_times = METRICS["response_times"]
    avg_response_time = (
        sum(response_times) / len(response_times) if response_times else 0
    )

    return jsonify(
        {
            "requests_total": METRICS["requests_total"],
            "requests_success": METRICS["requests_success"],
            "requests_error": METRICS["requests_error"],
            "error_rate": METRICS["requests_error"]
            / max(METRICS["requests_total"], 1)
            * 100,
            "avg_response_time": round(avg_response_time, 2),
            "active_users": METRICS["active_users"],
            "timestamp": datetime.now().isoformat(),
        }
    )


# 用户认证相关API
@app.route("/auth/login", methods=["POST"])
def login():
    """用户登录"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    # 模拟登录验证（简单验证）
    if len(username) < 3:
        return jsonify({"error": "用户名或密码错误"}), 401

    # 生成会话token
    token = str(uuid.uuid4())
    user_id = str(hash(username) % 10000)

    SESSIONS[token] = {
        "user_id": user_id,
        "username": username,
        "login_time": datetime.now().isoformat(),
    }

    USERS[user_id] = {
        "id": user_id,
        "username": username,
        "name": f"用户{username}",
        "email": f"{username}@example.com",
        "avatar": f"https://example.com/avatar/{user_id}.jpg",
    }

    METRICS["active_users"] = len(SESSIONS)

    return jsonify({"token": token, "user": USERS[user_id], "expires_in": 3600})


@app.route("/auth/logout", methods=["POST"])
def logout():
    """用户登出"""
    simulate_delay()

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token in SESSIONS:
        del SESSIONS[token]
        METRICS["active_users"] = len(SESSIONS)

    return jsonify({"message": "登出成功"})


@app.route("/auth/profile", methods=["GET"])
def profile():
    """获取用户信息"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token not in SESSIONS:
        return jsonify({"error": "未授权访问"}), 401

    user_id = SESSIONS[token]["user_id"]
    return jsonify(USERS.get(user_id, {}))


# 商品相关API
@app.route("/api/products", methods=["GET"])
def get_products():
    """获取商品列表"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    category = request.args.get("category", "")

    products = list(PRODUCTS.values())

    # 分类过滤
    if category:
        products = [p for p in products if p["category"] == category]

    # 分页
    start = (page - 1) * limit
    end = start + limit
    page_products = products[start:end]

    return jsonify(
        {
            "products": page_products,
            "total": len(products),
            "page": page,
            "limit": limit,
            "pages": (len(products) + limit - 1) // limit,
        }
    )


@app.route("/api/products/<product_id>", methods=["GET"])
def get_product(product_id):
    """获取商品详情"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    if product_id not in PRODUCTS:
        return jsonify({"error": "商品不存在"}), 404

    return jsonify(PRODUCTS[product_id])


@app.route("/api/search", methods=["GET"])
def search_products():
    """搜索商品"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    q = request.args.get("q", "").lower()
    sort = request.args.get("sort", "name")

    products = []
    for product in PRODUCTS.values():
        if q in product["name"].lower() or q in product["description"].lower():
            products.append(product)

    # 排序
    if sort == "price":
        products.sort(key=lambda x: x["price"])
    elif sort == "rating":
        products.sort(key=lambda x: x["rating"], reverse=True)

    return jsonify({"products": products, "query": q, "total": len(products)})


# 订单相关API
@app.route("/api/orders", methods=["GET"])
def get_orders():
    """获取订单列表"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token not in SESSIONS:
        return jsonify({"error": "未授权访问"}), 401

    user_id = SESSIONS[token]["user_id"]
    user_orders = [order for order in ORDERS.values() if order["user_id"] == user_id]

    return jsonify({"orders": user_orders})


@app.route("/api/orders", methods=["POST"])
def create_order():
    """创建订单"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token not in SESSIONS:
        return jsonify({"error": "未授权访问"}), 401

    data = request.get_json() or {}
    user_id = SESSIONS[token]["user_id"]

    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "user_id": user_id,
        "products": data.get("products", []),
        "total_amount": data.get("total_amount", 0),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    ORDERS[order_id] = order

    return jsonify(order), 201


@app.route("/api/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    """获取订单详情"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    if order_id not in ORDERS:
        return jsonify({"error": "订单不存在"}), 404

    return jsonify(ORDERS[order_id])


# 购物车API
@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    """添加到购物车"""
    simulate_delay()

    if should_return_error():
        return jsonify({"error": "服务器内部错误"}), 500

    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id or product_id not in PRODUCTS:
        return jsonify({"error": "商品不存在"}), 404

    return jsonify(
        {"message": "添加成功", "product_id": product_id, "quantity": quantity}
    )


# 配置管理API
@app.route("/admin/config", methods=["GET"])
def get_config():
    """获取服务配置"""
    return jsonify(CONFIG)


@app.route("/admin/config", methods=["POST"])
def update_config():
    """更新服务配置"""
    data = request.get_json() or {}
    CONFIG.update(data)
    return jsonify({"message": "配置更新成功", "config": CONFIG})


if __name__ == "__main__":
    import os

    # 从环境变量读取配置
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))

    init_data()
    print("🚀 Mock服务启动中...")
    print("📊 API端点:")
    print(f"  - 健康检查: http://localhost:{port}/health")
    print(f"  - 系统指标: http://localhost:{port}/metrics")
    print(f"  - 用户登录: POST http://localhost:{port}/auth/login")
    print(f"  - 商品列表: http://localhost:{port}/api/products")
    print(f"  - 商品搜索: http://localhost:{port}/api/search")
    print(f"  - 订单管理: http://localhost:{port}/api/orders")
    print("💡 用于Locust性能测试的模拟服务")

    app.run(host=host, port=port, debug=True, threaded=True)
