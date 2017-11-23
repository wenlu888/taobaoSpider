# -*- coding: utf-8 -*-
import  requests
from utils.utils import Utils
import logging
import json
from lxml import etree
from pymongo import MongoClient
import time
from datetime import datetime
conn = MongoClient('172.16.100.110', 27017)
local_set = conn.pdd.SEJ_table
local_set_data = conn.pdd.SEJ_data
local_set_data2 = conn.pdd.SEJ_data_brand_volume
HEADERS = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Host':'c6.shengejing.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
}
COOKIE = 'route=015b72bb3cad540bdd042b8688ca04ce; PHPSESSID=7ge5u2468d8pp31pa68rru6fu7'
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in COOKIE.split(';')}
today = str(datetime.today()).split(' ')[0]
default_encoding = 'utf-8'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='E:\wenlu\Log\{name}.log'.format(name=today + "SYJ_data"),
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def get_sub_industry_list (year, mouth):
    try:
        sub_list = local_set.find({'cid':25})
    except Exception,e:
        logging.error("处理子行业数据时出现错误{e}".format(e=e.message))
        get_sub_industry_list(year,mouth)
    try:
        cid_list = list()
        have_sun_list = list()
        for sub in sub_list:
            cid = sub['cid']
            cid_list.append(cid)
            if sub['have_sun']:
                have_sun_list.append(sub)
        cid_list = list(set(cid_list))
        for cid in cid_list:
            cid_url = "http://c6.shengejing.com/index.php?year={year}&month={mouth}&subcid=&brand=&gcate=&cate=&cid={" \
                      "cid}&tab=3&func=3&subfunc=submarket&prop=&external=&startprice=&endprice=&custpriceinterval=10" \
                      "&priceview=default".format(year=year,mouth=mouth,cid=cid)
            html = get_response(cid_url)
            total = html.xpath("//table[@id='central']/tbody/tr/td[1]")
            if total == 0:
                count = 0
                while count < 4:
                    html = get_response(cid_url)
                    total = html.xpath("//*[@id='central']/tbody/tr/td[1]")
                    count += 1
                    if total != 0:
                        break
            for tr in range(1,len(total)+1):
                data = dict()
                data['子行业名称'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[1]'.format(tr=tr))[0].text
                data['成交量'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[2]'.format(tr=tr))[0].text
                data['销售额指数'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[3]'.format(tr=tr))[0].text
                data['高质宝贝数'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[4]'.format(tr=tr))[0].text
                data['crowl_time'] =  long(time.time())
                data['数据时间'] = str(year) + "_" + str(mouth)
                if cid == 16:
                    data['行业名称'] = "女装/女士精品"
                elif cid == 30:
                    data['行业名称'] = "男装"
                else:
                    data['行业名称'] = local_set.find({'cid':cid})[0]['cid_name']
                print data['子行业名称']
                try:
                    local_set_data.save(data)
                except Exception,e:
                    logging.error("遗失的数据为：{name}".format(name=data['子行业名称']))
        for have_sun in have_sun_list:
            need_cid = have_sun['cid']
            option_value = have_sun['option_value']
            sun_url = 'http://c6.shengejing.com/index.php?year={year}&month={mouth}&subcid={' \
                      'option_value}&brand=&gcate=&cate=&cid={need_cid}&tab=3' \
                      '&func=3&subfunc=submarket&prop=&external=&startprice=&endprice=&custpriceinterval=10&priceview' \
                      '=default '.format(year=year, mouth=mouth, option_value=option_value, need_cid=need_cid)
            html = get_response(sun_url)
            total = html.xpath("//*[@id='central']/tbody/tr/td[1]")
            if total ==0:
                count = 0
                while count <4:
                    html = get_response(sun_url)
                    total = html.xpath("//*[@id='central']/tbody/tr/td[1]")
                    count += 1
                    if total != 0:
                        break
            for tr in range(1,len(total)+1):
                data = dict()
                data['子行业名称'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[1]'.format(tr=tr))[0].text
                data['成交量'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[2]'.format(tr=tr))[0].text
                data['销售额指数'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[3]'.format(tr=tr))[0].text
                data['高质宝贝数'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[4]'.format(tr=tr))[0].text
                data['crowl_time'] = long(time.time())
                data['行业名称'] = have_sun['option_name']
                data['数据时间'] = str(year)+"_"+str(mouth)
                print data['子行业名称']
                try:
                    local_set_data.save(data)
                except Exception,e:
                    logging.error("遗失的数据为：{name}".format(name=data['子行业名称']))
    except Exception,e:
        logging.error("处理子行业数据时出现错误{e}".format(e=e.message))
        # get_sub_industry_list(year, mouth)


def get_brand_volume(year,month):
    try:
        sub_list = local_set.find({'cid': 25},no_cursor_timeout=True)
    except Exception,e:
        logging.error("查询mongdb时出现错误{e}".format(e=e.message))
        get_brand_volume(year,month)
    try:
        for sub in sub_list:
            cid = sub['cid']
            option_value = sub['option_value']
            option_name = sub['option_name']
            url = "http://c6.shengejing.com/index.php?year={year}&month={month}&subcid={subcid}&brand=&gcate=&cate=&cid={" \
                  "cid}&tab=3&func=3&subfunc=brand&prop=&external=&startprice=&endprice=&custpriceinterval=10&priceview" \
                  "=default ".format(year=year,month=month,subcid=option_value,cid=cid)
            html = get_response(url)
            total = html.xpath("//table[@id='central']/tbody/tr/td[1]")
            if total == 0:
                count = 0
                while count < 4:
                    html = get_response(url)
                    total = html.xpath("//*[@id='central']/tbody/tr/td[1]")
                    count += 1
                    if total != 0:
                        break
            for tr in range(1,len(total)+1):
                print "爬取品牌销量:{sub}".format(sub=option_name)
                data = dict()
                # //*[@id="central"]/tbody/tr[4]/td[1]
                data['子行业内品牌名'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[1]'.format(tr=tr))[0].text
                data['品牌成交量'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[2]'.format(tr=tr))[0].text
                data['品牌销售额'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[3]'.format(tr=tr))[0].text
                data['品牌高质宝贝数'] = html.xpath('//*[@id="central"]/tbody/tr[{tr}]/td[4]'.format(tr=tr))[0].text
                data['crowl_time'] = long(time.time())
                data['子行业名称'] = option_name
                data['数据时间'] = str(year) + "_" + str(month)
                try:
                    local_set_data2.save(data)
                except Exception,e:
                    logging.error("数据处理时出现错误：{e}，遗失的数据为：{name}".format(e=e.message,name=data['子行业名称']))
        sub_list.close()
    except Exception,e:
        logging.error("数据处理时出现错误：{e}".format(e=e.message))
        # get_brand_volume(year, month)


def get_response(url):
    try:
        proxy = dict()
        proxy['HTTP'] = Utils.GetMyAgent()
        #proxy['HTTP'] ={'HTTP':'182.34.50.90:808'}
        respones = requests.get(url=url, cookies=cookie_dict, headers=HEADERS, verify=False,proxies=proxy).text
        html = etree.HTML(respones)
        time.sleep(8)
    except Exception, e:
        logging.error("获取响应时出现错误{e}".format(e=e.message))
        get_response(url)
    return html


if __name__ == '__main__':
    starttime = datetime.now()
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for i in range(2016,2017):
        for j in range (12,13):
            if j < 10:
                logging.info("开始爬取{year}年{mouth}数据".format(year=i,mouth=j))
                get_sub_industry_list(i, '0'+str(j))
                get_brand_volume(i, '0'+str(j))
            else:
                logging.info("开始爬取{year}年{mouth}数据".format(year=i, mouth=j))
                # get_sub_industry_list(i, str(j))
                get_brand_volume(i, str(j))
    endtime = datetime.now()
    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    runningTime = (endtime - starttime).seconds
    logging.info("共计爬取时间：{runtime}".format(runtime=runningTime))
