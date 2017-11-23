# -*- coding: utf-8 -*-
# ---------------------------
# 脚本效果：将竞店爬取改为多线程执行，因为将序列化过程写入数据获取中所以没有对执行过程进行线程（锁处理）
# 已将竞店获取和存储流程化
# 注意：爬取月销量需要登录后店铺cookie，可用时间约1天左右。
# ---------------------------
from utils.utils import Utils
import time
from datetime import datetime
from utils.html_downloader import Html_Downloader
from time import sleep
import re
import json
import sys
import logging
import Queue
import threading
from config import SAVE__INSERT_API
from config import SAVE__INSERT_API_ZS
import requests
today = str(datetime.today()).split(' ')[0]
default_encoding = 'utf-8'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='E:\wenlu\Log\{name}.log'.format(name=today+" crwalTmall"),
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
# 创建队列将店铺放入队列中进行多线程
SHARE_Q = Queue.Queue()
# 设置线程个数
_WORKER_THREAD_NUM = 7


class CrawlShopItemDetails(object):
    def __init__(self, shop_url, shop_id, shop_name):
        self.shop_url = shop_url
        self.shop_id = shop_id
        self.shop_name = shop_name

    def crawl_shop_all_item(self):
        agentIp = Utils.GetMyAgent()
        shop_id = self.shop_id
        shop_name = self.shop_name
        userAgent = Html_Downloader.GetUserAgent()
        header = {'ip': agentIp, 'user-agent': userAgent}
        test_detail_url = "{shop_url}shop/shop_auction_search.do?ajson=1&_tm_source=tmallsearch&spm=a320p.7692171.0.0&sort" \
                          "=d&p={page}&page_size={page_size}&from=h5".format(shop_url=self.shop_url, page_size=1,
                                                                             page=1)
        test_detail_url = test_detail_url.replace(".tmall.com", ".m.tmall.com")
        try:
            ok, response = Html_Downloader.Download_Html(test_detail_url, {}, header)
            if not ok:
                count = 0
                while (count < 4):
                    sleep(2)
                    agentip = Utils.GetMyAgent()
                    header = {'ip': agentip}
                    ok, response = Html_Downloader.Download_Html(test_detail_url, {}, header)
                    if ok:
                        break
                    count += 1
                    if count == 3:
                        header = {}
            if ok:
                jsonArray = json.loads(response.content)  # 获取解析的json
                total_page = jsonArray.get("total_page")
                total_results = jsonArray.get("total_results")
                page_size = jsonArray.get("page_size")
                logging.info(
                        "shopname:" + shop_name + " total_page:" + total_page + " total_results:" + total_results + " page_size:" + page_size)
                print "total_page:" + total_page + "total_results:" + total_results + "page_size:" + page_size
                for i in range(int(total_page)):
                    print i + 1
                    test_detail_url = "{shop_url}shop/shop_auction_search.do?ajson=1&_tm_source=tmallsearch&spm=a320p.7692171.0.0&sort=d&p={page}&page_size={page_size}&from=h5".format(
                            shop_url=self.shop_url, page_size=page_size, page=i + 1)
                    test_detail_url = test_detail_url.replace(".tmall.com", ".m.tmall.com")
                    '''
                    if int(total_page)==(i+1):
                        lastCount=int(total_results)-i*int(page_size)
                        ok, response = Html_Downloader.Download_Html(test_detail_url,{}, header)
                        if not ok:
                            count =0
                            while(count<11):
                                sleep(2)
                                agentip = Utils.GetMyAgent()
                                header = {'ip': agentip}
                                ok, response = Html_Downloader.Download_Html(test_detail_url,{},header)
                                if ok  and "price" in response.text and lastCount-response.text.count("price")<2:
                                    break
                                count+=1
                                if count==10:
                                    header={}
                        print  response.text.count('price')
                        if ok and  "price" not in response.text:
                           print "111"
                           count =0
                           while(count<11):
                                sleep(2)
                                agentip = Utils.GetMyAgent()
                                header = {'ip': agentip}
                                ok, response = Html_Downloader.Download_Html(test_detail_url,{},header)
                                if ok and "price" in response.text and lastCount-response.text.count("price")<2:
                                    break
                                count+=1
                                if count==10:
                                    header={}
                        if ok and  lastCount-response.text.count("price")>2:
                           while(count<11):
                                sleep(2)
                                agentip = Utils.GetMyAgent()
                                header = {'ip': agentip}
                                ok, response = Html_Downloader.Download_Html(test_detail_url,{},header)
                                if ok and "price" in response.text and lastCount-response.text.count("price")<2:
                                    break
                                count+=1
                                if count==10:
                                    header={}
                        if ok  and lastCount-response.text.count("price")<2:
                            logging.info("成功获取price字符串并开始解析")
                            self.parse_items(response.content,shop_id,agentIp,shop_name,userAgent)
                    else:
                        '''
                    ok, response = Html_Downloader.Download_Html(test_detail_url, {}, header)
                    if not ok:
                        count = 0
                        while (count < 11):
                            sleep(2)
                            agentip = Utils.GetMyAgent()
                            header = {'ip': agentip}
                            ok, response = Html_Downloader.Download_Html(test_detail_url, {}, header)
                            if ok:
                                break
                            count += 1
                            if count == 10:
                                header = {}
                    if ok:
                        # logging.info("成功获取price字符串并开始解析")
                        self.parse_items(response.content, shop_id, agentIp, shop_name, userAgent)
        except Exception, e:
            logging.error("抓取店铺:{shop_name}失败,店铺id:{shop_id},错误内容{m}".format(shop_name=shop_name,
                                                                                               shop_id=shop_id,
                                                                                               m=e.message,))
            crawl_content = "抓取列表页有错"
            message = e.message
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            insertLog(crawl_content, message, shop_id, agentIp, test_detail_url, start_time, shop_name)

    def crawlMonthSales(self, nid, agentip):
        try:
            month_Sales = ""
            nid_url = "https://mdskip.taobao.com/core/initItemDetail.htm?itemId={nid}"
            refer_url = "https://detail.taobao.com/item.htm?id={nid}"
            nid_Url = nid_url.format(nid=nid)
            nid_refer = refer_url.format(nid=nid)
            cookies = "x=__ll%3D-1%26_ato%3D0; l=AhERSU92PmRba9QUgSCkQMF6oRaqOoXt; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; cna=dNU/EvGIRjsCAQ4XY4PdDkHN; _m_h5_tk=7d8d6e65e5c676a6d0a69c26f7436ea1_1510363282671; _m_h5_tk_enc=e32129060738b7ce01e9114c9bec037f; sm4=440100; hng=CN%7Czh-CN%7CCNY%7C156; uc1=cookie14=UoTde95xncLyFQ%3D%3D&lng=zh_CN; uc3=sg2=Vq0THzNyGHIH22DuvMx9ZEwXL5qc2kn7REWHdois6v0%3D&nk2=&id2=&lg2=; uss=AQDPJiEXAu47o41b5k%2BKpKRT3Ckpz9nqnJX2F%2F7kZG6ttuI82ZnQa7ZL; t=1630b104e4d32df897451d6c96642469; unb=2607292494; sn=sitiselected%E6%97%97%E8%88%B0%E5%BA%97%3A%E5%A4%A7%E9%BA%A6; _tb_token_=eef7bd7b7abd6; cookie2=23bb087c638814ce8a8e329ead5332d4; isg=ApqaMZmelJirXxuDoGSRqtW160B8YxWwfLxcMqQTRi34FzpRjFtutWDlkdVw"
            # cookies="_tb_token_=f3fe5d65a6591;cookie2=171e5eb92d66332b1d52d9e2730fed33;t=bf64b0d40d912c08dd434661471b2c98;v=0"
            cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in cookies.split(';')}
            header = {'ip': agentip, 'Referer': nid_refer,
                      "cookies": cookie_dict,
                      'User-Agent': Html_Downloader.GetUserAgent()}
            ok, response = Html_Downloader.Download_Html(nid_Url, {}, header)
            if not ok:
                count = 0
                while count < 5:
                    sleep(2)
                    agentip = Utils.GetMyAgent()
                    header = {'ip': agentip, 'Referer': nid_refer,
                              'timeout': '5000',
                              "cookies": cookie_dict,
                              'User-Agent': Html_Downloader.GetUserAgent()}
                    ok, response = Html_Downloader.Download_Html(nid_Url, {}, header)
                    if ok:
                        break
                    count += 1
                    print "获取月销量第{count}试错".format(count=count)
            if ok and "sellCount\":" not in response.text:
                count = 0
                while count <10:
                    sleep(2)
                    agentip = Utils.GetMyAgent()
                    header = {'ip': agentip, 'Referer': nid_refer,
                              'timeout': '5000',
                              "cookies": cookie_dict,
                              'User-Agent': Html_Downloader.GetUserAgent()}
                    if count ==9:
                        header = {}
                    ok, response = Html_Downloader.Download_Html(nid_Url, {}, header)
                    if ok and "sellCount\":" in response.text:
                        break
                    count += 1
                    print "sellCount不在反馈中，获取月销量第{count}试错".format(count=count)
            if ok and "sellCount\":" in response.text:
                month_Sales = str(re.compile("sellCount\":(.*?)(?=\"success\")").findall(response.text)[0]).replace(",",
                                                                                                                    "").replace(
                        "，", "").strip()
                print "获得月销量为：{month_Sales}".format(month_Sales=month_Sales)
                return month_Sales
        except Exception, e:
            logging.info("月销量爬取错误{m}".format(m=e.message))

    def parse_items(self, content, shop_id, agentIp, shop_name, userAgent):
        try:
            # start_time2=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            jsonArray = json.loads(content)
            jsonResult = jsonArray.get("items")
            shop_items = []
            header = {'ip': agentIp, 'user-agent': userAgent}
            print "开始解析列表json数据"
            for item in jsonResult:
                shop_item = {}
                shop_item['shop_id'] = str(shop_id)
                shop_item['shop_name'] = shop_name
                item_id = str(item.get("item_id")).strip()
                shop_item['item_id'] = item_id
                shop_item['title'] = item.get('title').encode('utf-8')
                shop_item['picUrl'] = "https:" + item.get('img')
                # print  item.get('price')
                # 现在的销售价
                # shop_item['salePrice'] = item.get('price')
                shop_item['totalSoldQuantity'] = str(item.get('totalSoldQuantity'))
                crawl_url = "https:" + item.get('url')
                shop_item['crawl_url'] = crawl_url.replace(".m.tmall.com", ".tmall.com")
                shop_item['crawl_time'] = long(time.time())
                # 获取quantity接口url
                # 获取Items接口url
                category_id = ""
                category_id_Url = "http://d.da-mai.com/index.php?r=itemApi/getItemInfoByItemId&item_id=" + item_id
                ok, response = Html_Downloader.Download_Html(category_id_Url, {}, header)
                if not ok:
                    count = 0
                    while count < 4:
                        sleep(1)
                        agentip = Utils.GetMyAgent()
                        header = {'ip': agentip}
                        if count == 3:
                            header = {}
                        ok, response = Html_Downloader.Download_Html(category_id_Url, {}, header)
                        if ok:
                            break
                        count += 1

                if ok:
                    jsonItems = json.loads(response.content)
                    category_id = jsonItems['data']['data']['cid']
                total_quantity = 0
                quantity_Url = "http://yj.da-mai.com/index.php?r=itemskus/getSkus&fields=*&num_iids={item_id}".format(
                        item_id=item_id)
                ok, response = Html_Downloader.Download_Html(quantity_Url, {}, header)
                if not ok:
                    count = 0
                    while (count < 4):
                        sleep(2)
                        agentip = Utils.GetMyAgent()
                        header = {'ip': agentip}
                        ok, response = Html_Downloader.Download_Html(quantity_Url, {}, header)
                        if ok and "quantity" in response.text:
                            break
                        count += 1
                        if count == 3:
                            header = {}
                if ok and "quantity" not in response.text:
                    count = 0
                    while (count < 4):
                        sleep(2)
                        agentip = Utils.GetMyAgent()
                        header = {'ip': agentip}
                        ok, response = Html_Downloader.Download_Html(quantity_Url, {}, header)
                        if ok and "quantity" in response.text:
                            break
                        count += 1
                        if count == 3:
                            header = {}
                if ok and "quantity" in response.text:
                    print "成功获取sku的json字符串并开始解析"
                    jsonItems = json.loads(response.content)  # 获取解析的json
                    total_data = jsonItems.get("data")
                    for date in total_data:
                        quantity = date.get("quantity")
                        total_quantity = total_quantity + quantity
                shop_item['category_id'] = str(category_id)
                shop_item['quantity'] = str(total_quantity)
                agentip = Utils.GetMyAgent()
                shop_item['month_Sales'] = self.crawlMonthSales(item_id, agentip)
                shop_items.append(shop_item)
            post_data = {'data': json.dumps(shop_items)}
            if not self.process_request(SAVE__INSERT_API, post_data):
                sleep(3)
                self.process_request(SAVE__INSERT_API, post_data)
            # if not self.process_request(SAVE__INSERT_API_ZS, post_data):
            #     sleep(3)
            #     self.process_request(SAVE__INSERT_API_ZS, post_data)
        except Exception, e:
            logging.info("抓取店铺:{shop_name}失败,抓取店铺链接:{shop_url},店铺id:{shop_id},错误内容{m}".format(shop_name=shop_name,
                                                                                              shop_id=shop_id,
                                                                                              m=e.message))
            crawl_content = "解析接口数据有误"
            message = e.message
            end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            insertLog(crawl_content, message, shop_id, agentIp, "", start_time, shop_name)

    def process_request(self, url, data):
        result_ok = False
        ok, result = Html_Downloader.Download_Html(url, data, {'timeout': 60}, post=True)
        if ok:
            result_json = json.loads(result.content)
            result_ok = bool(result_json['flag'])
            print result_ok
        return result_ok


def insertLog(crawl_content, message, shop_id, agentIp, shop_url, start_time, shop_name):
    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    getData = "&shop_id=" + shop_id + "&ip_addr=" + agentIp + "&shop_name=" + shop_name + "&crawl_url=" + shop_url + "&start_time=" + start_time + "&end_time=" + end_time + "&crawl_content=" + crawl_content + "&error_info=" + message
    log = "http://192.168.10.198:8080/pdd/CrawlerLogController/SaveCrawlerLog?"
    # logZS = "http://syjcapi.da-mai.com/CrawlerLogController/SaveCrawlerLog?"
    logUU = log + getData
    # logUUZS = logZS + getData
    ok, result = Html_Downloader.Download_Html(logUU, {}, {})
    if ok:
        result_json = json.loads(result.content)
        result_ok = bool(result_json['status'])
    #ok, result = Html_Downloader.Download_Html(logUUZS, {}, {})
    #if ok:
    #    result_json = json.loads(result.content)
    #    result_ok = bool(result_json['status'])

# 继承线程并重写
class MyThread(threading.Thread):
    def __init__(self, func):
        super(MyThread, self).__init__()
        self.func = func

    def run(self):
        self.func()


def go_thread():
    global SHARE_Q
    threads = []
    # 通过接口获取竞店列表
    shop_means = [
        # {'shop_name': '都市丽人官方旗舰店', 'shop_url': 'https://dushiliren.tmall.com/', 'shop_id': '106448998'},
        # {'shop_name': '杰西伍旗舰店', 'shop_url': 'https://jeccifive.tmall.com/', 'shop_id': '60358260'},
        # {'shop_name': 'bobdog巴布豆童鞋旗舰店', 'shop_url': 'https://bobdogtx.tmall.com/', 'shop_id': '508371060'},
        {'shop_name': 'vans童鞋旗舰店', 'shop_url': 'https://vanskids.tmall.com/', 'shop_id': '108221379'},
        # {'shop_name': 'newbalance童鞋旗舰店', 'shop_url': 'https://newbalancekids.tmall.com/', 'shop_id': '101815493'},
        # {'shop_name': 'abckids旗舰店', 'shop_url': 'https://abckids.tmall.com/', 'shop_id': '70010831'},
        # {'shop_name': '尚古主义旗舰店', 'shop_url': 'https://drinitioisn.tmall.com/', 'shop_id': '69223965'},
        # {'shop_name': '阿吉多旗舰店', 'shop_url': 'https://ajiduo.tmall.com/', 'shop_id': '105615102'},
        # {'shop_name': 'duoyi朵以旗舰店', 'shop_url': 'https://duoyi.tmall.com/', 'shop_id': '64323785'},
        # {'shop_name': '鹿歌旗舰店', 'shop_url': 'https://lugefs.tmall.com/', 'shop_id': '116775932'},
        # {'shop_name': '秀黛内衣旗舰店', 'shop_url': 'https://xiudainy.tmall.com/', 'shop_id': '66814102'},
        # {'shop_name': '俏薇妮旗舰店', 'shop_url': 'https://qiaoweini.tmall.com/', 'shop_id': '108500397'},
        # {'shop_name': '黛安芬官方旗舰店', 'shop_url': 'https://triumph.tmall.com/', 'shop_id': '72881048'},
        # {'shop_name': 'feizing旗舰店', 'shop_url': 'https://feizing.tmall.com/', 'shop_id': '65141332'},
        # {'shop_name': '拉墨客旗舰店', 'shop_url': 'https://lamosky.tmall.com/', 'shop_id': '103210511'},
        # {'shop_name': 'iumi旗舰店', 'shop_url': 'https://iumi.tmall.com/', 'shop_id': '73151152'},
        # {'shop_name': '歌莉娅官方旗舰店', 'shop_url': 'https://goelia.tmall.com/', 'shop_id': '57301326'},
        # {'shop_name': 'isabufei衣纱布菲旗舰店', 'shop_url': 'https://isabufeifs.tmall.com/', 'shop_id': '102579676'},
        # {'shop_name': '索蒂尔旗舰店', 'shop_url': 'https://sottile.tmall.com/', 'shop_id': '70937507'},
        # {'shop_name': 'dsign旗舰店', 'shop_url': 'https://dsign.tmall.com/', 'shop_id': '481523720'},
        # {'shop_name': 'sitiselected旗舰店', 'shop_url': 'https://sitiselected.tmall.com/', 'shop_id': '62486683'},
        # {'shop_name': '意冉旗舰店', 'shop_url': 'https://y-ran.tmall.com/', 'shop_id': '108059568'},
        # {'shop_name': '悦蔻内衣旗舰店', 'shop_url': 'https://yuekouny.tmall.com/', 'shop_id': '107278923'},
        # {'shop_name': '荷韵阁旗舰店', 'shop_url': 'https://heyunge.tmall.com/', 'shop_id': '67755163'},
        # {'shop_name': '珀依兰内衣旗舰店', 'shop_url': 'https://paerlan.tmall.com/', 'shop_id': '70745452'},
    ]
    get_shop_url = "http://syjcapi.da-mai.com/CrawlerLogController/getAllCnick"
    # shop_items = requests.get(get_shop_url, verify=False).json()['data']
    for shop in shop_means:
        SHARE_Q.put(shop)
    for i in xrange(_WORKER_THREAD_NUM):
        thread = MyThread(startItemCrawl)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def startItemCrawl():
    global SHARE_Q
    while not SHARE_Q.empty():
        shop = SHARE_Q.get()
        shop_url = shop.get('shop_url')
        shop_id = shop.get('shop_id')
        shop_name = shop.get('shop_name')
        crawl = CrawlShopItemDetails(shop_url, shop_id, shop_name)
        starttime2 = datetime.now()
        logging.info("开始爬取店铺：{shopname}".format(shopname=shop_name))
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        crawl.crawl_shop_all_item()
        endtime2 = datetime.now()
        # end_time2=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        runningTime2 = (endtime2 - starttime2).seconds
        logging.info("爬取店铺{shopname}结束，耗时：{runningTime}".format(shopname=shop_name, runningTime=runningTime2))


if __name__ == "__main__":
    starttime = datetime.now()
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    '''
          for i in range(len(shop_means)):
              shop_url = shop_means[i].get('shop_url')
              shop_id = shop_means[i].get('shop_id')
              shop_name = shop_means[i].get('shop_name')
              print  shop_name
              try:
                  startItemCrawl(shop_url,shop_id,shop_name)
              except Exception, e:
                  logging.error("抓取店铺:{shop_name}失败,抓取店铺链接:{shop_url},店铺id:{shop_id},错误内容{m}".format(shop_name=shop_name,shop_url=shop_url,shop_id=shop_id,m=e.message))
                  logging.info("开始重新爬取店铺{shopname}".format(shopname=shop_name))
                  startItemCrawl(shop_url,shop_id,shop_name)
    '''
    go_thread()
    endtime = datetime.now()
    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    runningTime = (endtime - starttime).seconds
    logging.info("共计爬取时间：{runtime}".format(runtime=runningTime))
