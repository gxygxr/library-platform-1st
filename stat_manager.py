# -*- coding: utf-8 -*-
"""
stat_manager.py
统计管理模块：分类统计、借阅趋势、畅销榜。
涉及方法：aggregate
"""
from mongodb_connect import get_db


def category_stats():
    """分类统计：按类别分组，统计库存总量、平均价格、图书数量，按库存总量降序。"""
    return list(get_db().books.aggregate([
        {"$group": {
            "_id": "$category",
            "stock_total": {"$sum": "$stock"},
            "avg_price": {"$avg": "$price"},
            "count": {"$sum": 1},
        }},
        {"$sort": {"stock_total": -1}},
    ]))


def borrow_trend():
    """借阅趋势：按年份分组统计借阅量，格式化输出为'YYYY年'。"""
    return list(get_db().borrow_logs.aggregate([
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y年", "date": "$borrow_date"}},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]))


def bestseller(limit: int = 1):
    """畅销榜：取借阅次数最多的图书。"""
    return list(get_db().books.aggregate([
        {"$sort": {"borrow_count": -1}},
        {"$limit": limit},
        {"$project": {"title": 1, "author": 1, "borrow_count": 1, "_id": 0}},
    ]))


def save_category_stats_to_db():
    """将分类统计结果写入 category_stats 集合。"""
    pipeline = [
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "avgRating": {"$avg": "$rating"},
        }},
        {"$merge": {
            "into": "category_stats", "on": "_id",
            "whenMatched": "replace", "whenNotMatched": "insert",
        }},
    ]
    get_db().books.aggregate(pipeline)
    print("分类统计结果已写入 category_stats, 现有 {0} 条".format(
        get_db().category_stats.count_documents({})))


if __name__ == "__main__":
    print("--- 分类统计 ---")
    for c in category_stats():
        print("  {0}: 库存={1} 均价={2:.2f} 数量={3}".format(
            c["_id"], c["stock_total"], c["avg_price"], c["count"]))
    print("--- 借阅趋势 ---")
    for t in borrow_trend():
        print("  {0}: {1} 次".format(t["_id"], t["count"]))
#（注：内容由AI生成）
