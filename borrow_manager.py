# -*- coding: utf-8 -*-
"""
borrow_manager.py
借阅管理模块：借阅登记、归还处理、逾期查询。
涉及方法：insert_one / update_many / find
"""
from datetime import datetime, timedelta

from mongodb_connect import get_db


def borrow_book(reader_card: str, book_isbn: str, days: int = 30):
    """借阅登记：写入一条借阅流水，状态为'借出'。"""
    doc = {
        "borrow_date": datetime.now(),
        "reader_card": reader_card,
        "book_isbn": book_isbn,
        "status": "借出",
    }
    result = get_db().borrow_logs.insert_one(doc)
    print("借阅登记成功, _id =", result.inserted_id,
          " 应还日期 ≈", (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d"))
    # 同步累加该书的累计借阅次数
    get_db().books.update_one({"isbn": book_isbn}, {"$inc": {"borrow_count": 1}})
    return result


def return_book(reader_card: str, book_isbn: str):
    """归还处理：将'借出'状态更新为'已归还'并记录归还时间。"""
    result = get_db().borrow_logs.update_many(
        {"reader_card": reader_card, "book_isbn": book_isbn, "status": "借出"},
        {"$set": {"status": "已归还", "return_date": datetime.now()}},
    )
    print("归还处理影响 {0} 条记录".format(result.modified_count))
    return result


def query_overdue(days: int = 30):
    """查询逾期未还记录：借出超过 days 天仍为'借出'状态。"""
    deadline = datetime.now() - timedelta(days=days)
    return list(get_db().borrow_logs.find(
        {"status": "借出", "borrow_date": {"$lt": deadline}}
    ))


def list_borrow_logs(condition: dict = None, limit: int = 20):
    """按条件列出借阅流水。"""
    condition = condition or {}
    return list(get_db().borrow_logs.find(condition).limit(limit))


def count_by_status():
    """按状态统计借阅记录数。"""
    return list(get_db().borrow_logs.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))


if __name__ == "__main__":
    print("--- 借阅状态统计 ---")
    for s in count_by_status():
        print("  {0}: {1} 条".format(s["_id"], s["count"]))
#（注：内容由AI生成）
