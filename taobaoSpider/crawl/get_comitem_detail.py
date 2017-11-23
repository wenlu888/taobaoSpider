# -*- coding: utf-8 -*-
# ---------------------------
# 脚本效果：爬取竞品数据并完成存储已经完成流程化
# 注意：1、爬取月销量需要登录后店铺cookie，可用时间约1天左右。
#      2、爬取过程中应用了页面详情页的解析，所以稳定性可能一般，需要大批量数据测试
# ---------------------------
import requests
from utils.utils import Utils
# from fake_useragent import UserAgent
from lxml import etree
from utils.html_downloader import Html_Downloader
import json
import logging
from time import sleep
import time
import re
import sys
from config import SAVE__INSERT_API
from config import SAVE__INSERT_API_ZS
from datetime import datetime
default_encoding = 'utf-8'
today = str(datetime.today()).split(' ')[0]
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='E:\wenlu\Log\{name}.log'.format(name=today+" crawlComItems"),
                filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
class get_datail(object):
    @staticmethod
    def get_item():
        # 调用接口获取需要爬取的宝贝，并对数据进行判定，如果存在则进行宝贝详情数据更新，如果不存在则对宝贝数据进行完善
        com_items_url = "http://192.168.10.198:8080/pdd/MonitorCowryController/getMonitorCowry"
        com_items = requests.get(com_items_url, verify=False).text
        com_items = json.loads(com_items)['data']
        com_items = com_items[13:]
        for com_item in com_items:
            item_url = com_item['item_url']
            item_id = com_item['item_id']
            belong_shop_id = com_item['belong_shop_id']
            id = com_item['id']
            #直接爬取竞品数据并存入数据库
            comitem = get_datail.comitem_datail(item_url, item_id)
            # 在数据库没有竞店shop_id和shop_name情况下直接爬取竞店信息
            if com_item['monitor_shop_id'] == None or com_item['monitor_shop_name'] == None:
                monitor_shop_id = comitem['shop_id']
                monitor_shop_name = comitem['shop_name']
                record_time = long(time.time())
                # 更新竞品数据的url,最好应放到config中
                com_data_url = "http://192.168.10.198:8080/pdd/MonitorCowryController/UpdateMonitorCowry?id={id}&" \
                               "belong_shop_id={belong_shop_id}&monitor_shop_id={monitor_shop_id}&monitor_shop_name=" \
                               "{monitor_shop_name}&item_url={item_url}&item_id={item_id}&record_time={record_time}".format(
                        id=id, belong_shop_id=belong_shop_id, monitor_shop_id=monitor_shop_id,
                        monitor_shop_name=monitor_shop_name, item_url=item_url, item_id=item_id,record_time=record_time)
                requests.get(com_data_url, verify=False)

    @staticmethod
    def comitem_datail(item_url, item_id):
        agentIp = dict()
        comitem_detail = dict()
        agentIp['HTTPS'] = Utils.GetMyAgent()
        # url = "https://item.taobao.com/item.htm?id={item_id}".format(item_id=self.item_id)
        # ua = UserAgent()
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        comitem_detail['crawl_url'] = item_url
        comitem_detail['item_id'] = item_id
        logging.info("开始爬取宝贝id为：{item_id}的宝贝".format(item_id=item_id))
        # 爬取淘宝详情页
        try:
            if "taobao" in item_url:
                try:
                    response = requests.get(item_url, proxies=agentIp, verify=False, headers=headers)
                    if response.status_code == 200 and "J_ImgBooth" in response.text:
                        html = etree.HTML(response.text)
                        # 竞品图片url
                        picUrl = html.xpath("//img[@id='J_ImgBooth']/@src")[0]
                        comitem_detail['picUrl'] = "https:"+picUrl
                    else:
                        count = 0
                        while count <3:
                            agentIp['HTTPS'] = Utils.GetMyAgent()
                            logging.info("第{count}次发送请求获取宝贝详情页(天猫)".format(count=count))
                            response = requests.get(item_url, proxies=agentIp, verify=False, headers=headers)
                            if response.status_code == 200 and "J_ImgBooth" in response.text:
                                html = etree.HTML(response.text)
                                picUrl = html.xpath("//img[@id='J_ImgBooth']/@src")[0]
                                comitem_detail['picUrl'] = "https:"+picUrl
                                break
                            else:
                                count += 1
                except Exception, e:
                    logging.ERROR("获取图片url出错：{m},宝贝id为：{item_id}".format(m=e.message, item_id=item_id))
                # 竞品标题
                comitem_detail['title'] = html.xpath("//h3[@class='tb-main-title']")[0].text.strip()
                if html.xpath("//meta[@name='microscope-data']"):
                    for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                        if 'shopid' in meta.lower():
                            shop_id = meta.split("=")[1]
                comitem_detail['shop_id'] = shop_id
                # shopName= re.compile("shopName(.*?)(?=sellerId)").findall(response.strip())[0]
                # 竞店店铺名
                comitem_detail['shopName'] = html.xpath("//div[@class='tb-shop-name']/dl/dd/strong/a")[0].text.strip()
            # 爬取天猫详情页
            else:
                try:
                    response = requests.get(item_url, proxies=agentIp, verify=False, headers=headers)
                    if response.status_code == 200 and "J_ImgBooth" in response.text:
                        html = etree.HTML(response.text)
                        # 竞品图片url
                        picUrl = html.xpath("//img[@id='J_ImgBooth']/@src")[0]
                        comitem_detail['picUrl'] = "https:"+picUrl
                    else:
                        count = 0
                        while count < 3:
                            agentIp['HTTPS'] = Utils.GetMyAgent()
                            response = requests.get(item_url, proxies=agentIp, verify=False, headers=headers)
                            logging.info("第{count}次发送请求获取宝贝详情页(天猫)".format(count=count))
                            if response.status_code == 200 and "J_ImgBooth" in response.text:
                                html = etree.HTML(response.text)
                                picUrl = html.xpath("//img[@id='J_ImgBooth']/@src")[0]
                                comitem_detail['picUrl'] = "https:"+picUrl
                                break
                            else:
                                count += 1
                except Exception, e:
                    logging.ERROR("获取图片url出错：{m},宝贝id为：{item_id}".format(m=e.message,item_id=item_id))
                # 竞品标题
                comitem_detail['title'] = html.xpath("//div[@class='tb-detail-hd']/h1")[0].text.strip()
                if html.xpath("//meta[@name='microscope-data']"):
                    for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                        if 'shopid' in meta.lower():
                            shop_id = meta.split("=")[1]
                comitem_detail['shop_id'] = shop_id
                # shopName= re.compile("shopName(.*?)(?=sellerId)").findall(response.strip())[0]
                # 竞店店铺名
                comitem_detail['shopName'] = html.xpath("//a[@class='slogo-shopname']/strong")[0].text.strip()
        except Exception, e:
            logging.error("通过解析页面获取数据发生异常：{m}，店铺名：{shopName}".format(m=e.message,shopName=comitem_detail['shopName']))
        agentip2 = Utils.GetMyAgent()
        # 获得月销量
        comitem_detail['month_Sales'] = get_datail.crawlMonthSales(item_id, agentip2,)
        category_id = ""
        category_id_Url = "http://d.da-mai.com/index.php?r=itemApi/getItemInfoByItemId&item_id=" + item_id
        header = {'ip': agentip2, 'user-agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"}
        ok, response = Html_Downloader.Download_Html(category_id_Url, {}, header)
        if not ok:
            count = 0
            while count < 3:
                sleep(1)
                agentip = Utils.GetMyAgent()
                header = {'ip': agentip}
                ok, response = Html_Downloader.Download_Html(category_id_Url, {}, header)
                if ok:
                    break
                count += 1
                if count == 3:
                    header = {}
        if ok:
            jsonItems = json.loads(response.content)
            category_id = jsonItems['data']['data']['cid']
        total_quantity = 0
        quantity_Url = "http://yj.da-mai.com/index.php?r=itemskus/getSkus&fields=*&num_iids={item_id}".format(
                item_id=item_id)
        ok, response = Html_Downloader.Download_Html(quantity_Url, {}, header)
        if not ok:
            count = 0
            while count < 4:
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
            while count < 4:
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
        comitem_detail['category_id'] = str(category_id)
        comitem_detail['quantity'] = str(total_quantity)
        comitem_detail['crawl_time'] = long(time.time())
        comitem = [comitem_detail]
        post_data = {'data':json.dumps(comitem)}
        if not get_datail.process_request(SAVE__INSERT_API, post_data):
            sleep(3)
            get_datail.process_request(SAVE__INSERT_API, post_data)
        # if not get_datail.process_request(SAVE__INSERT_API_ZS, post_data):
        #     sleep(3)
        #     get_datail.process_request(SAVE__INSERT_API_ZS, post_data)
        # return comitem_detail

    @staticmethod    # 数据序列化
    def process_request(url, data):
        result_ok = False
        ok, result = Html_Downloader.Download_Html(url, data, {'timeout':60}, post=True)
        if ok:
            result_json = json.loads(result.content)
            result_ok = bool(result_json['flag'])
            print result_ok
        return result_ok

    @staticmethod      # 爬取月销量
    def crawlMonthSales(nid, agentip):
        try:
            month_Sales = ""
            nid_url = "https://mdskip.taobao.com/core/initItemDetail.htm?itemId={nid}"
            refer_url = "https://detail.taobao.com/item.htm?id={nid}"
            nid_Url = nid_url.format(nid=nid)
            nid_refer = refer_url.format(nid=nid)
            cookies = "ab=12; UM_distinctid=15e7a46caf311b-0188d989dac01e-5c153d17-144000-15e7a46caf4552; thw=cn; ali_apache_id=11.131.226.119.1505353641652.239211.1; miid=2033888855982094870; l=AllZcEkSLTy0io2vJcWc-ksY6U4zk02Y; _cc_=WqG3DMC9EA%3D%3D; tg=0; _uab_collina=150780747345339957932139; cna=dNU/EvGIRjsCAQ4XY4PdDkHN; _tb_token_=3d73497b6b4b1; ali_ab=14.23.99.131.1510570522194.8; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; x=124660357; uc3=sg2=AVMH%2FcTVYAeWJwo98UZ6Ld9wxpMCVcQb0e1XXZrd%2BhE%3D&nk2=&id2=&lg2=; uss=VAmowkFljKPmUhfhc%2B1GBuXNJWn9cLMEX%2FtIkJ5j0tQgoNppvUlaKrn3; tracknick=; sn=%E4%BE%9D%E4%BF%8A%E6%9C%8D%E9%A5%B0%3A%E8%BF%90%E8%90%A5; skt=0e5a260ab8937fce; v=0; cookie2=17f5415096176ca88c03d1fed693a1d4; unb=2077259956; t=1630b104e4d32df897451d6c96642469; _m_h5_tk=66b057f261b6fcec7f0ace77c9f21d71_1511054204654; _m_h5_tk_enc=c8a74858b6e3ba407aeb33c19366a9cd; uc1=cookie14=UoTdevxw5pf0Qg%3D%3D&lng=zh_CN; isg=Ap-fotQUOUYumD7zwF6KwBiqLvPprPiz4as54THsKM6XwL9COdSD9h0S9GZF; _umdata=85957DF9A4B3B3E8F872A3094256432F0F1549AE1C92C6CCF1E68B982581686F23BFC13A60CCABD1CD43AD3E795C914CF14B199E3D11F637B5B193797399B50B"
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


if __name__ == '__main__':
    starttime = datetime.now()
    get_datail.get_item()
    endtime = datetime.now()
    runningTime = (endtime - starttime).seconds
    logging.info("共计爬取时间：{runtime}".format(runtime=runningTime))