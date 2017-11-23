# -*- coding: utf-8 -*-

#用于抓取订单中tradeID对应的宝贝ID

import json
from utils.driver_utils import ChromeDriver
from db.DataStore import *
from utils.utils import Utils
from lxml import etree
import time
import datetime
from time import sleep
import re
import random

agent_ip = Utils.GetAgentIp()
result = get_item_trade_ids()
cookies = "mt=ci%3D-1_0; thw=cn; _m_user_unitinfo_=unit|unsz; _m_unitapi_v_=1498717160426; _m_h5_tk=5497d68b5bcf376f3f03c2bfe29d5c3e_1499745724771; _m_h5_tk_enc=bd37ed1f8dad5844fa8737aa499399d3; mt=ci%3D-1_0; _tb_token_=e17e846a1e737; x=78550821; uc3=sg2=AVAJ%2F%2FuFgrZrwbvpPwMpeUNJWGnNVTEcpZhNLKPoZwE%3D&nk2=&id2=&lg2=; uss=WvmGFLDaRLuLKHzx3Jt6R6Zh8SbBg8epTAb4OU0jo4jMr30BF8ACG4yF; tracknick=; sn=%E8%8B%B1%E8%AF%AD%E4%BA%8C%E6%B2%B9%E6%9D%A1%3A%E6%8E%A8%E5%B9%BF; skt=753a73a2763c5d75; v=0; cookie2=3c92dea4c50d0cf31281f889a3a999ec; unb=857889334; t=efd1f635969594e9ad33c0ec391d9883; uc1=cookie14=UoW%2BsWPGhqNu%2Fw%3D%3D&lng=zh_CN; cna=0SPrEVg+OkQCAQ4XY4MHK7uX; isg=Avv7jk0BJmcLoRtlqwnHCbYyit-l-AMTeQ3uMe245_oRTBsudSCfohnMENr5; apush5dceacf8bcd04ef16398a2906680ab9b=%7B%22ts%22%3A1499853369995%2C%22parentId%22%3A1499850283869%7D"
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in cookies.split(';')}

driver = ChromeDriver()
cookies = driver.login_an_get('英语二油条:推广', 'tuiguang654321')
sleep(5)

for item in result:
    url = "https:%s" % item['item_url']
    mydriver = driver.get_driver()
    mydriver.get(url)
    source = mydriver.page_source
    match_lst = re.compile("\"itemId\":(.*?)(?=,)").findall(source.replace(" ", ""))
    if match_lst:
        print(match_lst[0])
        # ok, result = Html_Downloader.Download_Html(url, {}, {"cookies": cookie_dict, "ip": agent_ip}, post=False)
        # if ok:
        #     html = etree.HTML(result.text)
        #     match_lst = re.compile("\"itemId\":(.*?)(?=,)").findall(result.text.replace(" ", ""))
        #     if match_lst:
        #         print(match_lst[0])
    sleep(15)
