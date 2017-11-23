# -*- coding: utf-8 -*-
import logging
from selenium import webdriver
import requests
from datetime import datetime
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='getCookieBySelenium.log',
                filemode='a')

class useSelenium(object):

    def __init__(self):
        self.ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/40.0 Mobile/12F69 Safari/600.1.4"
        self.url = "https://sitiselected.tmall.com"
        #按照销量显示列表的url
        self.url2 = "https://sitiselected.m.tmall.com/shop/shop_auction_search.htm?ajson=1&_tm_source=tmallsearch&spm=a320p.7692171.0.0&suid=479206460&sort=d"
        #获取店铺宝贝json数据的url
        #self.url4 = "https://sitiselected.m.tmall.com/shop/shop_auction_search.do?ajson=1&_tm_source=tmallsearch&spm=a320p.7692171.0.0&suid=479206460&sort=d&p=1&page_size=12&from=h5&shop_id=62486683&callback=jsonp_20617737 HTTP/1.1"
        self.url4 = "https://tassimo.m.tmall.com/shop/shop_auction_search.do?ajson=1&_tm_source=tmallsearch&spm=a320p.7692171.0.0&sort=d&p=1&page_size=12&from=h5"
        #self.url2 = "https://sitiselected.tmall.com/search.htm?spm=a1z10.3-b-s.w4011-14859494149.69.46f16db0KkefJ9&search=y&orderType=hotsell_desc&tsearch=y"
        #默认进入列表页的url
        self.url3 = "https://sitiselected.m.tmall.com/shop/shop_auction_search.htm?spm=a320p.7692171.0.0&suid=479206460&sort=default"
        self.headers = {
            'User-Agent':"Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/40.0 Mobile/12F69 Safari/600.1.4",
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.8'
        }
    #登陆列表页的url，可以获得一个cookie集合，解析cookie集合生成新cookie，用新cookie去请求json数据

    def use_Selenium_getCookie(self):
        options = webdriver.ChromeOptions()
        options.add_argument(
            'user-agent={ua}'.format(ua=self.ua)
        )
        brower = webdriver.Chrome(chrome_options=options)
        wait = WebDriverWait(brower,30)
        brower.get(self.url2)
        cookies = brower.get_cookies()
        time.sleep(3)
        new_cookie = {}
        new_cookie["t"] = cookies[2]["value"]
        new_cookie["_tb_token_"] = cookies[1]["value"]
        new_cookie["cookie2"] = cookies[4]["value"]
        new_cookie["isg"] = cookies[5]["value"]
        new_cookie["l"] = cookies[0]["value"]
        return new_cookie




    #通过新cookie获得json
    def getjson(self,newcookie):
        #cookies = useSelenium.makeNewCookie()
        proxy = {"https":"221.203.1.3:20343"}
        jsonResult = requests.get(self.url4,headers=self.headers,cookies = newcookie,verify=False).json()
        #开始解析json数据获得所需信息并以字典形式保存
        jsonArray = jsonResult.get("items")
        for item in jsonArray:
            shop_item = {}
            shop_item['item_id'] = str(item.get("item_id")).strip("L")
            shop_item['title'] = item.get('title').encode('utf-8')
            shop_item['picUrl'] = "http:"+item.get('img')
            #现在的销售价
            shop_item['salePrice'] = item.get('price')
            shop_item['totalSoldQuantity'] = item.get('totalSoldQuantity')
            shop_item['crawl_url'] = "http:"+item.get('url')
            shop_item['crawl_time'] = long(time.time())
            response = requests.get(shop_item['crawl_url'],headers = self.headers,cookies = newcookie,verify=False).text
            html = etree.HTML(response)
            #写到这里，要解析详情页获得其他数据
            re.compile('{"priceMoney":129900,"priceText":"1299"},"quantity":()}')
        print shop_item




if __name__ == '__main__':
    logging.info("开始登陆页面获取cookie")
    startTime = datetime.now()
    useselenium = useSelenium()
    #获得cookie
    cookie = useselenium.use_Selenium_getCookie()
    #将cookie放入解析获得新cookie
    res = useselenium.getjson(cookie)
    endtime = datetime.now()
    runningTime = (endtime-startTime).seconds

