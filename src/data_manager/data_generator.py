"""
测试数据生成器

提供各种类型测试数据的生成功能
"""

import csv
import json
import random
import string
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from faker import Faker

from src.utils.log_moudle import logger


class DataGenerator:
    """测试数据生成器"""

    def __init__(self, locale: str = "zh_CN"):
        self.faker = Faker(locale)
        self.generators = {}
        self._register_default_generators()

    def register_generator(self, name: str, generator_func: Callable):
        """注册自定义数据生成器"""
        self.generators[name] = generator_func
        logger.info(f"注册数据生成器: {name}")

    def generate_user_data(self, count: int = 100) -> List[Dict]:
        """生成用户数据"""
        users = []
        for _ in range(count):
            user = {
                "user_id": str(uuid.uuid4()),
                "username": self.faker.user_name(),
                "email": self.faker.email(),
                "phone": self.faker.phone_number(),
                "name": self.faker.name(),
                "age": random.randint(18, 65),
                "gender": random.choice(["male", "female"]),
                "address": self.faker.address(),
                "company": self.faker.company(),
                "job": self.faker.job(),
                "created_at": self.faker.date_time_between(
                    start_date="-2y", end_date="now"
                ).isoformat(),
                "is_active": random.choice([True, False]),
                "balance": round(random.uniform(0, 10000), 2),
            }
            users.append(user)

        logger.info(f"生成了 {count} 条用户数据")
        return users

    def generate_product_data(self, count: int = 50) -> List[Dict]:
        """生成商品数据"""
        categories = [
            "电子产品",
            "服装",
            "食品",
            "图书",
            "家居",
            "运动",
            "美妆",
            "汽车",
        ]
        products = []

        for _ in range(count):
            product = {
                "product_id": str(uuid.uuid4()),
                "name": self.faker.catch_phrase(),
                "description": self.faker.text(max_nb_chars=200),
                "category": random.choice(categories),
                "price": round(random.uniform(10, 1000), 2),
                "stock": random.randint(0, 1000),
                "brand": self.faker.company(),
                "rating": round(random.uniform(1, 5), 1),
                "reviews_count": random.randint(0, 1000),
                "created_at": self.faker.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat(),
                "is_available": random.choice([True, False]),
                "weight": round(random.uniform(0.1, 10), 2),
                "dimensions": {
                    "length": round(random.uniform(1, 50), 1),
                    "width": round(random.uniform(1, 50), 1),
                    "height": round(random.uniform(1, 50), 1),
                },
            }
            products.append(product)

        logger.info(f"生成了 {count} 条商品数据")
        return products

    def generate_order_data(
        self,
        count: int = 200,
        user_ids: List[str] = None,
        product_ids: List[str] = None,
    ) -> List[Dict]:
        """生成订单数据"""
        if not user_ids:
            user_ids = [str(uuid.uuid4()) for _ in range(20)]
        if not product_ids:
            product_ids = [str(uuid.uuid4()) for _ in range(50)]

        orders = []
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]

        for _ in range(count):
            order_items = []
            item_count = random.randint(1, 5)

            for _ in range(item_count):
                order_items.append(
                    {
                        "product_id": random.choice(product_ids),
                        "quantity": random.randint(1, 10),
                        "unit_price": round(random.uniform(10, 500), 2),
                    }
                )

            total_amount = sum(
                item["quantity"] * item["unit_price"] for item in order_items
            )

            order = {
                "order_id": str(uuid.uuid4()),
                "user_id": random.choice(user_ids),
                "items": order_items,
                "total_amount": round(total_amount, 2),
                "status": random.choice(statuses),
                "payment_method": random.choice(
                    ["credit_card", "debit_card", "paypal", "alipay", "wechat_pay"]
                ),
                "shipping_address": self.faker.address(),
                "created_at": self.faker.date_time_between(
                    start_date="-6m", end_date="now"
                ).isoformat(),
                "updated_at": self.faker.date_time_between(
                    start_date="-6m", end_date="now"
                ).isoformat(),
                "notes": (
                    self.faker.text(max_nb_chars=100) if random.random() < 0.3 else ""
                ),
            }
            orders.append(order)

        logger.info(f"生成了 {count} 条订单数据")
        return orders

    def generate_api_test_data(self, count: int = 100) -> List[Dict]:
        """生成API测试数据"""
        methods = ["GET", "POST", "PUT", "DELETE"]
        status_codes = [200, 201, 400, 401, 403, 404, 500]

        api_data = []
        for _ in range(count):
            data = {
                "request_id": str(uuid.uuid4()),
                "method": random.choice(methods),
                "url": f"https://api.example.com/{self.faker.uri_path()}",
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": self.faker.user_agent(),
                    "Authorization": f"Bearer {self.faker.sha256()[:32]}",
                },
                "params": {
                    "page": random.randint(1, 100),
                    "limit": random.choice([10, 20, 50, 100]),
                    "sort": random.choice(["asc", "desc"]),
                },
                "body": {
                    "data": self.faker.json(),
                    "timestamp": datetime.now().isoformat(),
                },
                "expected_status": random.choice(status_codes),
                "timeout": random.randint(5, 30),
            }
            api_data.append(data)

        logger.info(f"生成了 {count} 条API测试数据")
        return api_data

    def generate_performance_test_data(self, count: int = 1000) -> List[Dict]:
        """生成性能测试数据"""
        scenarios = ["login", "browse", "search", "purchase", "logout"]

        perf_data = []
        for _ in range(count):
            data = {
                "session_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "scenario": random.choice(scenarios),
                "start_time": self.faker.date_time_between(
                    start_date="-1d", end_date="now"
                ).isoformat(),
                "response_time": round(random.uniform(100, 5000), 2),  # ms
                "success": random.choice([True, False]),
                "error_message": (
                    self.faker.sentence() if random.random() < 0.1 else None
                ),
                "request_size": random.randint(100, 10000),  # bytes
                "response_size": random.randint(500, 50000),  # bytes
                "concurrent_users": random.randint(1, 100),
                "server_load": round(random.uniform(0, 100), 2),  # %
            }
            perf_data.append(data)

        logger.info(f"生成了 {count} 条性能测试数据")
        return perf_data

    def generate_custom_data(
        self, generator_name: str, count: int = 100, **kwargs
    ) -> List[Dict]:
        """使用自定义生成器生成数据"""
        if generator_name not in self.generators:
            raise ValueError(f"未找到数据生成器: {generator_name}")

        generator_func = self.generators[generator_name]
        data = []

        for _ in range(count):
            item = generator_func(self.faker, **kwargs)
            data.append(item)

        logger.info(f"使用 {generator_name} 生成了 {count} 条数据")
        return data

    def generate_random_string(self, length: int = 10, chars: str = None) -> str:
        """生成随机字符串"""
        if chars is None:
            chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))

    def generate_random_number(self, min_val: int = 0, max_val: int = 100) -> int:
        """生成随机数字"""
        return random.randint(min_val, max_val)

    def generate_random_email(self, domain: str = None) -> str:
        """生成随机邮箱"""
        if domain:
            username = self.generate_random_string(8)
            return f"{username}@{domain}"
        return self.faker.email()

    def generate_random_phone(self, country_code: str = "+86") -> str:
        """生成随机手机号"""
        if country_code == "+86":
            # 中国手机号格式
            prefixes = [
                "130",
                "131",
                "132",
                "133",
                "134",
                "135",
                "136",
                "137",
                "138",
                "139",
                "150",
                "151",
                "152",
                "153",
                "155",
                "156",
                "157",
                "158",
                "159",
                "180",
                "181",
                "182",
                "183",
                "184",
                "185",
                "186",
                "187",
                "188",
                "189",
            ]
            prefix = random.choice(prefixes)
            suffix = "".join([str(random.randint(0, 9)) for _ in range(8)])
            return f"{country_code}{prefix}{suffix}"
        else:
            return self.faker.phone_number()

    def save_to_csv(self, data: List[Dict], filename: str, output_dir: str = "data"):
        """保存数据到CSV文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        file_path = output_path / filename

        if not data:
            logger.warning("没有数据可保存")
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in data:
                    # 处理嵌套字典和列表
                    processed_row = {}
                    for key, value in row.items():
                        if isinstance(value, (dict, list)):
                            processed_row[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            processed_row[key] = value
                    writer.writerow(processed_row)

            logger.info(f"数据已保存到: {file_path}")

        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")
            raise

    def save_to_json(self, data: List[Dict], filename: str, output_dir: str = "data"):
        """保存数据到JSON文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        file_path = output_path / filename

        try:
            with open(file_path, "w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=2)

            logger.info(f"数据已保存到: {file_path}")

        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            raise

    def _register_default_generators(self):
        """注册默认数据生成器"""

        def simple_user_generator(faker, **kwargs):
            return {
                "id": str(uuid.uuid4()),
                "name": faker.name(),
                "email": faker.email(),
            }

        def simple_product_generator(faker, **kwargs):
            return {
                "id": str(uuid.uuid4()),
                "name": faker.catch_phrase(),
                "price": round(random.uniform(10, 1000), 2),
            }

        self.register_generator("simple_user", simple_user_generator)
        self.register_generator("simple_product", simple_product_generator)

    def batch_generate(self, generators_config: List[Dict]) -> Dict[str, List[Dict]]:
        """批量生成多种类型的数据"""
        results = {}

        for config in generators_config:
            data_type = config.get("type")
            count = config.get("count", 100)
            params = config.get("params", {})

            if data_type == "user":
                results["users"] = self.generate_user_data(count)
            elif data_type == "product":
                results["products"] = self.generate_product_data(count)
            elif data_type == "order":
                user_ids = params.get("user_ids")
                product_ids = params.get("product_ids")
                results["orders"] = self.generate_order_data(
                    count, user_ids, product_ids
                )
            elif data_type == "api":
                results["api_data"] = self.generate_api_test_data(count)
            elif data_type == "performance":
                results["performance_data"] = self.generate_performance_test_data(count)
            elif data_type in self.generators:
                results[data_type] = self.generate_custom_data(
                    data_type, count, **params
                )
            else:
                logger.warning(f"未知的数据类型: {data_type}")

        return results
