# -*- coding: utf-8 -*-
from pymongo import MongoClient
conn = MongoClient('192.168.10.198', 27017)
local_set = conn.pdd.SEJ_table
import requests
import PyV8
HEADS = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Host':'c6.shengejing.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
}

COOKIE = 'route=822c7baf1a5081e8fb756c0bf2729316; PHPSESSID=7pvh0o8mbi4uq5u2iaj5jk2qm7'
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in COOKIE.split(';')}

def load_data():
    # url = "http://c6.shengejing.com/index.php?year=2017&month=11&subcid=50011404&brand=&gcate=&cate=&cid=16&tab=3&func=3&subfunc=submarket&prop=&external=&startprice=&endprice=&custpriceinterval=10&priceview=default"
    # response = requests.get(url=url, cookies=cookie_dict, headers=HEADS, verify=False).text
    # ctxt = PyV8.JSContext()
    # js = "var myselect=document.getElementById('subcid');a = myselect.options[index].value;return a"
    # func = ctxt.eval(js)
    # result_txt = func(response)
    # print result_txt
    data = dict()
    data['option_name'] = '奶酪'
    data['option_value'] = 121416017
    data['have_sun'] = 1
    data['cid'] = 35
    data['cid_name'] = '奶粉/辅食/营养品/零食'
    local_set.save(data)
    print "成功"

def get_data():
    datas = local_set.find()
    cid = list()
    for data in datas:
        # cid.append(data['cid'])
     # totalcid=list(set(cid))
        print data
    #print totalcid

def get_tagid_7():
    a = ["0~4","5~9","10~20","21~31"]
    for aa in a :
        yield str(aa)

def use_tagid_7():
    a = get_tagid_7()
    b = get_tagid_7()
    c = get_tagid_7()
    s = get_tagid_7()
    print next(a)
    print next(b)
    print next(c)
    print next(s)


if __name__ == '__main__':
      load_data()
      #get_data()
    # load_data()
    # get_data()