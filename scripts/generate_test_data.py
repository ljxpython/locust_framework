#!/usr/bin/env python3
"""
测试数据生成脚本

用于生成各种类型的测试数据
"""

import argparse
import csv
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from src.data_manager.data_generator import DataGenerator


def generate_csv_data(generator, data_type, count, output_file):
    """生成CSV格式数据"""
    print(f"📊 生成CSV数据: {data_type}")

    data = []
    if data_type == "users":
        for _ in range(count):
            data.append(generator.generate_user_profile())
    elif data_type == "products":
        for _ in range(count):
            data.append(generator.generate_product_data())
    elif data_type == "orders":
        for _ in range(count):
            data.append(generator.generate_order_data())
    elif data_type == "mixed":
        # 混合数据类型
        for _ in range(count):
            data.append(
                {
                    "type": generator.fake.random_element(["user", "product", "order"]),
                    "name": generator.generate_name(),
                    "email": generator.generate_email(),
                    "phone": generator.generate_phone(),
                    "address": generator.generate_address(),
                    "id": generator.fake.uuid4(),
                    "timestamp": generator.fake.date_time().isoformat(),
                }
            )
    else:
        print(f"❌ 不支持的数据类型: {data_type}")
        return False

    if not data:
        print("❌ 未生成数据")
        return False

    # 写入CSV文件
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    print(f"✅ 已生成 {len(data)} 条记录到: {output_file}")
    return True


def generate_json_data(generator, data_type, count, output_file):
    """生成JSON格式数据"""
    print(f"📊 生成JSON数据: {data_type}")

    data = []
    if data_type == "users":
        for _ in range(count):
            data.append(generator.generate_user_profile())
    elif data_type == "products":
        for _ in range(count):
            data.append(generator.generate_product_data())
    elif data_type == "orders":
        for _ in range(count):
            data.append(generator.generate_order_data())
    elif data_type == "test_dataset":
        # 创建测试数据集
        dataset = {
            "users": [
                generator.generate_user_profile() for _ in range(min(count // 3, 100))
            ],
            "products": [
                generator.generate_product_data() for _ in range(min(count // 3, 100))
            ],
            "orders": [
                generator.generate_order_data() for _ in range(min(count // 3, 100))
            ],
            "metadata": {
                "generated_at": generator.fake.date_time().isoformat(),
                "total_records": count,
                "generator_version": "1.0.0",
            },
        }
        data = dataset
    else:
        print(f"❌ 不支持的数据类型: {data_type}")
        return False

    # 写入JSON文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if isinstance(data, list):
        print(f"✅ 已生成 {len(data)} 条记录到: {output_file}")
    else:
        print(f"✅ 已生成数据集到: {output_file}")
    return True


def generate_locust_data(generator, count, output_dir):
    """生成Locust测试专用数据"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"🎯 生成Locust测试数据到: {output_dir}")

    # 用户凭据数据
    credentials_file = output_dir / "credentials.csv"
    credentials = []
    for _ in range(count):
        credentials.append(
            {
                "username": generator.generate_username(),
                "password": generator.fake.password(length=12),
                "email": generator.generate_email(),
            }
        )

    with open(credentials_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "password", "email"])
        writer.writeheader()
        writer.writerows(credentials)

    print(f"✅ 用户凭据: {credentials_file}")

    # 商品数据
    products_file = output_dir / "products.json"
    products = [generator.generate_product_data() for _ in range(min(count, 100))]

    with open(products_file, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"✅ 商品数据: {products_file}")

    # 搜索关键词
    keywords_file = output_dir / "search_keywords.txt"
    keywords = [generator.fake.word() for _ in range(min(count // 10, 50))]

    with open(keywords_file, "w", encoding="utf-8") as f:
        f.write("\n".join(keywords))

    print(f"✅ 搜索关键词: {keywords_file}")

    # 测试参数配置
    config_file = output_dir / "test_config.json"
    config = {
        "users_count": count,
        "spawn_rate": max(1, count // 10),
        "run_time": "300s",
        "host": "http://localhost:5000",
        "custom_params": {
            "loop_num": generator.fake.random_int(1, 5),
            "is_rendezvous": generator.fake.boolean(),
            "rendezvous_num": generator.fake.random_int(2, 10),
        },
    }

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"✅ 测试配置: {config_file}")

    print(f"🎉 Locust测试数据生成完成!")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="生成测试数据")

    # 数据类型和数量
    parser.add_argument(
        "--type",
        choices=["users", "products", "orders", "mixed", "test_dataset", "locust"],
        default="mixed",
        help="数据类型",
    )
    parser.add_argument("--count", type=int, default=100, help="数据条数")

    # 输出格式和文件
    parser.add_argument(
        "--format", choices=["csv", "json"], default="json", help="输出格式"
    )
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument(
        "--output-dir", default="data", help="输出目录 (用于locust类型)"
    )

    # 数据生成选项
    parser.add_argument("--locale", default="zh_CN", help="本地化设置")
    parser.add_argument("--seed", type=int, help="随机种子")

    args = parser.parse_args()

    print("🎲 测试数据生成器")
    print("=" * 50)
    print(f"   数据类型: {args.type}")
    print(f"   数据数量: {args.count}")
    print(f"   输出格式: {args.format}")
    print(f"   本地化: {args.locale}")
    if args.seed:
        print(f"   随机种子: {args.seed}")
    print()

    # 初始化数据生成器
    try:
        generator = DataGenerator(locale=args.locale, seed=args.seed)
    except Exception as e:
        print(f"❌ 初始化数据生成器失败: {e}")
        return 1

    # 特殊处理locust类型
    if args.type == "locust":
        return 0 if generate_locust_data(generator, args.count, args.output_dir) else 1

    # 确定输出文件
    if args.output:
        output_file = Path(args.output)
    else:
        # 自动生成文件名
        suffix = "csv" if args.format == "csv" else "json"
        output_file = Path(f"test_data_{args.type}_{args.count}.{suffix}")

    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 生成数据
    try:
        if args.format == "csv":
            success = generate_csv_data(generator, args.type, args.count, output_file)
        else:
            success = generate_json_data(generator, args.type, args.count, output_file)

        return 0 if success else 1

    except Exception as e:
        print(f"❌ 生成数据失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
