# -*- coding: utf-8 -*-
# 用于抓取指定店铺所有宝贝及宝贝规格属性
#间隔时间小于一天拿item_id判重,间隔时间大于一天直接入库
from config import PROJECT_PATH, SEPARATOR
from lxml import etree
from utils.utils import Utils
from utils.html_downloader import Html_Downloader
import json

fq=open("d:\\1.txt",'r')
json_str=fq.read()
fq.close()
post_data={'data':json_str}
url='http://192.168.12.91:8080/pdd/competeShopRearController/saveCompeteShopInfo'
ok,result=Html_Downloader.Download_Html(url, post_data, {'timeout':60}, post=True)
print result


