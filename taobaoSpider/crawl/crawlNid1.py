# -*- coding: utf-8 -*-
from requests import Session
#用于抓取指定关键词top100宝贝的id和销量(付款人数)
from time import sleep
from lxml import etree
from utils.utils import Utils
from utils.html_downloader import Html_Downloader
from config import PROJECT_PATH, SEPARATOR
import sys
import logging
import re
import PyV8
import json
from datetime import datetime
from db.DataStore1 import KeywordItem
import time
from config import SAVE_INSERT_KEYWORD_API
from config import GET_SHOP_ID_API
from config import SAVE__Crawler_Log
import logging
import chardet
default_encoding = 'utf-8'
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='a')
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
def startNidCrawl(keyword):
    crawl = CrawlNid1(keyword)
    crawl.run()
class CrawlNid1(object):
    def __init__(self, keyword):
        self.key_word = keyword
        self.shopall = KeywordItem()
    def run(self):
        agentip = Utils.GetMyAgent()
        agentipjj= Utils.GetMyAgent()
        day = datetime.now().strftime("%Y%m%d")
        search_url="https://s.taobao.com/search?q={q}&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_{day}&ie=utf8&bcoffset=0&ntoffset=1&p4ppushleft=%2C44&sort=sale-desc&s={s}";
        page_Url=search_url.format(q=self.key_word,day=day,s=0)
        header = {'ip': agentip}
        total=3
        totalpage=self.crawlTotalpage(page_Url,header)
        total = totalpage if totalpage < total else total
        total=total+1
        for i in range(1, total):
            t_url =search_url.format(q=self.key_word, day=day, s=(i-1)*44)
            try:
                ok, response = Html_Downloader.Download_Html(t_url,{}, header)
                if not ok:
                      count =0
                      while(count<4):
                            sleep(2)
                            agentip = Utils.GetMyAgent()
                            header = {'ip': agentip}
                            ok, response = Html_Downloader.Download_Html(t_url,{},header)
                            if ok:
                                break
                            count+=1
                            if count==3:
                                header={}
                if ok:
                    html = etree.HTML(response.text)
                    matchs = html.xpath("//script[contains(.,'g_page_config')]")
                    if len(matchs) > 0:
                         data = re.compile("g_page_config=(.*)?;g_srp_loadCss").match(
                                matchs[0].text.replace("\n\n", "\n").replace("\n", "").replace(" ", ""))
                         if data.lastindex > 0:
                            data = json.loads(data.group(1).encode('utf-8'))
                            if data.has_key('mods'):
                                self.crawlNid(data,i,agentip,agentipjj)
                         else:
                            print("无法匹配有效的json")
                    else:
                     print("无法匹配到宝贝列表")
                else:
                     logging.info("关键词{p}第{i}页抓取失败{m}".format(p=self.key_word, i=i, m=e.message))
            except Exception, e:
                logging.info("关键词{p}第{i}页抓取错误{m}".format(p=self.key_word, i=i, m=e.message))

    def crawlTotalpage(self, search_url,header):
        try:
                ok, response = Html_Downloader.Download_Html(search_url,{}, header)
                if not ok:
                      count =0
                      while(count<4):
                            sleep(2)
                            agentip = Utils.GetMyAgent()
                            header = {'ip': agentip}
                            ok, response = Html_Downloader.Download_Html(search_url,{},header)
                            if ok:
                                break
                            count+=1
                            if count==3:
                                header={}
                if ok:
                    html = etree.HTML(response.text)
                    matchs = html.xpath("//script[contains(.,'g_page_config')]")
                    if len(matchs) > 0:
                         data = re.compile("g_page_config=(.*)?;g_srp_loadCss").match(
                                matchs[0].text.replace("\n\n", "\n").replace("\n", "").replace(" ", ""))
                         if data.lastindex > 0:
                            data = json.loads(data.group(1).encode('utf-8'))
                            if data.has_key('mods'):
                                totalpage = data['mods']['pager']['data']['totalPage']
                    else:
                        print("无法匹配有效的json")
                else:
                    print("无法匹配到宝贝列表")
        except Exception, e:
                logging.info("关键词{p}第{i}页抓取错误{m}".format(m=e.message))
        return totalpage
    def execute_javascript(self,txt):
        js_path = "%s%s%s" % (PROJECT_PATH, SEPARATOR, "taobao_sign_js")
        file = open(js_path, 'r')
        js = file.read()
        ctxt = PyV8.JSContext()
        ctxt.enter()
        func = ctxt.eval(js)
        result_txt = func(txt)
        return result_txt
    def get_total_sales(self, session,agentipjj,page_num,shop_id):
          try:
             count=0
             while(count<20):
                    print("agentipjj:"+agentipjj)
                    proxies = {"http": agentipjj, "https": agentipjj}
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
                    if agentipjj:
                        requests_parms['proxies'] = proxies
                        requests_parms['verify'] = False
                    try:
                       result = session.get(url, headers=headers, **requests_parms)
                    except Exception, e:
                       agentipjj=Utils.GetMyAgent()
                       continue
                    count=count+1
                    if result.status_code!=200:
                        logging.info("代理ip返回结果{log_code}".format(log_code=result.status_code))
                        agentipjj=Utils.GetMyAgent()
                        sleep(2)
                    else:
                        print(result.status_code)
                    if result.ok:
                        sleep(2)
                        return result.content
                        break
          except Exception, e:
              #shop_id={shop_id}&sort=d".format(shop_id=shop_id)
            logging.info("抓取totalSoldQuantity有错{m}".format(m=e.message))
            print("抓取totalSoldQuantity有错{e}".format(e=e.message))
    def parse_total_sales(self,jsonArray,nid):
        totalsasel=-1
        for item in jsonArray:
            auctionId=item.get('auctionId')
            if auctionId==nid:
                totalsasel=item.get('totalSoldQuantity')
                break
        return  totalsasel
    def crawlNid(self, data,i,agentip,agentipjj):
        items = data['mods']['itemlist']['data']['auctions']
        x=(i-1)*44+1
        agentip = Utils.GetMyAgent()
        for item in items:
                shop_items = []
                shop_item = {}
                shop_item['keyword'] =self.key_word
                title=item['title']
                isTmall=item['shopcard']['isTmall']
                shop_item['isTmall'] =isTmall
                title=title.replace("<spanclass=H>","").replace("</span>","").strip();
                shop_item['title'] =title
                nid=item['nid'].strip()
                shop_item['item_id'] =nid
                view_sales= item['view_sales'].strip()
                view_sales=view_sales.replace("人收货,","").replace("人收货","").strip();
                shop_item['view_sales'] =view_sales
                shop_item['view_price'] =item['view_price'].strip()
                shop_item['picUrl'] ="http:"+item['pic_url'].strip()
                shop_item['idnick'] =item['nick'].strip()
                shop_item['crawl_time'] =long(time.time())
                shop_item['rank'] =x
                print(x)
                if x==101:
                    break
                x+=1
                #if(x<=5):
                   # continue
                detail_url="https://detail.tmall.com/item.htm?spm=a230r.1.14.1.ebb2eb2PXquhm&id={nid}&ns=1&abbucket=20"
                t_detail_url=detail_url.format(nid=nid)
                header = {'ip': agentip}
                try:
                   sleep(2)
                   ok, response = Html_Downloader.Download_Html(t_detail_url,{}, header)
                   if not ok:
                      count =0
                      while(count<4):
                            sleep(2)
                            agentip = Utils.GetMyAgent()
                            header = {'ip': agentip}
                            ok, response = Html_Downloader.Download_Html(t_detail_url,{},header)
                            if ok:
                                break
                            count+=1
                            if count==3:
                                header={}
                   if ok:
                      html = etree.HTML(response.text)
                      if not "shopid" in response.text:
                           count =0
                           while(count<4):
                                sleep(2)
                                agentip = Utils.GetMyAgent()
                                header = {'ip': agentip}
                                ok, response = Html_Downloader.Download_Html(t_detail_url,{}, header)
                                if ok:
                                   html = etree.HTML(response.text)
                                   if "shopid" in response.text:
                                       break
                                count+=1
                                if count==3:
                                    header={}
                      shop_id = ""
                      # user_id=""
                      category_id= re.compile("item%5f(.*?)(?=&)").findall(response.text)[0]
                      shop_item['category_id']=category_id
                      if html.xpath("//meta[@name='microscope-data']"):
                         for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                            if 'shopid' in meta.lower():
                              shop_id = meta.split("=")[1]
                            # if 'userid=' in meta.lower():
                            #   user_id= meta.split("=")[1]
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
                                           if value.xpath('./a')[0].get('style') and re.compile("/([^/]*)(?=_!!|_M2)").findall(
                                               value.xpath('./a')[0].get('style')):
                                               sku_img_url=re.compile("/([^/]*)(?=_!!|_M2)").findall(value.xpath('./a')[0].get('style'))[0]
                                               sub_value_id.append(sku_img_url)
                                           prop_value_id.append(";".join(sub_value_id))
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
                            shop_item["attr_img"]="&&||".join(stype_img_id)
                      if html.xpath("//ul[@id='J_AttrUL']"):
                          styleliList=[]
                          # dict={}
                          for styleli in html.xpath("//ul[@id='J_AttrUL']")[0].xpath(".//li"):
                               if styleli.xpath('./text()'):
                                  styleliText= styleli.xpath('./text()')[0].encode('utf-8').strip()
                                  # styleliText=styleliText.replace("：",":")
                                  # str1=styleliText.split(":")[0].encode('utf-8').strip()
                                  # str2=styleliText.split(":")[1].encode('utf-8').strip().replace("\xc2\xa0"," ").lstrip()
                                  # dict[str1] =str2
                                  styleliList.append(styleliText)
                      elif html.xpath("//div[@id='attributes']"):
                          styleliList=[]
                          # dict={}
                          for styleli in html.xpath("//div[@id='attributes']")[0].xpath(".//ul/li"):
                             if styleli.xpath('./text()'):
                                styleliText= styleli.xpath('./text()')[0].encode('utf-8').strip()
                                # styleliText=styleliText.replace("：",":")
                                # str1=styleliText.split(":")[0].encode('utf-8').strip()
                                # str2=styleliText.split(":")[1].encode('utf-8').strip().replace("\xc2\xa0"," ").lstrip()
                                # dict[str1] =str2
                                styleliList.append(styleliText)
                      shop_item["attribute"]="&&||".join(styleliList)
                      # shop_item["attribute"]=dict
                except Exception, e:
                    logging.info("关键词{p}抓取失败,nid={nid},{m}".format(p=self.key_word,nid=nid, m=e.message))
                shop_item['crawl_url']=t_detail_url
                shop_item['shop_id']=shop_id
                session =Session()
                self.get_total_sales(session,agentip,1,shop_id)  #首次获取会失败只为获取cookie
                total_page = 1
                for i in range(50):
                    # 到最后一页就提前终止
                    if total_page and i >= total_page:
                        break
                    result =self.get_total_sales(session, agentip, (i + 1),shop_id)
                    if not result:
                        result =self.get_total_sales(session, agentip, (i + 1),shop_id)
                    if(result!=None):
                        jobj = json.loads(result.replace("mtopjsonp12(", "").replace("})", "}"))  # 获取解析的json
                        jsonArray=jobj['data']['itemsArray']
                        total_sales=self.parse_total_sales(jsonArray,nid)
                        if total_sales!=-1:
                            break
                        if jobj and "SUCCESS" in jobj['ret'][0]:
                            total = int(jobj['data']['totalResults'])
                            total_page = total / 30  # 每页最多30个不能再多
                            if total % 30:
                                total_page += 1
                        else:
                            print("获取数据失败")
                            break
                        sleep(2)
                    else:
                        total_sales=""
                shop_item['totalSoldQuantity']=total_sales
                shop_items.append(shop_item)
                post_data = {'data':json.dumps(shop_items)}
                if not self.process_request(SAVE_INSERT_KEYWORD_API, post_data):
                    self.process_request(SAVE_INSERT_KEYWORD_API, post_data)
    def process_request(self, url, data):
        result_ok = False
        ok, result = Html_Downloader.Download_Html(url, data, {'timeout':60}, post=True)
        if ok:
            result_json = json.loads(result.content)
            result_ok = bool(result_json['flag'])
            print (result_json['message'])
        return result_ok
def crawl_keyWord(shop_id_url):
    keyword=""
    try:
        ok, result = Html_Downloader.Download_Html(shop_id_url,{},{})
        if ok:
            result_json = json.loads(result.content)
            result_ok = bool(result_json['status'])
            keyword=result_json['data'][0]['keyword'].encode('utf-8').strip()
        else:
            print('调用接口获取关键词失败')
    except Exception,e:
         logging.info("获取关键词失败{e}".format(e=e.message))
    return  keyword
if __name__ == "__main__":
    starttime =datetime.now()
    #调用接口获取关键词
    #shop_id_url=GET_SHOP_ID_API
    #keyword=crawl_keyWord(shop_id_url)
    keyword="连衣裙"
    startNidCrawl(keyword)
    endtime =datetime.now()
    runningTime=(endtime - starttime).seconds
    print("抓取消耗Time: %s" %runningTime)
    pass