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
import json
import sys
import logging
import multiprocessing
from config import SAVE__INSERT_API
from config import SAVE__INSERT_API_ZS
from config import GET_ALLNick
default_encoding = 'utf-8'
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='a')
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
def startItemCrawl(shop_url,shop_id,shop_name):
    crawl = CrawlShopItemDetails(shop_url,shop_id,shop_name)
    result_code = crawl.crawl_shop_all_item()
    while result_code == -1:
        result_code = crawl.crawl_shop_all_item()
class CrawlShopItemDetails(object):
    def __init__(self, shop_url,shop_id,shop_name):
        self.shop_url = shop_url
        self.shop_id = shop_id
        self.shop_name = shop_name
    def execute_javascript(self,txt):
        js_path = "%s%s%s" % (PROJECT_PATH, SEPARATOR, "taobao_sign_js")
        file = open(js_path, 'r')
        js = file.read()
        ctxt = PyV8.JSContext()
        ctxt.enter()
        func = ctxt.eval(js)
        result_txt = func(txt)
        return result_txt
    def get_shop_item_list(self,session, proxy_ip, page_num,shop_id,shop_name):
        try:
             count=0
             start_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
             while(count<15):
                    proxies = {"http": proxy_ip, "https": proxy_ip}
                    parms_pager = "{{\"shopId\":\"{shop_id}\",\"currentPage\":{page_num},\"pageSize\":\"30\",\"sort\":\"hotsell\",\"q\":\"\"}}"
                    parms_url = "https://unzbmix25g.api.m.taobao.com/h5/com.taobao.search.api.getshopitemlist/2.0/?appKey=12574478&t={stmp}&sign={sign}&api=com.taobao.search.api.getShopItemList&v=2.0&type=jsonp&dataType=jsonp&callback=mtopjsonp12&data={pager}"
                    params_referer = "https://shop{shop_id}.m.taobao.com/?shop_id={shop_id}&sort=d".format(shop_id=shop_id)
                    stmp = "%s739" % (long(time.time()))
                    referer = params_referer.format(shop_id=shop_id)
                    pager = parms_pager.format(shop_id=shop_id, page_num=page_num)
                    if session.cookies.get_dict('.taobao.com') and session.cookies.get_dict('.taobao.com').has_key('_m_h5_tk'):
                        h5_tk = session.cookies.get_dict('.taobao.com')['_m_h5_tk']
                        token = re.compile('(.*)(?=_)').findall(h5_tk)[0]
                        value = '%s&%s&12574478&%s' % (token, stmp, pager)
                        sign =self.execute_javascript(value)
                    else:
                        sign = "a013c868718eddb116eac3da0aa7974a"
                    url = parms_url.format(pager=pager, stmp=stmp, sign=sign)
                    requests_parms = {}
                    headers = {'Referer': referer,
                               'Host': 'api.m.taobao.com',
                               'Cache-Control': 'no-cache',
                               'Pragma': 'no-cache',
                               'timeout':'5000',
                               'User-Agent': Html_Downloader.GetUserAgent()}
                    if proxy_ip:
                        requests_parms['proxies'] = proxies
                        requests_parms['verify'] = False
                    try:
                       result = session.get(url, headers=headers, **requests_parms)
                    except Exception, e:
                       proxy_ip=Utils.GetMyAgent()
                       continue
                    count=count+1
                    if result.status_code!=200:
                        logging.info("抓取{parms_url}返回状态码:{code}".format(code=result.status_code,parms_url=parms_url))
                        crawl_content="抓取列表{URL}".format(URL=parms_url)
                        message="返回状态码:{code}".format(code=result.status_code)
                        insertLog(crawl_content,message,shop_id,proxy_ip,parms_url,start_time,shop_name)
                        proxy_ip=Utils.GetMyAgent()
                        sleep(2)
                    else:
                        print(result.status_code)
                    if result.ok:
                        sleep(2)
                        return result.content
                        break
        except Exception, e:
            logging.info("抓取totalSoldQuantity有错".format(e=e.message))
            crawl_content="抓取totalSoldQuantity有错"
            message=e.message
            insertLog(crawl_content,message,shop_id,proxy_ip,parms_url,start_time,shop_name)
            #print("抓取totalSoldQuantity有错".format(e=e.message))
    def crawl_yxl(self,auctionId,agentIp):
        yxl=-1
        count =0
        while(count<20):
            agentIp=Utils.GetMyAgent()
            userAgent=Html_Downloader.GetUserAgent()
            header = {'ip': agentIp,'user-agent':userAgent}
            text_detail_url="https://detail.m.tmall.com/item.htm?spm=a320p.7692363.0.0&id={auctionId}".format(auctionId=auctionId)
            ok, response = Html_Downloader.Download_Html(text_detail_url,{}, header)
            if ok:
                matchs=re.compile("sellCount\":(.*?)(?=showShopActivitySize)").findall(response.text)
                if len(matchs) > 0:
                 if "sellCount" in response.text:
                    yxl=re.compile("sellCount\":(.*?)(?=showShopActivitySize)").findall(response.text)[0].encode('utf-8')
                    yxl=yxl.replace(",\"","")
                    break
            sleep(3)
            count+=1
        return  yxl
    def parse_items(self,jsonArray, shop_id,agentIp):
        shop_items=[]
        # agentIp=None
        header = {'ip': agentIp}
        for item in jsonArray:
             shop_item = {}
             shop_item['shop_id']=shop_id
             auctionId=item.get('auctionId')
             shop_item['item_id']=auctionId
             shop_item['title']= item.get('title')
             shop_item['picUrl']="http:"+item.get('picUrl')
             # shop_item['picUrl']=re.compile("/([^/]*)(?=_)").findall(item.get('picUrl'))[0]
             shop_item['salePrice']= item.get('salePrice')
             shop_item['reservePrice']= item.get('reservePrice')
             shop_item['quantity']= item.get('quantity')
             shop_item['totalSoldQuantity']= item.get('totalSoldQuantity')
             #获取链接里面的详情
             t_detail_url="https://item.taobao.com/item.htm?spm=a1z10.3-c-s.w4002-14766145001.18.6584ae82X93XhC&id={auctionId}".format(auctionId=auctionId)
             shop_item['crawl_url']=t_detail_url
             print(t_detail_url)
             shop_item['crawl_time'] = long(time.time())
             sold=item.get('sold')
             if "tmall" in self.shop_url:
                 sold=""
                 sold=self.crawl_yxl(auctionId,agentIp)
             #天猫的月销量另外获取
             shop_item['sold']=sold
             try:
                   ok, response = Html_Downloader.Download_Html(t_detail_url,{}, header)
                   if not ok:
                       count =0
                       while(count<4):
                            sleep(2)
                            agentip = Utils.GetMyAgent()
                            header = {'ip': agentip}
                            ok, response = Html_Downloader.Download_Html(t_detail_url,{},header)
                            if ok and "category=item" in response.text:
                                break
                            count+=1
                            if count==3:
                                header={}
                   if ok and  "category=item" not in response.text:
                       count =0
                       while(count<4):
                            sleep(2)
                            agentip = Utils.GetMyAgent()
                            header = {'ip': agentip}
                            ok, response = Html_Downloader.Download_Html(t_detail_url,{},header)
                            if ok and "category=item" in response.text:
                                break
                            count+=1
                            if count==3:
                                header={}
                   if ok and "category=item" in response.text:
                      html = etree.HTML(response.text)
                      # shop_id = ""
                      category_id= re.compile("item%5f(.*?)(?=&)").findall(response.text)[0]
                      shop_item['category_id']=category_id
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
                                               # prop_value_id.append(";".join(sub_value_id))
                                           if value.xpath('./a')[0].get('style') and re.compile("/([^/]*)(?=_!!|_M2)").findall(
                                               value.xpath('./a')[0].get('style')):
                                               sku_img_url=re.compile("/([^/]*)(?=_!!|_M2)").findall(value.xpath('./a')[0].get('style'))[0]
                                               sub_value_id.append(sku_img_url)
                                           prop_value_id.append(";".join(sub_value_id))
                                # shop_item[prop_name] ="&&||".join(prop_value_id)
                                    shop_item[prop_name] =prop_value_id
                      if html.xpath("//ul[@id='J_UlThumb']"):
                            stype_img_id=[]
                            if html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li/div"):
                                for value1 in html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li/div"):
                                         if value1.xpath('./a')[0].xpath('./img')[0].get('data-src') and re.compile("/([^/]*)(?=_!!|_M2)").findall(
                                               value1.xpath('./a')[0].xpath('./img')[0].get('data-src')):
                                               sku_img_id=re.compile("/([^/]*)(?=_!!|_M2)").findall(value1.xpath('./a')[0].xpath('./img')[0].get('data-src'))[0]
                                               stype_img_id.append(sku_img_id)
                            elif html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li"):
                                for value1 in html.xpath("//ul[@id='J_UlThumb']")[0].xpath(".//li"):
                                         if value1.xpath('./a')[0].xpath('./img')[0].get('src') and re.compile("/([^/]*)(?=_!!|_M2)").findall(
                                               value1.xpath('./a')[0].xpath('./img')[0].get('src')):
                                               sku_img_id=re.compile("/([^/]*)(?=_!!|_M2)").findall(value1.xpath('./a')[0].xpath('./img')[0].get('src'))[0]
                                               stype_img_id.append(sku_img_id)
                            shop_item["img_attr"]="&&||".join(stype_img_id)
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
                      shop_item["attribute"]="&&||".join(styleliList)
             except Exception, e:
                 logging.info("----详情抓取错误----".format(e=e.message))
             shop_items.append(shop_item)
        # self.shopall.insert_or_update(shop_items)
        post_data = {'data':json.dumps(shop_items)}
        if not self.process_request(SAVE__INSERT_API, post_data):
           sleep(3)
           self.process_request(SAVE__INSERT_API, post_data)
        if not self.process_request(SAVE__INSERT_API_ZS, post_data):
           sleep(3)
           self.process_request(SAVE__INSERT_API_ZS, post_data)

    def process_request(self, url, data):
        result_ok = False
        ok, result = Html_Downloader.Download_Html(url, data, {'timeout':60}, post=True)
        if ok:
            result_json = json.loads(result.content)
            result_ok = bool(result_json['flag'])
        return result_ok
    def crawl_shop_all_item(self):
        agentIp = Utils.GetMyAgent()
        shop_id =self.shop_id
        shop_name=self.shop_name
        session =Session()
        self.get_shop_item_list(session, agentIp,1,shop_id,shop_name)  # 首次获取会失败只为获取cookie
        total_page = 1
        for i in range(100):
            print i
            # 到最后一页就提前终止
            if total_page and i >= total_page:
                break
            result =self.get_shop_item_list(session, agentIp, (i+1),shop_id,shop_name)
            if not result:
                result =self.get_shop_item_list(session, agentIp, (i+1),shop_id,shop_name)
            print(result)
            jobj = json.loads(result.replace("mtopjsonp12(", "").replace("})", "}"))  # 获取解析的json
            #if(i>=7):
            jsonArray=jobj['data']['itemsArray']
            self.parse_items(jsonArray,shop_id,agentIp)
            if jobj and "SUCCESS" in jobj['ret'][0]:
                total = int(jobj['data']['totalResults'])
                total_page = total / 30  # 每页最多30个不能再多
                if total % 30:
                    total_page += 1
            else:
                print("获取数据失败")
                break
            sleep(2)
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
          try:
              startItemCrawl(shop_url,shop_id,shop_name)
              endtime =datetime.now()
              end_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
              runningTime=(endtime - starttime).seconds
              print("抓取消耗Time: %s" %runningTime)
          except Exception, e:
              logging.info("抓取店铺:{shop_name}失败,抓取店铺链接:{shop_url},店铺id:{shop_id},开始时间{start_time},结束时间{end_time},错误内容{m}".format(shop_name=shop_name,shop_url=shop_url,shop_id=shop_id,start_time=starttime,end_time=endtime,m=e.message))
              content="抓取店铺:{shop_name}失败".format(shop_name=shop_name)
              '''
              crawl_content=content
              getData="&shop_id="+shop_id+"&ip_addr="+agentIp+"&shop_name="+shop_name+"&shop_url"+shop_url+"&start_time="+start_time+"&end_time="+end_time+"&crawl_content="+crawl_content+"&error_info="+e.message
              #logUU="http://192.168.10.198:8080/pdd/CrawlerLogController/SaveCrawlerLog?shop_id=64469556&ip_addr=125.119.54.140&start_time=2017-09-15%2014:34:12&end_time=2017-09-15%2014:34:15&crawl_content=%E9%94%99%E8%AF%AFlog:crawl_url=https://bra360.taobao.comshop_name=%E8%9C%9C%E8%89%B2%E4%B9%8B%E5%90%BB%E5%86%85%E8%A1%A3%E9%A6%86&error_info=log404"

              logUU=log+getData
              ok, result = Html_Downloader.Download_Html(logUU,{},{})
              if ok:
                  result_json = json.loads(result.content)
                  result_ok = bool(result_json['flag'])
             '''




