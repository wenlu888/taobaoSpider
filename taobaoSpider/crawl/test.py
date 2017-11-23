# -*- coding: utf-8 -*-
# 用于抓取买家后台订单
import json
from utils.driver_utils import ChromeDriver
from db.data_store import *
from utils.html_downloader import Html_Downloader
import time
import datetime
from time import sleep
import re
import random
import chardet
from config import SAVE_SALES_ITEMS_INFO_API, GET_SALES_ORDER_CNT_API, \
    SAVE_SALES_ORDER_INFO_API, GET_SALES_ORDER_IDS_API, GET_SALES_TRADE_IDS_API
class CrawlSales(object):
    def __init__(self, data):
        if data['start_str']:
            self.start_date = datetime.datetime.strptime("%s 00:00:00" % data['start_str'], "%Y-%m-%d 00:00:00")
        if data['end_str']:
            self.end_date = datetime.datetime.strptime("%s 00:00:00" % data['end_str'],
                                                       "%Y-%m-%d 00:00:00") + datetime.timedelta(days=1)

        self.account_name = data['account_name'] if data['account_name'] else None
        self.account_pwd = data['account_pwd'] if data['account_pwd'] else None

        self.url = "https://trade.taobao.com/trade/itemlist/asyncSold.htm?event_submit_do_query=1&_input_charset=utf8"

        self.params = "action=itemlist/SoldQueryAction" \
                      "&auctionType=0&buyerNick=&close=0&dateBegin={start}054" \
                      "&dateEnd={end}659&logisticsService=&orderStatus=SUCCESS&" \
                      "pageNum={page_num}&pageSize={page_size}&queryMore={query_more}&queryOrder=desc&rateStatus=&" \
                      "refund=&rxAuditFlag=0&rxHasSendFlag=0&rxOldFlag=0&rxSendFlag=0&rxSuccessflag=0&" \
                      "sellerNick=&tabCode=success&tradeTag=0&useCheckcode=false&useOrderInfo=false&" \
                      "errorCheckcode=false&prePageNo={pre_page}"
        self.db = SalesOrderDb()

    def log_and_print(self, message):
        message = message.decode('utf-8') if chardet.detect(message)['encoding'] == "utf-8" else message
        url = "%s  %s" % (datetime.datetime.now().strftime('%H:%M:%S'), message)
        print(url)

    def upload_data(self, data, is_item=False):
        if is_item:
            url = SAVE_SALES_ITEMS_INFO_API
        else:
            url = SAVE_SALES_ORDER_INFO_API
        post_data = "account_name=%s&data=%s" % (self.account_name, json.dumps(data))

        if not self.process_request(url, post_data):
            sleep(3)
            self.process_request(url, post_data)

    def process_request(self, url, data):
        result_ok = False
        ok, result = Html_Downloader.Download_Html(url, {item.split('=')[0]: item.split('=')[1] for item in
                                                         data.split('&')}, {}, post=True)
        if ok:
            result_json = json.loads(result.content)
            result_ok = bool(result_json['flag'])
            self.log_and_print(result_json['message'])
        else:
            self.log_and_print(result)
        return result_ok

    def get_id_set(self, start, end, trade_id=False):
        if trade_id:
            url = GET_SALES_TRADE_IDS_API
        else:
            url = GET_SALES_ORDER_IDS_API
        trade_id = []
        post_data = "account_name=%sstart=%s&end=%s" % (self.account_name, start, end)

        ok, result = Html_Downloader.Download_Html(url, {item.split('=')[0]: item.split('=')[1] for item in
                                                         post_data.split('&')}, {}, post=True)
        if ok:
            result_json = json.loads(result.content)
            if bool(result_json['flag']):
                trade_id = set(result_json['data'])
            self.log_and_print(result_json['message'])
        else:
            self.log_and_print(result)
            self.log_and_print("获取id列表失败")
        return trade_id

    def get_sales_cnt(self, start, end):
        url = GET_SALES_ORDER_CNT_API
        trade_id = []
        post_data = "account_name=%sstart=%s&end=%s" % (self.account_name, start, end)

        ok, result = Html_Downloader.Download_Html(url, {item.split('=')[0]: item.split('=')[1] for item in
                                                         post_data.split('&')}, {}, post=True)
        if ok:
            result_json = json.loads(result.content)
            if bool(result_json['flag']):
                trade_id = set(result_json['data'])
            self.log_and_print(result_json['message'])
        else:
            self.log_and_print(result)
            self.log_and_print("获取id列表失败")
        return trade_id


def get_total_page(self, url_params, agent_ip, cookie_dict, start, end):
    total_page = 0
    try:
        ok, result = Html_Downloader.Download_Html(self.url,
                                                   {item.split('=')[0]: item.split('=')[1] for item in
                                                    url_params.split('&')},
                                                   {"cookies": cookie_dict,
                                                    "ip": agent_ip,
                                                    "Referer": "https://trade.taobao.com/trade/itemlist/list_sold_items.htm?action=itemlist/SoldQueryAction&event_submit_do_query=1&auctionStatus=SUCCESS&tabCode=success"
                                                    }, post=True)
        if ok:
            order_json = json.loads(result.text.replace("\n", "").replace("\r", ""))
            if order_json.has_key('page'):
                total_page = int(order_json['page']['totalNumber'])
        else:
            print(result)
    except:
        pass
    return total_page


def parse_sales_json(self, order_json, start, end):
    order_ids = self.db.get_order_id_set(start, end)
    item_ids = []
    order_total = []
    item_total = []
    if order_json.has_key('mainOrders') and len(order_json['mainOrders']):
        for order in order_json['mainOrders']:
            if order['orderInfo']['id'] not in order_ids:
                t_order = {}
                t_order['order_id'] = order['orderInfo']['id']
                t_order['buyer_id'] = order['buyer']['id']
                t_order['buyer_nick'] = order['buyer']['nick']
                t_order['actual_fee'] = order['payInfo']['actualFee']
                if order['payInfo'].has_key('icons'):
                    t_order['other_pay_info'] = ';'.join(i['linkTitle'] for i in order['payInfo']['icons'])
                t_order['item_count'] = len(order['subOrders'])
                t_order['post_type'] = order['payInfo']['postType']
                t_order['order_create_time'] = long(
                        time.mktime(time.strptime(order['orderInfo']['createTime'], "%Y-%m-%d %H:%M:%S")))
                order_total.append(t_order)
            t_order_items = []
            for item in order['subOrders']:
                tradeId = re.compile("\?tradeID=(.*?)(?=&)").findall(item['itemInfo']['itemUrl'])[0]
                if tradeId not in item_ids:
                    t_item = {}
                    t_item['order_create_time'] = long(
                            time.mktime(time.strptime(order['orderInfo']['createTime'], "%Y-%m-%d %H:%M:%S")))
                    t_item['trade_id'] = tradeId
                    t_item['img_sign'] = re.compile("/([^/]*)(?=_!!)").findall(item['itemInfo']['pic'])[
                        0] if re.compile("/([^/]*)(?=_!!)").findall(item['itemInfo']['pic']) else None
                    t_item['item_url'] = item['itemInfo']['itemUrl']
                    t_item['order_id'] = order['orderInfo']['id']
                    t_item['item_title'] = item['itemInfo']['title']
                    t_item['sku_type'] = ';'.join(
                            "%s:%s" % (i['name'], i['value']) for i in item['itemInfo']['skuText'])
                    t_order_items.append(t_item)
            item_total = item_total + t_order_items
    self.db.item_upsert(item_total)
    self.db.order_info_upsert(order_total)


def crawl_sales(self, finish_handler):
    driver = ChromeDriver()
    cookie_dic, cookies = driver.login_an_get(self.account_name, self.account_pwd)
    sleep(2)
    driver.quite()

    cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in cookies.split(';')}

    # 时间切分成一个个时间段,切割粒度为小时,
    # 每段时间采之前对比数据库跟服务器的数量差距,
    # 差距在5条以内的不再采这天的数据
    hour_interval = 24  # 24小时检查一次

    # start_date = datetime.datetime.strptime("%s 00:00:00" % "2017-06-01", "%Y-%m-%d 00:00:00")
    # end_date = datetime.datetime.strptime("%s 00:00:00" % "2017-06-03", "%Y-%m-%d 00:00:00")
    # end_date + datetime.timedelta(days=1)

    start = long(time.mktime(self.start_date.timetuple()))
    final_end = long(time.mktime(self.end_date.timetuple()))
    end = start + (hour_interval * 3600)
    agent_ip = None
    while end <= final_end:

        url_params = self.params.format(page_num=1, page_size=1, start=start, end=end, pre_page=1,
                                        query_more='true')
        page_size = 100
        total = self.get_total_page(url_params, agent_ip, cookie_dict, start, end)

        sleep(random.randint(1, 2))
        totalpage = 0
        exist_count = self.db.get_order_count_start_end(start, end)
        if total and total > exist_count and (total - exist_count) > 5:
            totalpage = total / page_size
            if total % page_size:
                totalpage += 1
            self.log_and_print("正在抓取从%s到%s的订单数据共%s条,分%s页获取" % (
                datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end), total, totalpage))
        elif total:
            self.log_and_print("从%s到%s订单数据已抓取完毕(服务端%s,数据库%s)" % (
                datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end), total, exist_count))

        for i in range(totalpage):
            page_num = i + 1
            self.log_and_print("正在抓取第%s页..." % page_num)
            url_params = self.params.format(page_num=page_num, page_size=page_size, start=start, end=end,
                                            pre_page=1,
                                            query_more='true')
            ok, result = Html_Downloader.Download_Html(self.url,
                                                       {item.split('=')[0]: item.split('=')[1] for item in
                                                        url_params.split('&')},
                                                       {"cookies": cookie_dict,
                                                        "ip": agent_ip,
                                                        "Referer": "https://trade.taobao.com/trade/itemlist/list_sold_items.htm?action=itemlist/SoldQueryAction&event_submit_do_query=1&auctionStatus=SUCCESS&tabCode=success"
                                                        }, post=True)
            if ok and "mainOrders" in result.text:
                try:
                    order_json = json.loads(result.text.replace("\r", "").replace("\n", ""))
                except Exception, e:
                    self.log_and_print("Error:%s,result:%s" % (e.message, result.text))
                self.parse_sales_json(order_json, start, end)
            else:
                self.log_and_print(
                        "抓取从%s到%s的订单数据第%s页数据失败:%s" % (
                            datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end), page_num,
                            result))
            sec = random.randint(15, 40)
            self.log_and_print("等待%s秒...." % sec)
            sleep(sec)
        self.log_and_print(
                "抓取从%s到%s的订单数据共%s条完成" % (
                    datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end), total))
        start = end
        end = start + (hour_interval * 3600)
    finish_handler()
