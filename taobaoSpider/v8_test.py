# -*- coding: utf-8 -*-
import PyV8
from requests import Session
import re
import time
from time import sleep
import json
import utils.utils
from utils.html_downloader import Html_Downloader
from config import PROJECT_PATH, SEPARATOR

def execute_javascript(txt):
    js_path = "%s%s%s" % (PROJECT_PATH, SEPARATOR, "taobao_sign_js")
    file = open(js_path, 'r')
    js = file.read()
    ctxt = PyV8.JSContext()
    ctxt.enter()
    func = ctxt.eval(js)
    result_txt = func(txt)
    return result_txt
def get_shop_item_list(session, proxy_ip, page_num):
    proxies = {"http": proxy_ip, "https": proxy_ip}
    parms_pager = "{{\"shopId\":\"{shop_id}\",\"currentPage\":{page_num},\"pageSize\":\"30\",\"sort\":\"hotsell\",\"q\":\"\"}}"
    parms_url = "https://api.m.taobao.com/h5/com.taobao.search.api.getshopitemlist/2.0/?appKey=12574478&t={stmp}&sign={sign}&api=com.taobao.search.api.getShopItemList&v=2.0&type=jsonp&dataType=jsonp&callback=mtopjsonp12&data={pager}"
    params_referer = "https://shop{shop_id}.m.taobao.com/?shop_id={shop_id}&sort=d".format(shop_id=shop_id)
    # print(params_referer)
    stmp = "%s739" % (long(time.time()))
    referer = params_referer.format(shop_id=shop_id)
    pager = parms_pager.format(shop_id=shop_id, page_num=page_num)
    if session.cookies.get_dict('.taobao.com') and session.cookies.get_dict('.taobao.com').has_key('_m_h5_tk'):
        h5_tk = session.cookies.get_dict('.taobao.com')['_m_h5_tk']
        token = re.compile('(.*)(?=_)').findall(h5_tk)[0]
        value = '%s&%s&12574478&%s' % (token, stmp, pager)
        sign = execute_javascript(value)
    else:
        sign = "a013c868718eddb116eac3da0aa7974a"
    url = parms_url.format(pager=pager, stmp=stmp, sign=sign)
    # print(url)
    requests_parms = {}
    headers = {'Referer': referer,
               'Host': 'api.m.taobao.com',
               'Cache-Control': 'no-cache',
               'Pragma': 'no-cache',
               'User-Agent': Html_Downloader.GetUserAgent()}
    if proxy_ip:
        requests_parms['proxies'] = proxies
        requests_parms['verify'] = False
    result = session.get(url, headers=headers, **requests_parms)
    if result.ok:
        return result.content
    else:
        return None


shop_id = "64469556"  # 店铺id必填
proxy_ip = utils.utils.Utils.GetAgentIp()  # 不能用代理ip
session = Session()
get_shop_item_list(session, None, 1)  # 首次获取会失败只为获取cookie
total_page = 1
for i in range(100):
    # 到最后一页就提前终止
    if total_page and i >= total_page:
        break
    result = get_shop_item_list(session, None, (i + 1))
    if not result:
        result = get_shop_item_list(session, None, (i + 1))
    jobj = json.loads(result.replace("mtopjsonp12(", "").replace("})", "}"))  # 获取解析的json
    if jobj and "SUCCESS" in jobj['ret'][0]:
        total = int(jobj['data']['totalResults'])
        total_page = total / 30  # 每页最多30个不能再多
        if total % 30:
            total_page += 1
        print(result)
    else:
        print("获取数据失败")
        break
    sleep(2)