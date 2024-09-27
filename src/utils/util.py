import random
import re
import string
from typing import Optional

import humps
import requests

from conf.config import settings

config = settings


def split_array(arr, lens):
    arr_len = len(arr)
    group_num = arr_len // lens
    result = []
    for i in range(group_num):
        result.append(arr[i * lens : (i + 1) * lens])
    if arr_len % lens != 0:
        result.append(arr[group_num * lens :])
    return result


def to_camel_case(key: str) -> str:
    """
    humps库地址后续可以研究大小驼峰转换
    https://github.com/nficano/humps?tab=readme-ov-file#converting-dictionary-keys
    """
    # 特殊简写处理
    if key == "md5":
        return "MD5"
    if key == "ip":
        return "IP"
    return humps.pascalize(key)


def to_snake_case(key: str) -> str:
    return humps.decamelize(key)


def expression_to_camel_case(expression: str):
    """
    将表达式中的key转为大驼峰
    找到所有符合条件的key，并分别处理为大驼峰并替换返回新的结果
    """
    pattern = r"(?<!')[A-Za-z][A-Za-z0-9]*"
    matchs = re.findall(pattern, expression)
    # logger.info(matchs)
    for match in matchs:
        # logger.info(match)
        camel_math = to_camel_case(match)
        # logger.info(camel_math)
        ptn = r"_?" + match
        expression = re.sub(ptn, camel_math, expression, count=1, flags=0)
        # logger.info(expression)
    return expression


def get_radmon_str(
    prefix: str = "",
    length: int = 10,
    characters: str = string.ascii_letters + string.digits,
) -> str:
    """生成随机字符串

    Args:
        prefix (str, optional): 要获取的字符串前缀. Defaults to "".
        length (int, optional): 要获取的字符串长度，包括前缀. Defaults to 10.
        characters (str, optional): 随机字符串列表. Defaults to a-zA-Z0-9.

    Returns:
        str: 生成的随机字符串
    """
    prefix_len = len(prefix)
    if prefix_len >= length:
        raise ValueError(
            f'The length of prefix "{prefix}" must be less than length [{length}].'
        )

    random_string = "".join(random.choices(characters, k=length - prefix_len))
    return prefix + random_string


def trimmed_split(
    s: str, seps: str | tuple[str, str] = (";", ","), remove_empty_item=True
) -> list[str]:
    """Given a string s, split is by one of one of the seps."""
    s = s.strip()
    for sep in seps:
        if sep not in s:
            continue
        data = [
            item.strip() for item in s.split(sep) if remove_empty_item and item.strip()
        ]
        return data
    return [item for item in [s] if remove_empty_item and item]


def ensure_a_list(data: Optional[str] | list[str] | tuple[str]) -> list[str]:
    """Ensure data is a list or wrap it in a list"""
    data_list = []
    if not data:
        return []
    if isinstance(data, str):  # 如果输入是字符串
        data_list = trimmed_split(data)
    elif isinstance(data, (list, tuple)):  # 如果输入是列表或元组
        data_list = list(data)
    return data_list


def get_random_str(
    prefix: str = "",
    length: int = 10,
    characters: str = string.ascii_letters + string.digits,
) -> str:
    """生成随机字符串

    Args:
        prefix (str, optional): 要获取的字符串前缀. Defaults to "".
        length (int, optional): 要获取的字符串长度，包括前缀. Defaults to 10.
        characters (str, optional): 随机字符串列表. Defaults to a-zA-Z0-9.

    Returns:
        str: 生成的随机字符串
    """
    prefix_len = len(prefix)
    if prefix_len >= length:
        raise ValueError(
            f'The length of prefix "{prefix}" must be less than length [{length}].'
        )

    random_string = "".join(random.choices(characters, k=length - prefix_len))
    return prefix + random_string


def remove_empty_values(
    obj: list | dict, empty_values: Optional[list] = None
) -> dict | list:
    """移除列表或字典中的空值

    Args:
        obj (list | dict): 要操作的对象
        empty_values (Optional[list], optional): 要移除的空值列表，默认值移除 None. Defaults to None.

    Returns:
        dict | list: 移除空值后的对象
    """
    if empty_values is None:
        empty_values = [None, ""]  # 默认移除 None 和 空字符串
    if isinstance(obj, dict):
        return {
            k: remove_empty_values(v, empty_values)
            for k, v in obj.items()
            if v not in empty_values
        }
    elif isinstance(obj, list):
        return [
            remove_empty_values(item, empty_values)
            for item in obj
            if item not in empty_values
        ]
    else:
        return obj


def split_list_into_chunks(input_list: list, chunk_size=100):
    """
    将一个列表拆分成多个列表,每个列表长度最多 chunk_size。

    参数:
    input_list (list): 需要被拆分的列表
    chunk_size (int): 每个子列表的最大长度,默认为 100

    返回:
    list: 拆分后的子列表组成的列表
    """
    return [
        input_list[i : i + chunk_size] for i in range(0, len(input_list), chunk_size)
    ]
