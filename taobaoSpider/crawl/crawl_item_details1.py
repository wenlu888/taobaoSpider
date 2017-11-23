# -*- coding: utf-8 -*-
# 用于抓取指定店铺所有宝贝及宝贝规格属性
from lxml import etree
from utils.utils import Utils
from utils.JsDriver import PhantomDriver
import time
from  crawl.crawl_item import CrawlItem
import multiprocessing
from utils.html_downloader import Html_Downloader
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
    result_code = crawl.crawl_shop_all_item()
    while result_code == -1:
        result_code = crawl.crawl_shop_all_item()
class CrawlShopItemDetails(object):
    def __init__(self, shop_url):
        self.shop_url = shop_url
        self.shopall = ShopAllItemDb1()
    def parse_items(self, html, shop_id,agentIp):
        shop_items = []
        if html.xpath("//div[contains(@class,'shop-hesper-bd')]"):
            for item in html.xpath("//div[contains(@class,'shop-hesper-bd')]")[0].xpath(".//dl"):
                shop_item = {}
                shop_item['shop_id'] = shop_id
                item_id= item.get('data-id').replace("\"", "").replace("\\", "")
                shop_item['item_id']=item_id
                shop_item['item_title'] = item.xpath('./dd[1]/a/text()')[0].encode('utf-8').strip()
                shop_item['item_pic'] = item.xpath('./dt/a/img/@src')[0].strip().replace("\\", "").replace("//",'https://')
                shop_item['item_sales'] = int(item.xpath(".//*[contains(@class,'sale-num')]/text()")[0].encode('utf-8'))
                shop_item['item_old_price'] = float(item.xpath(".//*[contains(@class,'s-price')]/text()")[0].encode(
                        'utf-8')) if item.xpath(".//*[contains(@class,'s-price')]/text()") else None
                shop_item['item_new_price'] = float(
                        item.xpath(".//*[contains(@class,'c-price')]/text()")[0].encode('utf-8'))
                shop_item['item_comment'] = int(item.xpath(".//*[contains(@class,'rates')]")[0].xpath(".//span/text()")[
                                                    0].encode('utf-8')) if item.xpath(".//*[contains(@class,'rates')]") else None
                shop_item['crawl_time'] = long(time.time())
                #获取链接里面的详情
                detail_url="https://item.taobao.com/item.htm?spm=a1z10.3-c-s.w4002-14766145001.18.6584ae82X93XhC&id={item_id}"
                t_detail_url=detail_url.format(item_id=item_id)
                shop_item['crawl_url']=t_detail_url
                header = {'ip': agentIp}
                try:
                   ok, response = Html_Downloader.Download_Html(t_detail_url,{}, header)
                   print(ok)
                   if not ok:
                      ok, response = Html_Downloader.Download_Html(t_detail_url,{}, {})
                   print(t_detail_url)
                   if ok:
                      html = etree.HTML(response.text)
                      # shop_id = ""
                      category_id= re.compile("item%5f(.*?)(?=&)").findall(response.text)[0]
                      shop_item['category_id']=category_id
                      # if html.xpath("//meta[@name='microscope-data']"):
                       # for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                         # if 'shopid' in meta.lower():
                              # shop_id = meta.split("=")[1]
                      if html.xpath("//dl[contains(@class,'tb-prop')]"):
                          for prop in html.xpath("//dl[contains(@class,'tb-prop')]"):
                                if not prop in html.xpath("//dl[contains(@class,'tb-hidden')]"):
                                    prop_value_id=[]
                                    prop_name = prop.xpath(".//dt/text()")[0].encode('utf-8')
                                    for value in prop.xpath(".//dd/ul/li"):
                                           sub_value_id= []
                                           sku_id = value.get('data-value')
                                           sub_value_id.append(sku_id)
                                           if value.xpath('./a/span/text()'):
                                               sku_name = value.xpath('./a/span/text()')[0].encode('utf-8')
                                               sub_value_id.append(sku_name)
                                           prop_value_id.append(";".join(sub_value_id))
                                shop_item[prop_name] ="&&||".join(prop_value_id)
                      if html.xpath("//ul[@id='J_UlThumb']"):
                            stype_img_id=[]
                            if html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li/div"):
                                for value1 in html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li/div"):
                                         if value1.xpath('./a')[0].xpath('./img')[0].get('data-src') and re.compile("/([^/]*)(?=!!)").findall(
                                                value1.xpath('./a')[0].xpath('./img')[0].get('data-src')):
                                               sku_img_id = re.compile("/([^/]*)(?=!!)").findall(value1.xpath('./a')[0].xpath('./img')[0].get('data-src'))[0]
                                               stype_img_id.append(sku_img_id)
                            elif html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li"):
                                for value1 in html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li"):
                                         if value1.xpath('./a')[0].xpath('./img')[0].get('src') and re.compile("/([^/]*)(?=!!)").findall(
                                                value1.xpath('./a')[0].xpath('./img')[0].get('src')):
                                               sku_img_id = re.compile("/([^/]*)(?=!!)").findall(value1.xpath('./a')[0].xpath('./img')[0].get('src'))[0]
                                               stype_img_id.append(sku_img_id)
                            shop_item["图片属性"]="&&||".join(stype_img_id)
                      if html.xpath("//ul[@id='J_AttrUL']"):
                          styleliList=[]
                          for styleli in html.xpath("//ul[@id='J_AttrUL']")[0].xpath(".//li"):
                               if styleli.xpath('./text()'):
                                    styleliText= styleli.xpath('./text()')[0].encode('utf-8').strip()
                                    styleliList.append(styleliText)
                      elif html.xpath("//div[@id='attributes']"):
                          styleliList=[]
                          for styleli in html.xpath("//div[@id='attributes']")[0].xpath(".//ul/li"):
                               if styleli.xpath('./text()'):
                                    styleliText= styleli.xpath('./text()')[0].encode('utf-8').strip()
                                    styleliList.append(styleliText)
                      shop_item["属性"]="&&||".join(styleliList)
                except Exception, e:
                    print("----抓取错误----")
                shop_items.append(shop_item)
                self.shopall.insert_or_update(shop_items)
        # return shop_items
    def parse_items1(self, html, shop_id,agentIp):
        shop_items = []
        if html.xpath("//div[contains(@class,'J_TItems')]"):
            for item in html.xpath("//div[contains(@class,'J_TItems')]")[0].xpath(".//dl"):
                shop_item = {}
                shop_item['shop_id'] = shop_id
                item_id= item.get('data-id').replace("\"", "").replace("\\", "")
                shop_item['item_id']=item_id
                shop_item['item_title'] = item.xpath('./dd[2]/a/text()')[0].encode('utf-8').strip()
                shop_item['item_pic'] =item.xpath('./dt/a/@href')[0].strip().replace("\\", "").replace("//",'https://')
                shop_item['item_sales'] = int(item.xpath(".//*[contains(@class,'sale-num')]/text()")[0].encode('utf-8'))
                # shop_item['item_old_price'] = float(item.xpath(".//*[contains(@class,'s-price')]/text()")[0].encode(
                #         'utf-8')) if item.xpath(".//*[contains(@class,'s-price')]/text()") else None
                shop_item['item_new_price'] = float(
                        item.xpath(".//*[contains(@class,'c-price')]/text()")[0].encode('utf-8'))
                item_comment=(item.xpath(".//*[contains(@class,'rates')]")[0].xpath(".//span/text()")[0].encode('utf-8')) if item.xpath(".//*[contains(@class,'rates')]") else None
                item_comment=item_comment.strip().replace("评价","").replace(":","")
                shop_item['item_comment'] =int(item_comment)
                shop_item['crawl_time'] = long(time.time())
                #获取链接里面的详情
                detail_url="https://item.taobao.com/item.htm?spm=a1z10.3-c-s.w4002-14766145001.18.6584ae82X93XhC&id={item_id}"
                t_detail_url=detail_url.format(item_id=item_id)
                shop_item['crawl_url']=t_detail_url
                header = {'ip': agentIp}
                try:
                   ok, response = Html_Downloader.Download_Html(t_detail_url,{}, header)
                   print(ok)
                   if not ok:
                      ok, response = Html_Downloader.Download_Html(t_detail_url,{}, {})
                   print(t_detail_url)
                   if ok:
                      html = etree.HTML(response.text)
                      # shop_id = ""
                      category_id= re.compile("item%5f(.*?)(?=&)").findall(response.text)[0]
                      shop_item['category_id']=category_id
                      # if html.xpath("//meta[@name='microscope-data']"):
                       # for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                         # if 'shopid' in meta.lower():
                              # shop_id = meta.split("=")[1]
                      if html.xpath("//dl[contains(@class,'tb-prop')]"):
                          for prop in html.xpath("//dl[contains(@class,'tb-prop')]"):
                                if not prop in html.xpath("//dl[contains(@class,'tb-hidden')]"):
                                    prop_value_id=[]
                                    prop_name = prop.xpath(".//dt/text()")[0].encode('utf-8')
                                    for value in prop.xpath(".//dd/ul/li"):
                                           sub_value_id= []
                                           sku_id = value.get('data-value')
                                           sub_value_id.append(sku_id)
                                           if value.xpath('./a/span/text()'):
                                               sku_name = value.xpath('./a/span/text()')[0].encode('utf-8')
                                               sub_value_id.append(sku_name)
                                           prop_value_id.append(";".join(sub_value_id))
                                shop_item[prop_name] ="&&||".join(prop_value_id)
                      if html.xpath("//ul[@id='J_UlThumb']"):
                            stype_img_id=[]
                            if html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li/div"):
                                for value1 in html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li/div"):
                                         if value1.xpath('./a')[0].xpath('./img')[0].get('data-src') and re.compile("/([^/]*)(?=!!)").findall(
                                                value1.xpath('./a')[0].xpath('./img')[0].get('data-src')):
                                               sku_img_id = re.compile("/([^/]*)(?=!!)").findall(value1.xpath('./a')[0].xpath('./img')[0].get('data-src'))[0]
                                               stype_img_id.append(sku_img_id)
                            elif html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li"):
                                for value1 in html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li"):
                                         if value1.xpath('./a')[0].xpath('./img')[0].get('src') and re.compile("/([^/]*)(?=!!)").findall(
                                                value1.xpath('./a')[0].xpath('./img')[0].get('src')):
                                               sku_img_id = re.compile("/([^/]*)(?=!!)").findall(value1.xpath('./a')[0].xpath('./img')[0].get('src'))[0]
                                               stype_img_id.append(sku_img_id)
                            shop_item["图片属性"]="&&||".join(stype_img_id)
                      if html.xpath("//ul[@id='J_AttrUL']"):
                          styleliList=[]
                          for styleli in html.xpath("//ul[@id='J_AttrUL']")[0].xpath(".//li"):
                               if styleli.xpath('./text()'):
                                    styleliText= styleli.xpath('./text()')[0].encode('utf-8').strip()
                                    styleliList.append(styleliText)
                      elif html.xpath("//div[@id='attributes']"):
                          styleliList=[]
                          for styleli in html.xpath("//div[@id='attributes']")[0].xpath(".//ul/li"):
                               if styleli.xpath('./text()'):
                                    styleliText= styleli.xpath('./text()')[0].encode('utf-8').strip()
                                    styleliList.append(styleliText)
                      shop_item["属性"]="&&||".join(styleliList)
                except Exception, e:
                    print("----抓取错误----")
                shop_items.append(shop_item)
                self.shopall.insert_or_update(shop_items)
        # return shop_items
    def crawl_shop_all_item(self):
        agentIp = Utils.GetAgentIp()
        shop_id = -1
        # agentIp=None
        # agentIp = '120.24.171.107:16816'
        driver = PhantomDriver(2, agentIp, 60)
        parms_url = "{shop_url}/i/asynSearch.htm?_ksTS={now}569_240&callback=jsonp241&mid=w-14766145001-0&wid=14766145001&path=/search.htm&search=y&orderType=hotsell_desc&scene=taobao_shop&pageNo={page_num}"
        url = "{shop_url}/search.htm?&search=y&orderType=hotsell_desc&scene=taobao_shop".format(shop_url=self.shop_url)
        # url="https://nanshanweng.m.tmall.com/shop/shop_auction_search.do?sort=d&p=1&page_size=12&from=h5&shop_id=247506881&ajson=1&_tm_source=tmallsearch"
        # self.testurl(url,agentIp)
        print(url)
        result = driver.download_no_quit(url)
        source = result['page_source']
        driver.return_driver().quit()
        if result['ok']:
            html = etree.HTML(source)
        shop_items = []
        if html is not None and 'page-info' in source and html.xpath("//span[contains(@class,'page-info')]/text()"):
            total = int(html.xpath("//span[contains(@class,'page-info')]/text()")[0].split('/')[1])
            total=3
            if html.xpath("//meta[@name='microscope-data']"):
                for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                    if 'shopid' in meta.lower():
                        shop_id = meta.split("=")[1]
                        # self.shopall.format_data(shop_id, False)
                        shop_items.extend(self.parse_items(html, shop_id,agentIp))
            for i in range(1, total):
                page_num = i + 1
                print("page%s" % page_num)
                url = parms_url.format(shop_url=self.shop_url, now=long(time.time()), page_num=page_num)
                result = driver.download_no_quit(url)
                if result['ok']:
                    html = etree.HTML(result['page_source'])
                if result['ok'] and 'page-info' in source and html.xpath("//span[contains(@class,'page-info')]/text()"):
                    results = self.parse_items(html, shop_id,agentIp)
                    shop_items.extend(results)
                sleep(15)
            self.shopall.insert_or_update(shop_items)
        elif html is not None and 'ui-page-s-len' in source and html.xpath("//b[contains(@class,'ui-page-s-len')]/text()"):
            total = int(html.xpath("//b[contains(@class,'ui-page-s-len')]/text()")[0].split('/')[1])
            total=3
            if html.xpath("//meta[@name='microscope-data']"):
                for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                    if 'shopid' in meta.lower():
                        shop_id = meta.split("=")[1]
                        # self.shopall.format_data(shop_id, False)
                        shop_items.extend(self.parse_items1(html, shop_id,agentIp))
            for i in range(1, total):
                page_num = i + 1
                print("page%s" % page_num)
                url = parms_url.format(shop_url=self.shop_url, now=long(time.time()), page_num=page_num)
                result = driver.download_no_quit(url)
                if result['ok']:
                    html = etree.HTML(result['page_source'])
                if result['ok'] and  'ui-page-s-len' in source and html.xpath("//b[contains(@class,'ui-page-s-len')]/text()"):
                    results = self.parse_items1(html, shop_id,agentIp)
                    shop_items.extend(results)
                sleep(15)
            self.shopall.insert_or_update(shop_items)
        else:
             # 失败就退出关闭webdriver
         driver.return_driver().quit()
        print("无法获取%s" % agentIp)
        return -1
        return shop_id

    # def crawl_all_item_details(self):
    #     for shop_id in self.shopall.get_all_shop_id():
    #         self.crawl_shop_all_item_details(shop_id)

if __name__ == "__main__":
    startItemCrawl("https://playboyfs.tmall.com")
