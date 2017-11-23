# -*- coding: utf-8 -*-
# ---------------------------
# 脚本效果：爬取淘宝全店宝贝数据
# 欠缺：效果稳定性目前一般，需要进一步测试和改进，日志系统进一步优化，异常捕获等
# 注意：记得启动本地redis数据库
# ---------------------------
import requests
import json
from redis import Redis
import random
from utils.utils import Utils
from datetime import datetime
from lxml import etree
from utils.html_downloader import Html_Downloader
import time
import Queue
import logging
from time import sleep
from config import SAVE__INSERT_API
from config import SAVE__INSERT_API_ZS
# from fake_useragent import UserAgent

'''
操作mongdb数据库，弃用
from pymongo import MongoClient
client = MongoClient('192.168.10.198', 27017)
db = client.pdd
collection = db.CompeteShop
'''
today = str(datetime.today()).split(' ')[0]
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='E:\wenlu\Log\{name}.log'.format(name=today + " crwalTaobaoShop"),
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
DATA = []
# 试验阶段用redis去重
r = Redis(host='127.0.0.1', port=6379, db=3)
# ua = UserAgent()
HEADERS = {
    # 'User-Agent': ua.random,
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Referer': "https://detail.taobao.com/item.htm?id=546615137384",
    'Upgrade-Insecure-Requests': '1'
}
COUNT = 0
TIME = long(time.time())
# TIME = random.randint(1509238800,1509242400)


# 获取全店宝贝数据，通过推荐方式获取
def get_data(shop_id, item_ids, total_items, shopname):
    url = "https://tui.taobao.com/recommend?seller_id=78550821&shop_id={shop_id}&item_ids={item_id}&floorId=42296&" \
          "pSize=500&callback=detail_pine&appid=2144&count=200&pNum=0".format(shop_id=shop_id, item_id=item_ids)
    agentIp = dict()
    agentIp['HTTPS'] = Utils.GetMyAgent()
    try:
        response = requests.get(url, headers=HEADERS, verify=False, proxies=agentIp)
        if response.status_code == 200 and "result" in response.text:
            total_json = response.text.replace("\r", "").replace("\n", "").replace("detail_pine(", "").replace("});",
                                                                                                               "}")
            total_json = json.loads(total_json)
            need_json = total_json["result"]
            for need in need_json:
                getNeedJson = dict()
                getNeedJson['month_Sales'] = str(need['monthSellCount'])
                getNeedJson['title'] = need['itemName']
                getNeedJson['item_id'] = str(need['itemId']).strip()
                getNeedJson['totalSoldQuantity'] = str(need['sellCount'])
                getNeedJson['quantity'] = str(need['quantity'])
                # 不要价格getNeedJson['promotionPrice'] = need['promotionPrice']
                getNeedJson['category_id'] = str(need['categoryId'])
                getNeedJson['picUrl'] = "https:" + need['pic']
                getNeedJson['crawl_url'] = "https:" + need['url']
                getNeedJson['crawl_time'] = TIME
                getNeedJson['shop_id'] = str(shop_id)
                getNeedJson['shop_name'] = shopname
                # 完成数据写入redis
                r.set(need['itemId'], getNeedJson)
                # SHARE_Q.put(getNeedJson)
                '''
                数组针对item_id去重，但效率太低弃用
                if len(DATA) == 0:
                    DATA.append(getNeedJson)
                else:
                    m = list()
                    for data in DATA:
                        m.append(data['itemId'])
                    if getNeedJson['itemId'] not in m:
                        DATA.append(getNeedJson)
                    else:
                        continue
                #DATA = list(set(DATA))
                '''
                print "添加商品成功{item_id}".format(item_id=need['itemId'])
    except Exception, e:
        logging.error("爬取{shopname}是出错：{e}".format(shopname=shopname, e=e.message))
        return get_data(shop_id, item_ids, total_items, shopname)
    # 想通过mongdb查询得到已经有的宝贝数量
    # database = collection.dout({'shop_id':shop_id,'crawl_time':{'$gt':int(time)}})
    # list(del_repeat(DATA))
    try:
        size = int(r.dbsize())
        # 每次存储DATA时获取随机itemId的方法
        # ranNum = random.randint(0,size-1)
        # re_itemId = r.get([ranNum])['itemId']
        re_itemId = r.randomkey()
        # size = len(DATA)
        global COUNT
        print COUNT
        if size == int(total_items):
            logging.info("爬取数量和预期相同，数量为：{size}".format(size=size))
            COUNT = 0
        elif size != int(total_items):
            COUNT += 1
            # 当爬取次数大于100且已经爬取的数量和需求总数差2个的时候
            if COUNT > 100 and size > int(total_items) - 3:
                logging.info("爬取数量和目标数量差额在2个，爬取到的数量为：{size}".format(size=size))
                COUNT = 0
                return size
            # 请求200次时间为2分钟左右
            elif COUNT >= 200:
                logging.info("爬取次数超过300次，爬取到的数量为：{size}".format(size=size))
                COUNT = 0
                return size
            # 如果已经爬取的数量和需求总数差20以内，就要继续爬
            elif size < int(total_items) - 20:
                get_data(shop_id, re_itemId, total_items, shopname)
            # 当爬取数量大约200之后就停止爬取
            else:
                get_data(shop_id, re_itemId, total_items, shopname)
    except Exception,e:
        logging.error("数据处理或循环控制时出现异常：{e}".format(e=e.message))
        return get_data(shop_id, item_ids, total_items, shopname)


# 数据序列化
def serialization():
    # 先从redis中将数据取出,并存入DATA中
    keys = r.keys()
    for key in keys:
        data = '{' + r.get(key)[1:-1].strip() + '}'
        data2 = eval(data)
        DATA.append(data2)
    post_data = {'data': json.dumps(DATA)}
    if not process_request(SAVE__INSERT_API, post_data):
        process_request(SAVE__INSERT_API, post_data)
        sleep(3)
    # if not process_request(SAVE__INSERT_API_ZS, post_data):
    #     sleep(3)
    #     process_request(SAVE__INSERT_API_ZS, post_data)
    r.flushdb()


def process_request(url, data):
    result_ok = False
    ok, result = Html_Downloader.Download_Html(url, data, {'timeout': 10}, post=True)
    if ok:
        result_json = json.loads(result.content)
        result_ok = bool(result_json['flag'])
        logging.info("数据存储成功{result_ok}".format(result_ok=result_ok))
    return result_ok


# 获得全店宝贝个数
def get_total_items(time_now, shop_url):
    ip = Utils.GetMyAgent()
    proxies = {
        "http": "http://{ip}".format(ip=ip),
        "https": "http://{ip}".format(ip=ip)
    }
    # shop_url = "https://shop67361531.taobao.com/"
    parms_url = "{shop_url}i/asynSearch.htm?_ksTS={now}569_240&callback=jsonp&mid=w-14766145001-0&wid=14766145001&path=/search.htm&search=y&orderType=hotsell_desc&scene=taobao_shop&pageNo={page_num}"
    url_test = parms_url.format(shop_url=shop_url, now=time_now, page_num=1)
    cookie2 = "UM_distinctid=15e7a46caf311b-0188d989dac01e-5c153d17-144000-15e7a46caf4552; thw=cn; ali_apache_id=11.131.226.119.1505353641652.239211.1; _uab_collina=150538207117146260512386; miid=2033888855982094870; l=AllZcEkSLTy0io2vJcWc-ksY6U4zk02Y; _cc_=WqG3DMC9EA%3D%3D; tg=0; _umdata=85957DF9A4B3B3E8F872A3094256432F0F1549AE1C92C6CCF1E68B982581686F23BFC13A60CCABD1CD43AD3E795C914CAF73DEDAA30E5DF4E27D6F4EB50F8E1F; cna=dNU/EvGIRjsCAQ4XY4PdDkHN; _tb_token_=36f53e7b339f5; _m_h5_tk=4570646d13ae7111fef3e2b7a043022c_1509837913393; _m_h5_tk_enc=20b6e25356a739887ddf33c092c83ece; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; x=124660357; uc3=sg2=AVMH%2FcTVYAeWJwo98UZ6Ld9wxpMCVcQb0e1XXZrd%2BhE%3D&nk2=&id2=&lg2=; uss=VAXSokZb41x3LrOdSf%2FkOXi5mZhwOKGqxWNIJ%2BcsBdECv1yvzxoYTiml; tracknick=; sn=%E4%BE%9D%E4%BF%8A%E6%9C%8D%E9%A5%B0%3A%E8%BF%90%E8%90%A5; skt=dfb70b3150f31cce; v=0; cookie2=113bd831048eba21f8cb9e18be45b345; unb=2077259956; t=1630b104e4d32df897451d6c96642469; uc1=cookie14=UoTcBrCpbGSbPg%3D%3D&lng=zh_CN; isg=AoWF8Nl9cPq6fVThFtgQUqaUlMF_6jLBbwXTU4fqQrzLHqWQT5JJpBP-XnQT"
    cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in cookie2.split(';')}
    try:
        response = requests.get(url=url_test, proxies=proxies, headers=HEADERS, verify=False, allow_redirects=False, cookies= cookie_dict)
        html = etree.HTML(response.text)
        if response.status_code == 200 and "search-result" in response.text:
            total_items = html.xpath("//div[contains(@class,'search-result')]/span/text()")[0]
            logging.info("获取店铺{shop_url},宝贝总数：{total_items}".format(total_items=total_items, shop_url=shop_url))
            return total_items
        else:
            return get_total_items(time_now, shop_url)
    except Exception, e:
        logging.error("爬取全店宝贝时{shop_url}时出错：{e}".format(shop_url=shop_url, e=e.message))
        return get_total_items(time_now, shop_url)


if __name__ == '__main__':
    begin = datetime.now()
    time_now = long(time.time())
    print "开始时间：{begin}".format(begin=begin)
    taobao_shops = [
        # {'shop_name': '莎琪儿私藏内衣店', 'shop_url': 'https://shop67361531.taobao.com/', 'shop_id': '67361531', 'item_ids': '544488976857'},
        # {'shop_name': '嘉爱丝', 'shop_url': 'https://shop108446669.taobao.com/', 'shop_id': '108446669', 'item_ids': '40881947920'},
        {'shop_name': '佰丝韵真丝 ', 'shop_url': 'https://shop107044311.taobao.com/', 'shop_id': '107044311', 'item_ids': '556840966632'},
        {'shop_name': '丝悦坊', 'shop_url': 'https://shop120839150.taobao.com/', 'shop_id': '120839150', 'item_ids': '549034046990'},
        {'shop_name': '六只兔子 高端内裤 内衣店', 'shop_url': 'https://shop36826868.taobao.com/', 'shop_id': '36826868', 'item_ids': '521044391372'},
        {'shop_name': '楼格格内衣馆', 'shop_url': 'https://shop69082681.taobao.com/', 'shop_id': '69082681', 'item_ids': '559021959024'},
        {'shop_name': '广州太易国际旅行社', 'shop_url': 'https://gztygjlxs.fliggy.com/', 'shop_id': '104592229', 'item_ids': '560187566759'},
        {'shop_name': '小步点童鞋', 'shop_url': 'https://xiaobudiantongxie.taobao.com/', 'shop_id': '70752327', 'item_ids': '552909629043'},
        {'shop_name': '蜜色之吻内衣馆', 'shop_url': 'https://bra360.taobao.com/', 'shop_id': '64469556', 'item_ids': '546615137384'},
        {'shop_name': '贞品坊 专注8年高端女装', 'shop_url': 'https://zpf1979.taobao.com/', 'shop_id': '58890609', 'item_ids': '543506763242'},
        {'shop_name': '蓝蓓真丝', 'shop_url': 'https://shop36236493.taobao.com/', 'shop_id': '36236493', 'item_ids': '558753743031'},
        {'shop_name': '邪恶先生帽子铺', 'shop_url': 'https://shop110467035.taobao.com/', 'shop_id': '110467035', 'item_ids': '536907024661'},
        {'shop_name': '韩都衣舍官方店铺', 'shop_url': 'https://hstyle.taobao.com/', 'shop_id': '106135951','item_ids': '557692179404'},
    ]
    for shop in taobao_shops:
        shop_name = shop['shop_name']
        shop_url = shop['shop_url']
        shop_id = shop['shop_id']
        item_id = shop['item_ids']
        logging.info("开始爬取{shop_name}".format(shop_name=shop_name))
        start_time2 = datetime.now()
        total_items = get_total_items(time_now, shop_url)
        get_data(shop_id, item_id, total_items, shop_name)
        serialization()
        end_time2 = datetime.now()
        runningTime2 = (end_time2 - start_time2).seconds
        logging.info("爬取店铺{shop_name}结束，耗时：{runningTime}".format(shop_name=shop_name, runningTime=runningTime2))
    over = datetime.now()
    print "结束时间：{over}".format(over=over)
    long = over - begin
    print long
