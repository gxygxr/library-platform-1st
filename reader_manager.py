# -*- coding: utf-8 -*-
"""
reader_manager.py
读者管理模块：读者信息管理、学院统计、等级分布。
涉及方法：find / count_documents / distinct
"""
from mongodb_connect import get_db


def find_reader(card_no: str):
    """按借阅证号查找读者。"""
    return get_db().readers.find_one({"card_no": card_no})


def list_readers(condition: dict = None):
    """按条件列出读者，返回 (列表, 条数)。"""
    condition = condition or {}
    docs = list(get_db().readers.find(condition))
    return docs, len(docs)


def update_reader(card_no: str, update: dict):
    """更新读者信息，返回受影响文档数。"""
    result = get_db().readers.update_one({"card_no": card_no}, update)
    print("更新读者 matched={0}, modified={1}".format(
        result.matched_count, result.modified_count))
    return result


def college_stats():
    """按学院统计读者数量。"""
    return list(get_db().readers.aggregate([
        {"$group": {"_id": "$college", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]))


def level_distribution():
    """按借阅等级统计读者数量。"""
    return list(get_db().readers.aggregate([
        {"$group": {"_id": "$level", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]))


def total_readers() -> int:
    """读者总数。"""
    return get_db().readers.count_documents({})


def distinct_colleges():
    """获取全部学院清单。"""
    return get_db().readers.distinct("college")


if __name__ == "__main__":
    print("读者总数:", total_readers())
    print("--- 学院统计 ---")
    for c in college_stats():
        print("  {0}: {1} 人".format(c["_id"], c["count"]))
    print("--- 等级分布 ---")
    for lv in level_distribution():
        print("  {0}: {1} 人".format(lv["_id"], lv["count"]))
#（注：内容由AI生成）
