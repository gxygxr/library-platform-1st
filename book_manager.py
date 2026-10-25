# -*- coding: utf-8 -*-
"""
book_manager.py
图书管理模块：图书增删改查、条件检索、评分排行。
涉及方法：insert_one / insert_many / find / find_one / update_one / delete_one / delete_many
"""
from mongodb_connect import get_db


def insert_one_book(doc: dict):
    """录入单本图书，返回插入结果。"""
    result = get_db().books.insert_one(doc)
    print("已录入图书, 自动生成的 _id =", result.inserted_id)
    return result


def insert_many_books(docs: list):
    """批量录入多本图书，返回插入条数。"""
    result = get_db().books.insert_many(docs)
    print("已批量录入 {0} 本图书".format(len(result.inserted_ids)))
    return result


def find_book_by_isbn(isbn: str):
    """按 ISBN 精确查找。"""
    return get_db().books.find_one({"isbn": isbn})


def find_books(condition: dict, projection=None, limit=0):
    """按条件检索图书，可选投影与条数限制。"""
    return list(get_db().books.find(condition, projection).limit(limit))


def search_books(condition: dict):
    """条件组合检索：多条件、$in、$regex、标签等。
    返回 (匹配列表, 条数)。
    """
    cursor = get_db().books.find(condition)
    docs = list(cursor)
    return docs, len(docs)


def rating_top(n: int = 5):
    """按评分降序取前 n 本图书排行。"""
    return list(get_db().books.find().sort("rating", -1).limit(n))


def update_book(isbn: str, update: dict):
    """更新一本图书，返回受影响文档数。"""
    result = get_db().books.update_one({"isbn": isbn}, update)
    print("更新图书 matched={0}, modified={1}".format(
        result.matched_count, result.modified_count))
    return result


def delete_book(isbn: str):
    """按 ISBN 删除一本图书，返回删除条数。"""
    result = get_db().books.delete_one({"isbn": isbn})
    print("删除图书 {0} 本".format(result.deleted_count))
    return result


def delete_books(condition: dict):
    """按条件批量删除图书，返回删除条数。"""
    result = get_db().books.delete_many(condition)
    print("按条件删除图书 {0} 本".format(result.deleted_count))
    return result


if __name__ == "__main__":
    # 模块自测
    print("--- 按 ISBN 查找 ---")
    b = find_book_by_isbn("9787115428028")
    print("  书名:", b["title"] if b else "未找到")
    print("--- 评分排行前 5 ---")
    for i, bk in enumerate(rating_top(5), 1):
        print("  {0}. {1}  评分={2}".format(i, bk["title"], bk["rating"]))
#（注：内容由AI生成）
