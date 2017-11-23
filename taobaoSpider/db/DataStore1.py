# -*- coding: utf-8 -*-

from pymongo import *
import time
import datetime

# 店铺宝贝列表和详情
class KeywordItem(object):
    def __init__(self):
        # client = MongoClient("mongodb://192.168.12.28:27017/")
        client = MongoClient("mongodb://localhost:27017/")
        db = client.syjc
        self.begining = long(time.time()) - 1 * 24 * 60 * 60
        self.keyword_item= db.keyword_item

    # 插入店铺所有宝贝,已存在不操作
    def insert_or_update(self, shop_items):
        for shop_item in shop_items:
            if not self.keyword_item.find_one({"crawl_time": {"$gt": self.begining}, "item_id": shop_item['item_id']},
                                               {"item_id": 1}):
                self.keyword_item.insert(shop_item)


 # 用于抓取指定店铺所有宝贝及宝贝规格属性
class ShopAllItemDb1(object):
    def __init__(self):
        client = MongoClient("mongodb://localhost:27017/")
        # client = MongoClient("mongodb://192.168.12.28:27017/")
        db = client.syjc
        self.begining = long(time.time()) - 1 * 24 * 60 * 60
        self.shop_all_item= db.shop_all_item
    # 插入店铺所有宝贝,已存在不操作
    def insert_or_update(self, shop_items):
        for shop_item in shop_items:
            if not self.shop_all_item.find_one({"crawl_time": {"$gt": self.begining}, "item_id": shop_item['item_id']},
                                               {"item_id": 1}):
                self.shop_all_item.insert(shop_item)



