# -*- coding: utf-8 -*-
"""
mongodb_connect.py
数据库连接模块：封装获取 MongoDB 连接的逻辑，供后续所有程序文件调用。
连接参数在本模块内统一定义。
"""
from pymongo import MongoClient

# 连接参数（与实训环境实际配置一致：端口 27017，启用访问控制后使用读写账号）
HOST = "127.0.0.1"
PORT = 27017
DATABASE = "library"
USERNAME = "libWriter"      # 读写账号（角色 readWrite + dbAdmin）
PASSWORD = "Writer@123"     # 实训演示密码（@ 在 URL 中需编码为 %40，这里用显式参数无需编码）

_CLIENT = None  # 模块级缓存，避免多次调用重复建连


def get_client() -> MongoClient:
    """建立并返回 MongoClient 连接（显式参数，规避连接串转义问题）。
    同一进程内复用同一个连接对象。
    """
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = MongoClient(
            host=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            authSource="admin",  # 账号建立在 admin 库上
        )
        _CLIENT.admin.command("ping")
    return _CLIENT


def get_db():
    """返回业务数据库实例。"""
    return get_client()[DATABASE]


if __name__ == "__main__":
    client = get_client()
    db = client[DATABASE]
    print("数据库连接成功 -> mongodb://{host}:{port}/{db}".format(
        host=HOST, port=PORT, db=DATABASE))
    for name in ["books", "readers", "borrow_logs", "category_stats"]:
        print("  集合 {0}: {1} 条文档".format(name, db[name].count_documents({})))
    client.close()
