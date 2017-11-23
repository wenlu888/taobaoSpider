# -*- coding: utf-8 -*-
from config import PROJECT_PATH, SEPARATOR
import PyV8
from lxml import etree
from utils.utils import Utils
from utils.JsDriver import PhantomDriver
import time
from datetime import datetime
from requests import Session
from  crawl.crawl_item import CrawlItem
import multiprocessing
from utils.html_downloader import Html_Downloader
import utils.utils
import multiprocessing
# from pyvirtualdisplay import Display
from time import sleep
from db.DataStore1 import ShopAllItemDb1
import random
import demjson  # 解析js特有的不带引号的json
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import sys
import logging
import multiprocessing
from config import SAVE__INSERT_API
#from config import SAVE__INSERT_API_ZS
#from config import GET_ALLNick
default_encoding = 'utf-8'
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
def startItemCrawl(shop_url,shop_id,shop_name,json_url):
    crawl = CrawlShopItemDetails(shop_url,shop_id,shop_name)
    result_code = crawl.crawl_shop_all_item(json_url)
    while result_code == -1:
        result_code = crawl.crawl_shop_all_item()
class CrawlShopItemDetails(object):
    def __init__(self, shop_url,shop_id,shop_name):
        self.shop_url = shop_url
        self.shop_id = shop_id
        self.shop_name = shop_name
    def crawl_shop_all_item(self):
        agentIp = Utils.GetMyAgent()
        shop_id =self.shop_id
        shop_name=self.shop_name
    def process_request(self, url, data):
        result_ok = False
        ok, result = Html_Downloader.Download_Html(url, data, {'timeout':60}, post=True)
        if ok:
            result_json = json.loads(result.content)
            result_ok = bool(result_json['flag'])
        return result_ok
    def crawl_shop_all_item(self,url):
        agentIp = Utils.GetMyAgent()
        shop_id =self.shop_id
        shop_name=self.shop_name
        userAgent=Html_Downloader.GetUserAgent()
        header = {'ip': agentIp,'user-agent':userAgent}
        text_detail_url=url
        ok, response = Html_Downloader.Download_Html(text_detail_url,{}, header)
        if ok:
            jsonArray=json.loads(response.content)  # 获取解析的json
            total_page=jsonArray.get("total_page")
            total_results=jsonArray.get("total_results")
            page_size=jsonArray.get("page_size")
            jsonResult= jsonArray.get("items")
            for item in jsonResult:
                shop_item = {}
                item_id= str(item.get("item_id")).strip()
                shop_item['item_id']=item_id
                shop_item['title'] = item.get('title').encode('utf-8')
                shop_item['picUrl'] = "http:"+item.get('img')
                #现在的销售价
                shop_item['salePrice'] = item.get('price')
                shop_item['totalSoldQuantity'] = item.get('totalSoldQuantity')
                shop_item['crawl_url'] =item.get('url')
                shop_item['crawl_time'] = long(time.time())
                #接口url 获取宝贝种类（颜色分类）不需要这个接口了，下面那个接口就可以得到颜色分类等信息
                '''
                test_Url="http://d.da-mai.com/index.php?r=itemApi/getItemInfoByItemId&item_id="+item_id
                ok, response = Html_Downloader.Download_Html(test_Url,{}, header)
                if ok:
                   jsonItems=json.loads(response.content)  # 获取解析的json
                '''
                #接口url 获取SKU详细信息（）
                shop_item['quantity'] =0
                getSKU_Url = "http://yj.da-mai.com/index.php?r=itemskus/getSkus&fields=*&num_iids={item_id}".format(item_id=item_id)
                ok, response = Html_Downloader.Download_Html(getSKU_Url,{}, header)
                if ok:
                    jsonItems=json.loads(response.content)
                    total_data = jsonItems.get("data")
                    for date in total_data:
                        quantity = date.get("quantity")
                        shop_item['quantity'] = shop_item['quantity']+quantity
                #获取宝贝详情页信息 （第二屏信息）
                getDetail_Url = "http://d.da-mai.com/index.php?r=itemApi/getItemInfoByItemId&item_id={item_id}".format(item_id=item_id)
                ok, response_detail = Html_Downloader.Download_Html(getDetail_Url,{}, header)
                if ok:
                    shop_item['attribute'] = []
                    #jsonDetails = response_detail['data']['data']
                    jsonDetails = json.loads(response_detail.content)
                    properties = jsonDetails['data']['data']['properties']
                    stringName=""
                    for attri in properties:
                        #string = "{name}:{value}&&||".format(name=attri.get('name'),value=attri.get('value'))
                        name = attri.get('name')
                        value = attri.get('value')
                        if name in stringName:
                            #shop_item['attribute'].append(name)
                            string = "{value} ".format(value=value)
                            shop_item['attribute'].append(string)
                        if name not in stringName:
                            string = "{name}:{value}&&||".format(name=name,value=value)
                            shop_item['attribute'].append(string)
                            stringName=name+stringName

        for page in total_page:
            #重写json的URL并完成回调函数
            ###！！！！！注意这里店铺的url写死了，应该传参进来！！！！
            getlist_url="https://yiqianny.m.tmall.com/shop/shop_auction_search.do?ajson=1&_tm_source=tmallsearch&" \
                    "spm=a320p.7692171.0.0&sort=d&p={page}&page_size=24&from=h5".format(page=page)
            p = multiprocessing.Process(target=self.crawl_shop_all_item(getlist_url),args=(page,))
            p.start()
            logging.info("开始多进程爬虫，爬取的json列表为：{url}".format(url=getlist_url))
            self.crawl_shop_all_item(getlist_url)

def insertLog(crawl_content,message,shop_id,agentIp,shop_url,start_time,shop_name):
    end_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    getData="&shop_id="+shop_id+"&ip_addr="+agentIp+"&shop_name="+shop_name+"&crawl_url="+shop_url+"&start_time="+start_time+"&end_time="+end_time+"&crawl_content="+crawl_content+"&error_info="+message
    log="http://192.168.10.198:8080/pdd/CrawlerLogController/SaveCrawlerLog?"
    logZS="http://syjcapi.da-mai.com/CrawlerLogController/SaveCrawlerLog?"
    logUU=log+getData
    logUUZS=logZS+getData
    ok, result = Html_Downloader.Download_Html(logUU,{},{})
    if ok:
        result_json = json.loads(result.content)
        #result_ok = bool(result_json['status'])
    ok, result = Html_Downloader.Download_Html(logUUZS,{},{})
    if ok:
        result_json = json.loads(result.content)
        #result_ok = bool(result_json['status'])

if __name__ == "__main__":
          starttime=datetime.now()
          start_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
          agentIp=Utils.GetMyAgent()
          '''
         urlLog="http://192.168.10.198:8080/pdd/CrawlerLogController/getAllNick"
         log="http://192.168.10.198:8080/pdd/CrawlerLogController/SaveCrawlerLog?"
         ok, result = Html_Downloader.Download_Html(urlLog,{},{})
         if ok:
             result_json1 = json.loads(result.content)
             sonArrayShop=result_json1['data']
             for itemShop in jsonArrayShop:
                shop_url=itemShop.get('shop_url')
                shop_id=itemShop.get('shop_id')
                shop_name=itemShop.get('shop_name')
         '''
          shop_url="https://newbalancekids.tmall.com/"
          shop_id="101815493"
          shop_name="newbalance童鞋旗舰店"
          json_url = "https://yiqianny.m.tmall.com/shop/shop_auction_search.do?ajson=1&_tm_source=tmallsearch&" \
                            "spm=a320p.7692171.0.0&sort=d&p=1&page_size=24&from=h5"
          try:
              startItemCrawl(shop_url,shop_id,shop_name,json_url)
              endtime =datetime.now()
              end_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
              runningTime=(endtime - starttime).seconds
              print("抓取消耗Time: %s" %runningTime)
          except Exception, e:
              # logging.error("抓取店铺:{shop_name}失败,抓取店铺链接:{shop_url},店铺id:{shop_id},开始时间{start_time},结束时"
              #              "间{end_time},错误内容{m}".format(shop_name=shop_name,shop_url=shop_url,shop_id=shop_id,
              #                                          start_time=starttime,m=e.message))
              content="抓取店铺:{shop_name}失败".format(shop_name=shop_name)





