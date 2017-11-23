# -*- coding: utf-8 -*-

# 用于抓取指定店铺所有宝贝及宝贝规格属性

from lxml import etree
from Utils.Utils import Utils
from Utils.JsDriver import PhantomDriver

import time
from  crawl.crawlItem import CrawlItem
import multiprocessing
from Utils.HtmlDownloader import Html_Downloader
import multiprocessing
# from pyvirtualdisplay import Display
from time import sleep
from db.DataStore1 import ShopAllItemDb1

import random
import demjson  # 解析js特有的不带引号的json
import re
import json

import sys
import multiprocessing

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def startItemCrawl(keyword):
    crawl = CrawlShopItemDetails(keyword)
    # crawl.crawl_shop_all_item_details("64469556")

    while crawl.crawl_shop_all_item() == -1:
        crawl.crawl_shop_all_item()


def crawl_item_details(queue, i):
    shopall = ShopAllItemDb1()
    agentIp = Utils.GetAgentIp()
    # agentIp = "127.0.0.1:8888"
    driver = PhantomDriver(1, agentIp, 60).return_driver()
    while (True):
        try:
            nid = None
            nid = queue.get(block=False)
        except:
            pass
        try:
            if nid:
                item = CrawlItem.crawl(driver, nid)
                if item:
                    shopall.insert_or_update_details(item)
                else:
                    #如果抓取失败就更换代理ip并重新放到队列中
                    agentIp = Utils.GetAgentIp()
                    try:
                        queue.put(nid, block=False)
                    except:
                        pass
                    print("进程%s抓取%s宝贝详情失败,重试 Ip:%s" % (i, nid, agentIp))
        except Exception, e:
            agentIp = Utils.GetAgentIp()
            driver.quit()
            driver = PhantomDriver(1, agentIp, 60).return_driver()
            try:
                queue.put(nid, block=False)
            except:
                pass
            print("进程%s抓取%s宝贝详情失败:%s,退出浏览器重试" % (i, nid, e.message))
            driver.quit()


class CrawlShopItemDetails(object):
    def __init__(self, shop_url):
        self.shop_url = shop_url
        self.shopall = ShopAllItemDb1()

    def parse_items(self, html, shop_id):
        shop_items = []
        print(html)
        if html.xpath("//div[contains(@class,'shop-hesper-bd')]"):
            for item in html.xpath("//div[contains(@class,'shop-hesper-bd')]")[0].xpath(".//dl"):
                shop_item = {}
                shop_item['shop_id'] = shop_id
                shop_item['item_id'] = item.get('data-id').replace("\"", "").replace("\\", "")
                shop_item['item_title'] = item.xpath('./dd[1]/a/text()')[0].encode('utf-8').strip()
                # shop_item['item_title1'] = item.xpath('.//img/@alt')[0].encode('utf-8').strip()
                shop_item['item_sales'] = item.xpath(".//*[contains(@class,'sale-num')]/text()")[0].encode('utf-8')
                shop_item['item_old_price'] = item.xpath(".//*[contains(@class,'s-price')]/text()")[0].encode(
                        'utf-8') if item.xpath(".//*[contains(@class,'s-price')]/text()") else None
                shop_item['item_new_price'] = item.xpath(".//*[contains(@class,'c-price')]/text()")[0].encode('utf-8')
                shop_item['item_comment'] = item.xpath(".//*[contains(@class,'rates')]")[0].xpath(".//span/text()")[
                    0].encode('utf-8') if item.xpath(".//*[contains(@class,'rates')]") else None
                shop_item['crawl_time'] = long(time.time())
                shop_items.append(shop_item)
        return shop_items

    def crawl_shop_all_item(self):
        agentIp = Utils.GetAgentIp()
        # agentIp="127.0.0.1:8888"
        driver = PhantomDriver(2, agentIp, 60)
        parms_url = "{shop_url}/i/asynSearch.htm?_ksTS={now}569_240&callback=jsonp241&mid=w-14766145001-0&wid=14766145001&path=/search.htm&search=y&orderType=hotsell_desc&scene=taobao_shop&pageNo={page_num}"

        url = "{shop_url}/search.htm?&search=y&orderType=hotsell_desc&scene=taobao_shop".format(shop_url=self.shop_url)
        print  (url)
        result = driver.download_no_quit(url)
        shop_id = -1
        source = result['page_source']
        if result['ok']:
            html = etree.HTML(source)
        shop_items = []
        if html is not None and 'page-info' in source and html.xpath("//span[contains(@class,'page-info')]/text()"):
            total = int(html.xpath("//span[contains(@class,'page-info')]/text()")[0].split('/')[1])
            if html.xpath("//meta[@name='microscope-data']"):
                for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                    if 'shopid' in meta.lower():
                        shop_id = meta.split("=")[1]
                        self.shopall.format_data(shop_id,False)
                        shop_items.extend(self.parse_items(html, shop_id))
            driver = PhantomDriver(1, agentIp, 60)
            for i in range(1, total):
                page_num = i + 1
                print("page%s" % page_num)
                url = parms_url.format(shop_url=self.shop_url, now=int(time.time()), page_num=page_num)
                result = driver.download_no_quit(url)
                if result['ok']:
                    html = etree.HTML(result['page_source'])
                if result['ok'] and 'page-info' in source and html.xpath("//span[contains(@class,'page-info')]/text()"):
                    results = self.parse_items(html, shop_id)
                    shop_items.extend(results)
            self.shopall.insert_or_update(shop_items)
        else:
            print("无法获取%s" % agentIp)
            return -1
        return shop_id

    def crawl_all_item_details(self):
        for shop_id in self.shopall.get_all_shop_id():
            self.crawl_shop_all_item_details(shop_id)

    def crawl_shop_all_item_details(self, shop_id):
        self.shopall.format_data(shop_id, True)

        for item in self.shopall.get_shop_item_ids(shop_id):
            if not self.shopall.exist_item(item['item_id']):
                try:
                    q.put(item['item_id'], block=False)
                except:
                    pass


if __name__ == "__main__":
    #多进程队列
    # q = multiprocessing.Queue()
    # for i in range(1):
    #     print(i)
    #     p = multiprocessing.Process(target=crawl_item_details, args=(q, i))
    #     p.start()
    startItemCrawl("https://bra360.taobao.com")
