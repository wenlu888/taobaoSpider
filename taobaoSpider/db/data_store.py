# -*- coding: utf-8 -*-

from pymongo import *
import time
import datetime

DB_CONNECT_STRING = "mongodb://localhost:27017/"
DB_NAME = "taobaocrawl"


# 店铺卖家中心订单数据
class SalesOrderDb(object):
    def __init__(self):
        client = MongoClient(DB_CONNECT_STRING)
        db = client[DB_NAME]
        self.begining = long(time.time()) - 7 * 24 * 60 * 60
        self.order_info = db.sales_order_info
        self.order_item = db.sales_order_item
        self.shop_all_item_detail = db.shop_all_item_detail

    # def get_real_start_end(self, start, end):
    #     for document in order_item.find({"order_create_time": {"$gte": start, "$lte": end}}, {"order_create_time": 1}) \
    #             .sort("order_create_time", 1).limit(1):
    #         start = long(document['order_create_time'])
    #     return start, end

    def get_order_count_start_end(self, start, end):
        return self.order_info.find({"order_create_time": {"$gte": start, "$lte": end}},
                                    {"order_create_time": 1}).count()

    # 获取指定时间段内的所有tradeid
    def get_trade_id_set(self, start, end):
        item_ids = []
        for document in self.order_item.find({"order_create_time": {"$gt": start, "$lte": end}}, {"trade_id": 1}):
            item_ids.append(document['trade_id'])
        return set(item_ids)

    def get_order_id_set(self, start, end):
        order_ids = []
        for document in self.order_info.find({"order_create_time": {"$gt": start, "$lte": end}}, {"order_id": 1}):
            order_ids.append(document['order_id'])
        return set(order_ids)

    def order_info_upsert(self, order_total):
        for order in order_total:  # 重复不插入
            self.order_info.replace_one({'order_id': order['order_id']}, order, upsert=True)

    def item_upsert(self, item_total):
        for item in item_total:
            self.order_item.replace_one({'trade_id': item['trade_id']}, item, upsert=True)

    def get_item_trade_id(self):
        return self.order_item.find_one({"item_id": None}, {"item_url": 1, "img_sign": 1})

    def update_item_same_img(self, item_id, img_sign):
        return self.order_item.update({"img_sign": img_sign}, {'$set': {"item_id": item_id}}, multi=True)

    # 根据图片规格签名匹配宝贝
    def match_item_id(self):
        for detail in self.order_item.find({'item_id': {'$exists': False}, 'img_sign': {"$ne": None}},
                                           {'img_sign': 1, 'order_id': 1}):
            try:
                match = self.shop_all_item_detail.find_one(
                        {'$or': [{'颜色分类': {'$regex': detail['img_sign'], '$options': 'i'}},
                                 {'尺码': {'$regex': detail['img_sign'], '$options': 'i'}}]},
                        {'item_id': 1, 'shop_id': 1})
            except Exception, e:
                print(e.message)
            if match:
                self.order_item.update({'_id': detail['_id']},
                                       {"$set": {"item_id": match['item_id'], "shop_id": match['shop_id']}})
                self.order_info.update({'order_id': detail['order_id']}, {"$set": {"shop_id": match['shop_id']}})
                print(match['item_id'])

    def unset_item_id(self):
        self.order_item.update({}, {'$unset': {'item_id': 1}}, multi=True)


# 店铺宝贝列表和详情
class ShopAllItemDb(object):
    def __init__(self):
        client = MongoClient("mongodb://localhost:27017/")
        db = client.taobaocrawl
        self.begining = long(time.time()) - 7 * 24 * 60 * 60
        self.shop_all_item = db.shop_all_item
        self.shop_all_item_detail = db.shop_all_item_detail

    # 格式化抓取时间对于特定间隔内的所有抓取的数据抓取时间都统一起来方便操作
    def format_data(self, shop_id, is_details):
        col = self.shop_all_item if is_details else self.shop_all_item_detail
        last = list(col.find({"shop_id": shop_id}, {"shop_id": 1, "crawl_time": 1}) \
                    .sort("crawl_time", ASCENDING).limit(1))
        if last:
            last_time = datetime.datetime.fromtimestamp(last[0]['crawl_time'])
            format_time = long(time.mktime(
                    time.strptime(datetime.datetime.strftime(last_time, "%Y-%m-%d 00:00:01"), '%Y-%m-%d %H:%M:%S')))
            start = format_time - 1
            end = long(time.mktime(
                    time.strptime(datetime.datetime.strftime(last_time, "%Y-%m-%d 23:59:59"), '%Y-%m-%d %H:%M:%S')))
            col.update({"crawl_time": {"$gt": start, "$lte": end}, "shop_id": shop_id},
                       {"$set": {"crawl_time": format_time}}, multi=True)

    # 插入店铺所有宝贝,已存在不操作
    def insert_or_update(self, shop_items):
        for shop_item in shop_items:
            if not self.shop_all_item.find_one({"crawl_time": {"$gt": self.begining}, "item_id": shop_item['item_id']},
                                               {"item_id": 1}):
                self.shop_all_item.insert(shop_item)

    # 插入宝贝详情,已存在忽略
    def insert_or_update_details(self, item_details):
        if not self.shop_all_item_detail.find_one(
                {"crawl_time": {"$gt": self.begining}, "item_id": item_details['item_id']},
                {"item_id": 1}):
            self.shop_all_item_detail.insert(item_details)

    # 获取指定店铺的所有宝贝id
    def get_shop_item_ids(self, shop_id):
        return list(self.shop_all_item.find({"crawl_time": {"$gt": self.begining}, "shop_id": shop_id},
                                            {"item_id": 1}))

    # 是否已经存在该宝贝的属性详情
    def exist_item(self, item_id):
        return self.shop_all_item_detail.find_one({"crawl_time": {"$gt": self.begining}, "item_id": item_id},

                                                  {"item_id": 1})

    # 获取指定时间段内的所有shop_id
    def get_all_shop_id(self, start=None, end=None):
        if not start or not end:
            return list(self.shop_all_item.find({}).distinct("shop_id"))
        else:
            return list(self.shop_all_item.find({"crawl": {"$gt": start, "$lt": end}}).distinct("shop_id"))
