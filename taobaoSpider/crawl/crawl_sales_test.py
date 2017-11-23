# -*- coding: utf-8 -*-

# 用于抓取买家后台订单


import json
from utils.driver_utils import ChromeDriver
from db.DataStore import *
from utils.html_downloader import Html_Downloader

import time
import datetime
from time import sleep
import re
import random
import chardet


def logandprint(message):
    message = message.decode('utf-8') if chardet.detect(message)['encoding'] == "utf-8" else message
    url = "%s  %s" % (datetime.datetime.now().strftime('%H:%M:%S'), message)
    print(url)


def getTotalPage(url_params, agent_ip, cookie_dict, start, end):
    total_page = 0
    try:
        ok, result = Html_Downloader.Download_Html(url,
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
    except Exception, e:
        pass
    return total_page


def parseSalesJson(order_json, start, end):
    order_ids = GetOrderIdSet(start, end)
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
    item_upsert(item_total)
    order_info_upsert(order_total)


# file = open("C:\\saleitem\\sales.txt", "r")
# content = file.read()
# order_json = json.loads(content.decode('GB2312').replace("\n", "").replace("\r", ""))

# start, end = get_real_start_end(start, end)



driver = ChromeDriver()
cookies = driver.login_an_get('英语二油条:推广', 'tuiguang654321')
sleep(2)
driver.quite()

#cookies = "857889334_euacm_ac_rs_uid_=78550821;tracknick=;_tb_token_=7ee53d5ef47d1;_umdata=2FB0BDB3C12E491D79FE816B95DDE50F55EEEFE8215631799F2A199DC32EAD55094DAD91D7C44BCECD43AD3E795C914C37D9160ADE24EDB9871B5B941249D7DD;x=78550821;isg=ArS04zgtUYkwFsVFBLdyEiu_hXLmJdQ2athRjE4Vmz_CuVADdpxZBna5T4ab;uss=V3pPi81krXypXqhUksc%2B5xerjbcKi2gmyJR%2Fi%2FHA7z%2Fdz2eF521vApfn;uc3=sg2=AVAJ%2F%2FuFgrZrwbvpPwMpeUNJWGnNVTEcpZhNLKPoZwE%3D&nk2=&id2=&lg2=;uc1=cookie14=UoTcDzZtyXcULg%3D%3D&lng=zh_CN;sn=%E8%8B%B1%E8%AF%AD%E4%BA%8C%E6%B2%B9%E6%9D%A1%3A%E6%8E%A8%E5%B9%BF;skt=b49042353c0b3f36;_euacm_ac_rs_sid_=64469556;unb=857889334;t=6d64317aee4c9f7d89ffe69c8160eb8c;cookie2=14103bb697886fba8c46182bcf65b191;v=0;cna=wej1EZzmfyACAQ4XY4PoZcqz;_euacm_ac_l_uid_=857889334;857889334_euacm_ac_c_uid_=78550821;_portal_version_=new;_lastvisited=wej1EZzmfyACAQ4XY4PoZcqz%2C%2Cwej1EZzmfyACAQ4XY4PoZcqzZZWSABOt%2Cj5amfert%2Cj5amfert%2C1%2Cac5c43a4%2Cwej1EZzmfyACAQ4XY4PoZcqz%2Cj5amferu"

params = "action=itemlist/SoldQueryAction" \
         "&auctionType=0&buyerNick=&close=0&dateBegin={start}054" \
         "&dateEnd={end}659&logisticsService=&orderStatus=SUCCESS&" \
         "pageNum={page_num}&pageSize={page_size}&queryMore={query_more}&queryOrder=desc&rateStatus=&" \
         "refund=&rxAuditFlag=0&rxHasSendFlag=0&rxOldFlag=0&rxSendFlag=0&rxSuccessflag=0&" \
         "sellerNick=&tabCode=success&tradeTag=0&useCheckcode=false&useOrderInfo=false&" \
         "errorCheckcode=false&prePageNo={pre_page}"
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in cookies.split(';')}

# 时间切分成一个个时间段,切割粒度为小时,
# 每段时间采之前对比数据库跟服务器的数量差距,
# 差距在5条以内的不再采这天的数据
hour_interval = 24  # 24小时检查一次

start_date = datetime.datetime.strptime("%s 00:00:00" % "2017-06-01", "%Y-%m-%d 00:00:00")
end_date = datetime.datetime.strptime("%s 00:00:00" % "2017-06-03", "%Y-%m-%d 00:00:00")
end_date + datetime.timedelta(days=1)

start = long(time.mktime(start_date.timetuple()))
final_end = long(time.mktime(end_date.timetuple()))
end = start + (hour_interval * 3600)
agent_ip = None  # 不能使用代理ip
# agent_ip = Utils.GetAgentIp()
while end <= final_end:

    url = "https://trade.taobao.com/trade/itemlist/asyncSold.htm?event_submit_do_query=1&_input_charset=utf8"
    url_params = params.format(page_num=1, page_size=1, start=start, end=end, pre_page=1, query_more='true')
    page_size = 100
    total = getTotalPage(url_params, agent_ip, cookie_dict, start, end)
    print(total)
    exit()
    sleep(random.randint(1, 2))
    totalpage = 0
    exist_count = get_order_count_start_end(start, end)
    if total and total > exist_count and (total - exist_count) > 5:
        totalpage = total / page_size
        if total % page_size:
            totalpage += 1
        logandprint("正在抓取从%s到%s的订单数据共%s条,分%s页获取" % (
            datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end), total, totalpage))
    elif total:
        logandprint("从%s到%s订单数据已抓取完毕(服务端%s,数据库%s)" % (
            datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end), total, exist_count))

    for i in range(totalpage):
        page_num = i + 1
        logandprint("正在抓取第%s页..." % page_num)
        url_params = params.format(page_num=page_num, page_size=page_size, start=start, end=end, pre_page=1,
                                   query_more='true')
        ok, result = Html_Downloader.Download_Html(url,
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
                logandprint("Error:%s,result:%s" % (e.message, result.text))
            parseSalesJson(order_json, start, end)
        else:
            logandprint(
                    "抓取从%s到%s的订单数据第%s页数据失败:%s" % (
                        datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end), page_num, result))
        sec = random.randint(15, 40)
        logandprint("等待%s秒...." % sec)
        sleep(sec)
    logandprint(
            "抓取从%s到%s的订单数据共%s条完成" % (
                datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end), total))
    start = end
    end = start + (hour_interval * 3600)
