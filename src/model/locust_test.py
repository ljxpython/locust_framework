from peewee import *

from src.model.modelsbase import BaseModel, database

"""

locust 压测

"""


class LocustFunc(BaseModel):
    """
    moudle: test_demo
    case_path: locustfiles/test_demo/get_good.py
    case_sence: get_good
    path_desc: 根据压测的内容,填写适合名字
    tags: 标签,暂时没有其他使用场景


    """

    moudle = CharField(max_length=100, verbose_name="所属模块")
    case_path = CharField(
        max_length=100,
        null=False,
        verbose_name="接口所在的位置,用于执行case",
        unique=True,
    )
    # case_sence 其实就是py的文件名
    case_sence = CharField(max_length=100, null=False, verbose_name="case场景")
    path_desc = TextField(null=True, verbose_name="接口描述")
    tags = CharField(max_length=100, null=True, verbose_name="标签")


class LocustShape(BaseModel):
    """
    压测的负载形状
    shape_name: 压测的shape名称
    shape_desc: 压测的shape描述
    shape_path: 压测的shape路径
    e.g:
    shape_name: hign_shape
    shape_desc: 峰压测
    shape_path: /data/locustfiles/shape/hign_shape.py
    """

    shape_name = CharField(max_length=100, verbose_name="压测的shape名称", unique=True)
    shape_desc = TextField(verbose_name="压测的shape描述")
    shape_path = CharField(max_length=100, verbose_name="压测的shape路径")


class LocustSuite(BaseModel):
    suite_name = CharField(max_length=100, verbose_name="套件名称", unique=True)
    describe = TextField(verbose_name="套件描述", null=True)
    # 需要执行的case集
    case_ids = TextField(verbose_name="需要执行的case集", null=True)
    case_sences = TextField(verbose_name="需要执行的case场景集")


class LocustTestResult(BaseModel):
    # 标题
    title = CharField(max_length=100, null=True, verbose_name="测试报告标题",unique=True)
    # 外键 suite_name
    locustsuite = ForeignKeyField(LocustSuite, verbose_name="suite_name")
    # 运行的状态 0 代表运行中 1 代表流程结束
    status = IntegerField(null=True, default=0, verbose_name="运行状态")
    # 测试结果 成功,失败,部分失败,这部分暂时预留出来
    result = CharField(max_length=100, null=True, verbose_name="测试结果")
    # 测试报告链接
    report_link = CharField(max_length=1000, null=True, verbose_name="测试报告链接")
    # 测试报告下载地址
    report_download = CharField(
        max_length=1000, null=True, verbose_name="测试报告下载地址"
    )
    # 上一次测试报告的id
    last_report_id = IntegerField(null=True, verbose_name="上一次测试报告的id")
    # result_desc = TextField(max_length=1000, null=True, verbose_name="测试结果描述")
    # 测试类型 定时 webhook 手动
    # 预留字段,展示都是手动
    test_type = CharField(max_length=100, null=True, verbose_name="测试类型")
    # 测试环境 线上线下
    test_env = CharField(max_length=100, null=True, verbose_name="测试环境")
    # task_id
    task_id = CharField(max_length=100, null=True, verbose_name="任务id")
    # shape_name
    shape_name = CharField(max_length=100, null=True, verbose_name="shape_name")
    # port locust启动的端口
    port = IntegerField(null=True, default=8090,verbose_name="locust启动的端口")
    # headless 是否是无头模式
    headless = BooleanField(null=True, verbose_name="是否是无头模式",default=False)
    # 是否是分布式
    distributed = BooleanField(null=True, verbose_name="是否是分布式",default=False)
    # 分布式节点
    nodes = TextField(null=True, verbose_name="分布式节点")
    # 增速
    spawn_rate = FloatField(null=True, verbose_name="spawn-rate")
    # 并发数
    users = IntegerField(null=True, verbose_name="users")
    # 标签
    tags = CharField(max_length=100, null=True, verbose_name="标签")
    exclude_tags = CharField(max_length=100, null=True, verbose_name="排除标签")
    run_time = CharField(max_length=100, null=True, verbose_name="运行时间")




if __name__ == "__main__":
    # 删除表
    database.drop_tables(
        [LocustTestResult, LocustSuite, LocustFunc, LocustShape],
    )
    # 创建表
    database.create_tables(
        [LocustTestResult, LocustSuite, LocustFunc, LocustShape],
    )
