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
import urllib
import urllib2
from bs4 import BeautifulSoup
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
                # shop_item['item_comment'] = int(item.xpath(".//*[contains(@class,'rates')]")[0].xpath(".//span/text()")[0].encode('utf-8')) if item.xpath(".//*[contains(@class,'rates')]") else None

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
    def testurl(self,url,agentIp):
        print("111")
        header = {'ip': agentIp}
        for i in range(1, 200):
            sleep(1)
            ok, response = Html_Downloader.Download_Html(url,{}, header)
            print(ok)
            if not ok:
              ok, response = Html_Downloader.Download_Html(url,{}, {})
            print(url)
            if ok:
                html = etree.HTML(response.text)
        print("1111")

    def crawl_shop_all_item(self):
        agentIp = Utils.GetAgentIp()
        header = {'ip': agentIp}
        shop_id = -1
        # agentIp=None
        # agentIp = '120.24.171.107:16816'
        url ="{shop_url}/search.htm?&search=y&orderType=hotsell_desc&scene=taobao_shop".format(shop_url=self.shop_url)
        url=self.shop_url
        print url
        # data=urllib2.urlopen(url).readlines()
        # soup=BeautifulSoup(''.join(data), fromEncoding='utf8')
        # primary_consumer = soup.find(id="bd")
        ok, response = Html_Downloader.Download_Html(url,{}, header)
        soup=BeautifulSoup(''.join(response), fromEncoding='utf8')
        header=soup.find(id="J_GlobalNav")
        div=header.text
        # print(ok)
        if ok:
            html = etree.HTML(response.text.encode('utf-8'))
            if html is not None and html.xpath("//header[@id='mp-header']"):
               if  "shopId" in html.xpath("//header[@id='mp-header']")[0].get("mdv-cfg").split(':')[0]:
                   shop_id =html.xpath("//header[@id='mp-header']")[0].get("mdv-cfg").split(':')[1]
                   shop_id=shop_id.replace("\'}", "").replace("\'", "")
        url="{shop_url}/shop/shop_auction_search.do?sort=d&p=1&page_size=90&from=h5&shop_id={shop_id}&ajson=1&_tm_source=tmallsearch&orderType=hotsell_desc".format(shop_url=self.shop_url,shop_id=shop_id)
        print (url)
        # driver = PhantomDriver(2, agentIp, 60)
        # driver.download_no_quit(self.shop_url)
        # sleep(1)
        # for i in range(20):
        #     result = driver.download_no_quit(url)
        #     sleep(3)
        # source = result['page_source']
        # driver.return_driver().quit()
        # if result['ok']:
        #     html = etree.HTML(source)
        ok, response = Html_Downloader.Download_Html(url,{}, header)
        print(ok)
        if not ok:
            ok, response = Html_Downloader.Download_Html(url,{}, {})
        print(url)
        if ok:
             html = etree.HTML(response.text)
             data = json.loads(html.group(1).encode('utf-8'))
             print


if __name__ == "__main__":
    startItemCrawl("https://playboyfs.m.tmall.com")
