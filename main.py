# -*- coding: utf-8 -*-
"""
main.py
主程序：菜单式交互程序，串联各功能模块。
启动时打印数据库连接状态与各集合文档总数；退出前关闭连接。
"""
import sys

from mongodb_connect import get_client
import book_manager
import reader_manager
import borrow_manager
import stat_manager

MENU = """
========== 图书情报检索与统计平台 ==========
 1. 按书名/ISBN 检索图书
 2. 组合条件检索图书（类别+价格范围）
 3. 图书评分排行榜（前 5）
 4. 录入一本新图书
 5. 更新图书库存
 6. 删除一本图书
 7. 读者学院/等级统计
 8. 分类统计（库存/均价/数量）
 9. 借阅趋势（按年份）
10. 借阅登记
11. 归还处理
12. 畅销榜（借阅次数最多）
 0. 退出
===========================================
请选择操作 [0-12]: """


def startup():
    """启动信息：连接状态与各集合文档总数。不关闭连接，由主流程在退出时统一关闭。"""
    db = get_client()["library"]
    print("数据库连接成功 -> {0}:{1}/{2}".format(
        "127.0.0.1", 27017, "library"))
    for name in ["books", "readers", "borrow_logs", "category_stats"]:
        print("  集合 {0}: {1} 条文档".format(name, db[name].count_documents({})))


def show_list(docs, title):
    """统一打印结果列表；无结果时给出明确提示。"""
    if not docs:
        print("[提示] 未查询到任何记录。")
        return
    print(title)
    for d in docs:
        print("  -", d)


def main():
    startup()
    client = get_client()  # 持有共享连接，退出时统一关闭
    while True:
        try:
            choice = input(MENU).strip()
        except (EOFError, KeyboardInterrupt):
            choice = "0"
        if choice == "0":
            break
        elif choice == "1":
            kw = input("请输入书名关键词或ISBN: ").strip()
            docs, n = book_manager.search_books(
                {"$or": [{"title": {"$regex": kw}}, {"isbn": kw}]})
            show_list(docs, "检索到 {0} 本图书：".format(n))
        elif choice == "2":
            cat = input("请输入类别(直接回车跳过): ").strip()
            try:
                low = float(input("最低价格(直接回车跳过): ") or "-inf")
                high = float(input("最高价格(直接回车跳过): ") or "inf")
            except ValueError:
                print("[提示] 价格输入无效，已忽略价格条件。")
                low, high = float("-inf"), float("inf")
            cond = {"price": {"$gte": low, "$lte": high}}
            if cat:
                cond["category"] = cat
            docs, n = book_manager.search_books(cond)
            show_list(docs, "组合检索到 {0} 本图书：".format(n))
        elif choice == "3":
            show_list(book_manager.rating_top(5), "图书评分排行榜(前5)：")
        elif choice == "4":
            isbn = input("ISBN: ").strip()
            title = input("书名: ").strip()
            author = input("作者: ").strip()
            category = input("类别: ").strip()
            try:
                price = float(input("定价: ").strip())
                stock = int(input("库存: ").strip())
                rating = float(input("评分(0-5): ").strip() or "3.0")
            except ValueError:
                print("[提示] 数值输入有误，本次录入取消。")
                continue
            book_manager.insert_one_book({
                "isbn": isbn, "title": title, "author": author,
                "category": category, "price": price, "stock": stock,
                "rating": rating, "tags": [], "borrow_count": 0,
            })
        elif choice == "5":
            isbn = input("请输入图书ISBN: ").strip()
            try:
                delta = int(input("库存增减量(正数增加/负数减少): ").strip())
            except ValueError:
                print("[提示] 输入无效。")
                continue
            book_manager.update_book(isbn, {"$inc": {"stock": delta}})
        elif choice == "6":
            isbn = input("请输入要删除的图书ISBN: ").strip()
            book_manager.delete_book(isbn)
        elif choice == "7":
            print("--- 学院统计 ---")
            for c in reader_manager.college_stats():
                print("  {0}: {1} 人".format(c["_id"], c["count"]))
            print("--- 等级分布 ---")
            for lv in reader_manager.level_distribution():
                print("  {0}: {1} 人".format(lv["_id"], lv["count"]))
        elif choice == "8":
            show_list(stat_manager.category_stats(),
                      "分类统计(按库存总量降序)：")
        elif choice == "9":
            show_list(stat_manager.borrow_trend(), "借阅趋势(按年份)：")
        elif choice == "10":
            card = input("借阅证号: ").strip()
            isbn = input("图书ISBN: ").strip()
            borrow_manager.borrow_book(card, isbn)
        elif choice == "11":
            card = input("借阅证号: ").strip()
            isbn = input("图书ISBN: ").strip()
            borrow_manager.return_book(card, isbn)
        elif choice == "12":
            show_list(stat_manager.bestseller(5), "畅销榜(借阅次数Top5)：")
        else:
            print("[提示] 无效选项，请重新选择。")

    if client:
        client.close()
    print("已关闭数据库连接，程序退出。")


if __name__ == "__main__":
    main()
#（注：内容由AI生成）
