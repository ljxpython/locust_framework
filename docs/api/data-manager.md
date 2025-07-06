# 数据管理API参考

本文档详细介绍数据管理模块的API接口，包括数据生成器、数据提供者和数据分发器。

## 📊 DataGenerator

数据生成器提供多种类型的测试数据生成功能。

### 类定义

```python
from src.data_manager.data_generator import DataGenerator

class DataGenerator:
    """测试数据生成器

    基于Faker库提供丰富的测试数据生成功能，
    支持多种数据类型和本地化设置。
    """
```

### 构造函数

```python
def __init__(self, locale: str = "zh_CN", seed: Optional[int] = None):
    """初始化数据生成器

    Args:
        locale: 本地化设置，默认中文
        seed: 随机种子，用于生成可重复的数据

    Example:
        >>> generator = DataGenerator(locale="en_US", seed=12345)
        >>> generator_cn = DataGenerator()  # 使用中文
    """
```

### 基础数据生成

#### generate_name()

```python
def generate_name(self, gender: Optional[str] = None) -> str:
    """生成姓名

    Args:
        gender: 性别 ("male"/"female")，可选

    Returns:
        str: 生成的姓名

    Example:
        >>> generator.generate_name()
        '张三'
        >>> generator.generate_name(gender="female")
        '李小红'
    """
```

#### generate_email()

```python
def generate_email(self, domain: Optional[str] = None) -> str:
    """生成邮箱地址

    Args:
        domain: 邮箱域名，可选

    Returns:
        str: 生成的邮箱地址

    Example:
        >>> generator.generate_email()
        'zhangsan@example.com'
        >>> generator.generate_email(domain="test.com")
        'user123@test.com'
    """
```

#### generate_phone_number()

```python
def generate_phone_number(self, region: str = "CN") -> str:
    """生成手机号码

    Args:
        region: 地区代码，默认中国

    Returns:
        str: 生成的手机号码

    Example:
        >>> generator.generate_phone_number()
        '13812345678'
        >>> generator.generate_phone_number(region="US")
        '+1-555-123-4567'
    """
```

#### generate_address()

```python
def generate_address(self, include_country: bool = False) -> Dict[str, str]:
    """生成地址信息

    Args:
        include_country: 是否包含国家信息

    Returns:
        Dict[str, str]: 地址信息字典

    Example:
        >>> generator.generate_address()
        {
            'province': '北京市',
            'city': '北京市',
            'district': '朝阳区',
            'street': '建国路123号',
            'postal_code': '100000'
        }
    """
```

### 数值数据生成

#### generate_integer()

```python
def generate_integer(self, min_value: int = 0, max_value: int = 100) -> int:
    """生成整数

    Args:
        min_value: 最小值
        max_value: 最大值

    Returns:
        int: 生成的整数

    Example:
        >>> generator.generate_integer(1, 10)
        7
        >>> generator.generate_integer(100, 1000)
        456
    """
```

#### generate_float()

```python
def generate_float(self, min_value: float = 0.0, max_value: float = 100.0,
                  precision: int = 2) -> float:
    """生成浮点数

    Args:
        min_value: 最小值
        max_value: 最大值
        precision: 小数位数

    Returns:
        float: 生成的浮点数

    Example:
        >>> generator.generate_float(0, 100, 2)
        45.67
        >>> generator.generate_float(1.0, 10.0, 3)
        7.234
    """
```

#### generate_price()

```python
def generate_price(self, min_price: float = 1.0, max_price: float = 1000.0,
                  currency: str = "CNY") -> Dict[str, Any]:
    """生成价格信息

    Args:
        min_price: 最小价格
        max_price: 最大价格
        currency: 货币类型

    Returns:
        Dict[str, Any]: 价格信息

    Example:
        >>> generator.generate_price(10, 100)
        {
            'amount': 45.99,
            'currency': 'CNY',
            'formatted': '¥45.99'
        }
    """
```

### 文本数据生成

#### generate_text()

```python
def generate_text(self, min_length: int = 10, max_length: int = 100,
                 text_type: str = "sentence") -> str:
    """生成文本内容

    Args:
        min_length: 最小长度
        max_length: 最大长度
        text_type: 文本类型 ("word"/"sentence"/"paragraph")

    Returns:
        str: 生成的文本

    Example:
        >>> generator.generate_text(10, 50, "sentence")
        '这是一个测试句子，用于演示文本生成功能。'
        >>> generator.generate_text(5, 20, "word")
        '测试 数据 生成 工具'
    """
```

#### generate_username()

```python
def generate_username(self, min_length: int = 6, max_length: int = 20) -> str:
    """生成用户名

    Args:
        min_length: 最小长度
        max_length: 最大长度

    Returns:
        str: 生成的用户名

    Example:
        >>> generator.generate_username()
        'user_zhang123'
        >>> generator.generate_username(8, 15)
        'testuser456'
    """
```

### 日期时间生成

#### generate_datetime()

```python
def generate_datetime(self, start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """生成日期时间

    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        format_str: 格式字符串

    Returns:
        str: 生成的日期时间字符串

    Example:
        >>> generator.generate_datetime()
        '2023-12-01 14:30:45'
        >>> generator.generate_datetime("2023-01-01", "2023-12-31")
        '2023-06-15 09:22:33'
    """
```

#### generate_timestamp()

```python
def generate_timestamp(self, start_timestamp: Optional[int] = None,
                      end_timestamp: Optional[int] = None) -> int:
    """生成时间戳

    Args:
        start_timestamp: 开始时间戳
        end_timestamp: 结束时间戳

    Returns:
        int: 生成的时间戳

    Example:
        >>> generator.generate_timestamp()
        1701234567
    """
```

### 业务数据生成

#### generate_user_profile()

```python
def generate_user_profile(self, include_avatar: bool = True) -> Dict[str, Any]:
    """生成用户资料

    Args:
        include_avatar: 是否包含头像URL

    Returns:
        Dict[str, Any]: 用户资料信息

    Example:
        >>> generator.generate_user_profile()
        {
            'id': 'user_123456',
            'username': 'zhangsan123',
            'name': '张三',
            'email': 'zhangsan@example.com',
            'phone': '13812345678',
            'age': 28,
            'gender': 'male',
            'avatar': 'https://example.com/avatar/123.jpg',
            'bio': '这是一个测试用户的简介。',
            'created_at': '2023-01-15 10:30:00'
        }
    """
```

#### generate_product_info()

```python
def generate_product_info(self, category: Optional[str] = None) -> Dict[str, Any]:
    """生成商品信息

    Args:
        category: 商品分类，可选

    Returns:
        Dict[str, Any]: 商品信息

    Example:
        >>> generator.generate_product_info("electronics")
        {
            'id': 'prod_789012',
            'name': '智能手机',
            'category': 'electronics',
            'price': 2999.00,
            'description': '高性能智能手机，配备先进的处理器。',
            'brand': '华为',
            'model': 'P50 Pro',
            'sku': 'HW-P50-PRO-256GB',
            'stock': 150,
            'images': ['https://example.com/img1.jpg'],
            'created_at': '2023-10-01 12:00:00'
        }
    """
```

## 📋 DataProvider

数据提供者负责管理和分发测试数据。

### 类定义

```python
from src.data_manager.data_provider import DataProvider

class DataProvider:
    """测试数据提供者

    管理测试数据的加载、分发和同步。
    """
```

### 核心方法

#### load_data_from_file()

```python
def load_data_from_file(self, file_path: str,
                       distribution_strategy: str = "round_robin",
                       data_key: Optional[str] = None) -> bool:
    """从文件加载数据

    Args:
        file_path: 文件路径
        distribution_strategy: 分发策略 ("round_robin"/"random"/"sequential")
        data_key: 数据键名，用于标识数据集

    Returns:
        bool: 加载是否成功

    Example:
        >>> provider = DataProvider()
        >>> provider.load_data_from_file("test_data/users.csv", "round_robin", "users")
        True
    """
```

#### load_data_from_database()

```python
def load_data_from_database(self, connection_string: str, query: str,
                           data_key: str, distribution_strategy: str = "round_robin") -> bool:
    """从数据库加载数据

    Args:
        connection_string: 数据库连接字符串
        query: SQL查询语句
        data_key: 数据键名
        distribution_strategy: 分发策略

    Returns:
        bool: 加载是否成功

    Example:
        >>> provider.load_data_from_database(
        ...     "mysql://user:pass@localhost/testdb",
        ...     "SELECT * FROM test_users",
        ...     "db_users"
        ... )
    """
```

#### get_next_data()

```python
def get_next_data(self, data_key: str) -> Optional[Dict[str, Any]]:
    """获取下一条数据

    Args:
        data_key: 数据键名

    Returns:
        Optional[Dict[str, Any]]: 数据记录，如果没有数据则返回None

    Example:
        >>> data = provider.get_next_data("users")
        >>> print(data)
        {'username': 'user1', 'password': 'pass1', 'email': 'user1@example.com'}
    """
```

#### get_random_data()

```python
def get_random_data(self, data_key: str, count: int = 1) -> List[Dict[str, Any]]:
    """获取随机数据

    Args:
        data_key: 数据键名
        count: 获取数量

    Returns:
        List[Dict[str, Any]]: 随机数据列表

    Example:
        >>> random_users = provider.get_random_data("users", 3)
        >>> len(random_users)
        3
    """
```

#### get_data_stats()

```python
def get_data_stats(self, data_key: str) -> Dict[str, Any]:
    """获取数据统计信息

    Args:
        data_key: 数据键名

    Returns:
        Dict[str, Any]: 统计信息

    Example:
        >>> stats = provider.get_data_stats("users")
        >>> print(stats)
        {
            'total_records': 1000,
            'current_index': 45,
            'distribution_strategy': 'round_robin',
            'last_accessed': '2023-12-01 10:30:00'
        }
    """
```

## 🔄 DataDistributor

数据分发器负责在分布式环境中同步测试数据。

### 类定义

```python
from src.data_manager.data_distributor import DataDistributor

class DataDistributor:
    """数据分发器

    在分布式测试环境中同步和分发测试数据。
    """
```

### 核心方法

#### sync_data()

```python
def sync_data(self, data_key: str, target_workers: List[str]) -> bool:
    """同步数据到工作节点

    Args:
        data_key: 数据键名
        target_workers: 目标工作节点列表

    Returns:
        bool: 同步是否成功

    Example:
        >>> distributor = DataDistributor()
        >>> success = distributor.sync_data("users", ["worker1", "worker2"])
    """
```

#### distribute_data_range()

```python
def distribute_data_range(self, data_key: str, worker_id: str,
                         total_workers: int) -> Tuple[int, int]:
    """分配数据范围给工作节点

    Args:
        data_key: 数据键名
        worker_id: 工作节点ID
        total_workers: 总工作节点数

    Returns:
        Tuple[int, int]: 数据范围 (start_index, end_index)

    Example:
        >>> start, end = distributor.distribute_data_range("users", "worker1", 4)
        >>> print(f"Worker1 处理数据范围: {start}-{end}")
    """
```

## 🔧 使用示例

### 完整数据管理流程

```python
from src.data_manager.data_generator import DataGenerator
from src.data_manager.data_provider import DataProvider
from src.data_manager.data_distributor import DataDistributor

# 1. 初始化组件
generator = DataGenerator(locale="zh_CN", seed=12345)
provider = DataProvider()
distributor = DataDistributor()

# 2. 生成测试数据
users_data = []
for i in range(1000):
    user = generator.generate_user_profile()
    users_data.append(user)

# 保存到文件
import csv
with open("test_data/generated_users.csv", "w", newline="", encoding="utf-8") as f:
    if users_data:
        writer = csv.DictWriter(f, fieldnames=users_data[0].keys())
        writer.writeheader()
        writer.writerows(users_data)

# 3. 加载数据到提供者
provider.load_data_from_file("test_data/generated_users.csv", "round_robin", "users")

# 4. 在测试中使用数据
def get_test_user():
    return provider.get_next_data("users")

# 5. 分布式环境中同步数据
if is_distributed_mode():
    distributor.sync_data("users", get_worker_list())
```

### 自定义数据生成器

```python
class CustomDataGenerator(DataGenerator):
    """自定义数据生成器"""

    def generate_order_info(self) -> Dict[str, Any]:
        """生成订单信息"""
        return {
            'order_id': f"ORD{self.generate_integer(100000, 999999)}",
            'customer_id': f"CUST{self.generate_integer(1000, 9999)}",
            'product_id': f"PROD{self.generate_integer(100, 999)}",
            'quantity': self.generate_integer(1, 5),
            'unit_price': self.generate_float(10.0, 500.0, 2),
            'total_amount': 0,  # 计算得出
            'order_date': self.generate_datetime(),
            'status': self.fake.random_element(['pending', 'confirmed', 'shipped', 'delivered'])
        }

    def generate_api_request_data(self) -> Dict[str, Any]:
        """生成API请求数据"""
        return {
            'request_id': self.fake.uuid4(),
            'timestamp': self.generate_timestamp(),
            'method': self.fake.random_element(['GET', 'POST', 'PUT', 'DELETE']),
            'endpoint': f"/api/v1/{self.fake.random_element(['users', 'orders', 'products'])}",
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': self.fake.user_agent(),
                'X-Request-ID': self.fake.uuid4()
            },
            'payload': self.generate_json_payload()
        }
```

### 数据提供者扩展

```python
class EnhancedDataProvider(DataProvider):
    """增强的数据提供者"""

    def load_data_from_api(self, api_url: str, headers: Dict[str, str],
                          data_key: str) -> bool:
        """从API加载数据"""
        try:
            import requests
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self._store_data(data_key, data)
                return True
        except Exception as e:
            print(f"Failed to load data from API: {e}")
        return False

    def get_weighted_data(self, data_key: str, weights: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """根据权重获取数据"""
        import random

        data_list = self._get_data_list(data_key)
        if not data_list:
            return None

        # 根据权重选择数据
        choices = list(weights.keys())
        weight_values = list(weights.values())

        selected_key = random.choices(choices, weights=weight_values)[0]
        return self.get_next_data(selected_key)
```

## ⚠️ 注意事项

1. **内存管理**: 大量数据加载时注意内存使用
2. **数据同步**: 分布式环境中确保数据一致性
3. **文件格式**: 支持CSV、JSON、Excel等格式
4. **数据质量**: 生成的数据应符合业务逻辑
5. **性能优化**: 合理设置缓存和批处理大小

## 🔗 相关文档

- [性能分析API](analysis.md) - 性能分析模块API
- [监控告警API](monitoring.md) - 监控告警模块API
- [插件接口API](plugins.md) - 插件开发接口
- [数据配置](../configuration/data-config.md) - 数据管理配置
