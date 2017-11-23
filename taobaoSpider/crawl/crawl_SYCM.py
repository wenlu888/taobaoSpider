# -*- coding: utf-8 -*-
import requests
import json
from lxml import etree
from utils.html_downloader import Html_Downloader
from fake_useragent import UserAgent
from pymongo import MongoClient
from utils.utils import Utils
import time
HEADERS = {
    # 'User-Agent': ua.random,
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    # 'Referer': "https://detail.taobao.com/item.htm?id=546615137384",
    'Host': 'sycm.taobao.com',
    'Referer':'https://sycm.taobao.com/mq/industry/rank/industry.htm?spm=a21ag.7782692.LeftMenu.d342.513a3619eWqebd'
    # 'Upgrade-Insecure-Requests': '1'
}
COOKIE = "UM_distinctid=15e7a46caf311b-0188d989dac01e-5c153d17-144000-15e7a46caf4552; thw=cn; ali_apache_id=11.131.226.119.1505353641652.239211.1; miid=2033888855982094870; l=AllZcEkSLTy0io2vJcWc-ksY6U4zk02Y; _cc_=WqG3DMC9EA%3D%3D; tg=0; cna=dNU/EvGIRjsCAQ4XY4PdDkHN; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; _tb_token_=eb16eb075db6f; cookie2=3bd452168701ba9667662201cc96272e; t=1630b104e4d32df897451d6c96642469; ali_ab=14.23.99.131.1510570522194.8; JSESSIONID=5DDF1D853EFD6CD01FD2968E8B8DA2C1; x=78550821; uc3=sg2=WqUP2bQgEyBZjaQsNz6Zq8zb%2FPTkQqprbFHUVLha2bQ%3D&nk2=&id2=&lg2=; uss=BxuX4xOXjRUDj3bM7JJWPiIY56IozO16fuxNOi3XJJYnMd5w%2Bzv0zaGfdIY%3D; tracknick=; sn=%E8%8B%B1%E8%AF%AD%E4%BA%8C%E6%B2%B9%E6%9D%A1%3A%E5%88%86%E6%9E%90; unb=3464634750; skt=711fc32976c66b8d; v=0; _euacm_ac_rs_sid_=64469556; _euacm_ac_l_uid_=3464634750; 3464634750_euacm_ac_c_uid_=78550821; 3464634750_euacm_ac_rs_uid_=78550821; _m_h5_tk=7b839f51250e5d3cd953a4f73eedbdee_1510650351773; _m_h5_tk_enc=c1ccc5305dc67595b76a0351d1072124; uc1=cookie14=UoTde9BR2DTQEw%3D%3D&lng=zh_CN; isg=AlhY91z6tjFiOpkGo3v1PWtHKYYq6bfe8lZeNJJJpBNGLfgXOlGMW26PE1Pm; apush8f4098f91aa68430ce451009e44d4a93=%7B%22ts%22%3A1510649010818%2C%22heir%22%3A1510647469186%2C%22parentId%22%3A1510639647253%7D"
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in COOKIE.split(';')}
conn = MongoClient('192.168.10.198', 27017)
local_set = conn.pdd.sycm3
local_set2 = conn.pdd.sycm_items_coming_PC

def get_response(cate,i):
    agentIp = dict()
    agentIp['HTTPS'] = Utils.GetMyAgent()
    url = "https://sycm.taobao.com/mq/rank/listItems.json?cateId={cate}&categoryId={cate}&dateRange=2017-11-06%7C2017-11-12&dateRangePre=2017-11-06|2017-11-12&dateType=recent7&dateTypePre=recent7&device=0&devicePre=0&itemDetailType=1&keyword=&orderDirection=desc&orderField=payOrdCnt&page={page}&pageSize=100&rankTabIndex=0&rankType=1&seller=-1&token=67868107c&view=rank&_=1510572223929".format(page=i,cate=cate)
    response = requests.get(url=url, headers=HEADERS, proxies=agentIp, verify=False, cookies=cookie_dict).text
    return response

# 50008882,50008883    50008881


def get_all_json():
    for cate in [50008882,50008883,50008881]:
        for i in range(1,6):
            response = get_response(cate,i)
            if "操作成功" in response:
                data = json.loads(response)
                datas = data['content']['data']['data']
            else:
                time.sleep(15)
                response = get_response(cate, i)
                data = json.loads(response)
                datas = data['content']['data']['data']
            for need_data in datas:
                DATA = dict()
                DATA['cate'] = cate
                DATA['热销排名'] = need_data['orderNum']
                DATA['商品信息'] = need_data['itemTitle']
                DATA['店铺网址'] = "https:"+need_data['shopUrl']
                DATA['支付子订单'] = int(need_data['payOrdCnt'])
                DATA['所属店铺'] = need_data['shopName']
                if "tradeIndexCrc" in str(need_data):
                    DATA['交易增长幅度'] = str(float(need_data['tradeIndexCrc'])*100)+'%'
                DATA['支付转化率指数'] = need_data['payByrRateIndex']
                DATA['产品价格'] = need_data['itemPrice']
                DATA['item_id'] = need_data['itemId']
                local_set.save(DATA)


# db.getCollection('sycm').find({"所属店铺":/六只兔子/})
def get_detail():
    rabbits = local_set.find({"所属店铺":"六只兔子 高端内裤 内衣店"})
    rabbits2 = local_set.find({"所属店铺":"莎琪儿私藏内衣店"})
    for rabbit in rabbits2:
        # 引流关键词
        coming_url_coming = "https://sycm.taobao.com/mq/rank/listItemSeKeyword.json?cateId={cate}&categoryId={cate}&dateRange=2017-11-07%7C2017-11-13&dateRangePre=2017-11-06|2017-11-12&dateType=recent7&dateTypePre=recent7&device=0&devicePre=0&itemDetailType=1&itemId={itemid}&latitude=undefined&rankTabIndex=0&rankType=1&seller=-1&token=67868107c&view=detail&_=1510630823012".format(cate=rabbit['cate'],itemid=rabbit['item_id'])
        # Top10成交关键词
        coming_url_deal = "https://sycm.taobao.com/mq/rank/listKeywordOrder.json?cateId={cate}&categoryId={cate}&dateRange=2017-11-07%7C2017-11-13&dateRangePre=2017-11-06|2017-11-12&dateType=recent7&dateTypePre=recent7&device=0&devicePre=0&itemDetailType=1&itemId={itemid}&latitude=undefined&rankTabIndex=0&rankType=1&seller=-1&token=67868107c&view=detail&_=1510630823016".format(cate=rabbit['cate'],itemid=rabbit['item_id'])
        # 无线端来源(流量来源)
        coming_url_wlSeList = "https://sycm.taobao.com/mq/rank/listItemSrcFlow.json?cateId={cate}&categoryId={cate}&dateRange=2017-11-13%7C2017-11-13&dateRangePre=2017-11-07|2017-11-13&dateType=recent1&dateTypePre=recent7&device=2&devicePre=0&itemDetailType=1&itemId={itemid}&rankTabIndex=0&rankType=1&seller=-1&token=67868107c&view=detail&_=1510632184267".format(cate=rabbit['cate'],itemid=rabbit['item_id'])
        # PC端来源(流量来源)
        coming_url_PC = "https://sycm.taobao.com/mq/rank/listItemSrcFlow.json?cateId={cate}&categoryId={cate}&dateRange=2017-11-13%7C2017-11-13&dateRangePre=2017-11-07|2017-11-13&dateType=recent1&dateTypePre=recent7&device=1&devicePre=0&itemDetailType=1&itemId={itemid}&rankTabIndex=0&rankType=1&seller=-1&token=67868107c&view=detail&_=1510632184266".format(cate=rabbit['cate'],itemid=rabbit['item_id'])
        agentIp = dict()
        agentIp['HTTPS'] = Utils.GetMyAgent()
        try:
            '''
            if coming_url_coming:
                time.sleep(4)
                response = requests.get(url=coming_url_coming, headers=HEADERS, proxies=agentIp, verify=False,
                                        cookies=cookie_dict).text
                if "操作成功" in response:
                    need_datas = json.loads(response)['content']['data']
                    for need_date in need_datas:
                        for need in need_datas[str(need_date)]:
                            data = dict()
                            data['name'] = "Top10引流关键词"
                            data['coming_from'] = str(need_date)
                            # data_keyword = dict()
                            data['shop_name'] = "六只兔子 高端内裤 内衣店"
                            data['keyword'] = need['keyword']
                            data['uv'] = need['uv']
                            data['itemid'] = rabbit['item_id']
                            # data_keyword_list.append(data_keyword)
                            # data['流量明细'] = data_keyword_list
                            local_set2.save(data)
                            # data = dict()
                else:
                    time.sleep(30)
                    response = requests.get(url=coming_url_coming, headers=HEADERS, proxies=agentIp, verify=False,
                                            cookies=cookie_dict).text
                    need_datas = json.loads(response)['content']['data']
                    for need_date in need_datas:
                        for need in need_datas[str(need_date)]:
                            data = dict()
                            data['name'] = "Top10引流关键词"
                            data['coming_from'] = str(need_date)
                            # data_keyword = dict()
                            data['shop_name'] = "六只兔子 高端内裤 内衣店"
                            data['keyword'] = need['keyword']
                            data['uv'] = need['uv']
                            data['itemid'] = rabbit['item_id']
                            # data_keyword_list.append(data_keyword)
                            # data['流量明细'] = data_keyword_list
                            local_set2.save(data)
                            # data = dict()
            '''
            if coming_url_deal:
                time.sleep(4)
                response = requests.get(url=coming_url_PC, headers=HEADERS, proxies=agentIp, verify=False,
                                        cookies=cookie_dict).text
                if "操作成功" in response:
                    need_datas = json.loads(response)['content']['data']
                    for need_date in need_datas:
                        for need in need_datas[str(need_date)]:
                            data = dict()
                            data['name'] = "Top10成交关键词"
                            data['coming_from'] = str(need_date)
                            # data_keyword = dict()
                            data['shop_name'] = "六只兔子 高端内裤 内衣店"
                            data['keyword'] = need['keyword']
                            data['value'] = need['value']
                            data['itemid'] = rabbit['item_id']
                            # data_keyword_list.append(data_keyword)
                            # data['流量明细'] = data_keyword_list
                            local_set2.save(data)
                            # data = dict()
                else:
                    time.sleep(30)
                    response = requests.get(url=coming_url_deal, headers=HEADERS, proxies=agentIp, verify=False,
                                            cookies=cookie_dict).text
                    need_datas = json.loads(response)['content']['data']
                    for need_date in need_datas:
                        for need in need_datas[str(need_date)]:
                            data = dict()
                            data['name'] = "Top10成交关键词"
                            data['coming_from'] = str(need_date)
                            # data_keyword = dict()
                            data['shop_name'] = "六只兔子 高端内裤 内衣店"
                            data['keyword'] = need['keyword']
                            data['value'] = need['value']
                            data['itemid'] = rabbit['item_id']
                        local_set2.save(data)
            '''
            if coming_url_wlSeList:
                time.sleep(4)
                response = requests.get(url=coming_url_PC, headers=HEADERS, proxies=agentIp, verify=False,
                                        cookies=cookie_dict).text
                if "操作成功" in response:
                    need_datas = json.loads(response)['content']['data']
                    for need_date in need_datas:
                        for need in need_datas[str(need_date)]:
                            data = dict()
                            data['name'] = "无线端来源"
                            data['coming_from'] = str(need_date)
                            # data_keyword = dict()
                            data['shop_name'] = "六只兔子 高端内裤 内衣店"
                            data['pageName'] = need['pageName']
                            data['uv'] = need['uv']
                            data['pv'] = need['pv']
                            data['uvRate'] = need['uvRate']
                            data['pvRate'] = need['pvRate']
                            data['itemid'] = rabbit['item_id']
                            local_set2.save(data)
                else:
                    time.sleep(30)
                    response = requests.get(url=coming_url_PC, headers=HEADERS, proxies=agentIp, verify=False,
                                            cookies=cookie_dict).text
                    need_datas = json.loads(response)['content']['data']
                    for need_date in need_datas:
                        for need in need_datas[str(need_date)]:
                            data = dict()
                            data['name'] = "Top10成交关键词"
                            data['coming_from'] = str(need_date)
                            data['shop_name'] = "六只兔子 高端内裤 内衣店"
                            data['pageName'] = need['pageName']
                            data['uv'] = need['uv']
                            data['pv'] = need['pv']
                            data['uvRate'] = need['uvRate']
                            data['pvRate'] = need['pvRate']
                            data['itemid'] = rabbit['item_id']
                            local_set2.save(data)
            '''
            '''
            if coming_url_wlSeList:
                time.sleep(4)
                response = requests.get(url=coming_url_wlSeList, headers=HEADERS, proxies=agentIp, verify=False,
                                        cookies=cookie_dict).text
                if "操作成功" in response:
                    need_datas = json.loads(response)['content']['data']
                    for need_date in need_datas:
                        #for need in need_datas[str(need_date)]:
                        data = dict()
                        data['name'] = "无线端来源"
                        # data['coming_from'] = str(need_date)
                        # data_keyword = dict()
                        data['shop_name'] = "六只兔子 高端内裤 内衣店"
                        data['pageName'] = need_date['pageName']
                        data['uv'] = need_date['uv']
                        data['pv'] = need_date['pv']
                        data['uvRate'] = need_date['uvRate']
                        data['pvRate'] = need_date['pvRate']
                        data['itemid'] = rabbit['item_id']
                        local_set2.save(data)
                else:
                    time.sleep(30)
                    response = requests.get(url=coming_url_wlSeList, headers=HEADERS, proxies=agentIp, verify=False,
                                            cookies=cookie_dict).text
                    need_datas = json.loads(response)['content']['data']
                    for need_date in need_datas:
                        # for need in need_datas[str(need_date)]:
                        data = dict()
                        data['name'] = "无线端来源"
                        # data['coming_from'] = str(need_date)
                        data['shop_name'] = "六只兔子 高端内裤 内衣店"
                        data['pageName'] = need_date['pageName']
                        data['uv'] = need_date['uv']
                        data['pv'] = need_date['pv']
                        data['uvRate'] = need_date['uvRate']
                        data['pvRate'] = need_date['pvRate']
                        data['itemid'] = rabbit['item_id']
                        local_set2.save(data)
            '''
        except Exception,e:
            print e




if __name__ == '__main__':
    # get_all_json()
    get_detail()