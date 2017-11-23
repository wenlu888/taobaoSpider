# -*- coding: utf-8 -*-
import requests
import time
from fake_useragent import UserAgent
from utils.utils import Utils
from datetime import datetime
import logging
import sys
import json
from itertools import combinations
import codecs
from pymongo import MongoClient
conn = MongoClient('127.0.0.1',27017)
db = conn.admin
my_set = db.DMP
today = str(datetime.today()).split(' ')[0]
default_encoding = 'utf-8'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='E:\wenlu\Log\{name}.log'.format(name=today+" crwalDMP"),
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
ua = UserAgent()
HEADER = {
    'User-Agent': ua.random,
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': "http://dmp.taobao.com/index.html",
    'Host': 'dmp.taobao.com',
    # 'Proxy-Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    #'X-Requested-With': 'XMLHttpRequest',
}
COOKIE = "UM_distinctid=15e7a46caf311b-0188d989dac01e-5c153d17-144000-15e7a46caf4552; thw=cn; ali_apache_id=11.131.226.119.1505353641652.239211.1; miid=2033888855982094870; l=AllZcEkSLTy0io2vJcWc-ksY6U4zk02Y; _cc_=WqG3DMC9EA%3D%3D; tg=0; cna=dNU/EvGIRjsCAQ4XY4PdDkHN; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; x=124660357; uc3=sg2=AVMH%2FcTVYAeWJwo98UZ6Ld9wxpMCVcQb0e1XXZrd%2BhE%3D&nk2=&id2=&lg2=; uss=VAXSokZb41x3LrOdSf%2FkOXi5mZhwOKGqxWNIJ%2BcsBdECv1yvzxoYTiml; tracknick=; sn=%E4%BE%9D%E4%BF%8A%E6%9C%8D%E9%A5%B0%3A%E8%BF%90%E8%90%A5; skt=44507678af07ca73; v=0; cookie2=113bd831048eba21f8cb9e18be45b345; unb=2077259956; t=1630b104e4d32df897451d6c96642469; _m_h5_tk=c1a78bd1ba3dd2c9ecca52c33fc9fbc1_1509929493370; _m_h5_tk_enc=62b4374f3e7e6c423b065fb9281bd9f8; uc1=cookie14=UoTcBrFj64SWvw%3D%3D&lng=zh_CN; _tb_token_=36f53e7b339f5; isg=AkNDruUzHaoINdJnhBIu7JQ-0gctENzv_b_VVXUmZaIRNH9We4m3S81i2PKB"
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in COOKIE.split(';')}
DATA = dict()
TATAL_DATA = list()

def get_csrfId():
    url = "http://dmp.taobao.com/api/login/loginuserinfo"
    proxy = dict()
    proxy['HTTP'] = Utils.GetMyAgent()
    response = requests.get(url=url, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict).text
    csrfid = json.loads(response)['data']['csrfId']
    return csrfid


def get_data(tag_id):
    csrfid = str(get_csrfId())
    tag_data = dict()
    url = "http://dmp.taobao.com/api/tag/{tag_id}?csrfId={csrfid}&t={time}977" \
        .format(tag_id=tag_id, csrfid=csrfid, time=int(time.time()))
    proxy = dict()
    proxy['HTTP'] = Utils.GetMyAgent()
    # allow_redirects 是用来解决URI重定向问题
    response = requests.get(url=url, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict, allow_redirects=False).text
    data = json.loads(response)
    # 标签信息
    tag_data['dmp_msg'] = str(data["data"]["tag"]["tagDesc"].split(",")[0])[9:-1]
    # 获取标签数
    tag_data['qualityScore'] = str(data["data"]["tag"]["qualityScore"])
    # 标签标题
    tag_data['tag_name'] =  str(data["data"]["tag"]["tagName"])
    # 标签
    options = dict()
    optionValue = data["data"]["tag"]["options"]
    GroupId = data["data"]["tag"]["options"][0]['optionGroupId']
    optionValue_id = dict()
    global DATA
    # 先把选项编号和选型名称以字典的形式保存在数组中
    options = list()
    for value in optionValue:
        options_list = list()
        options_list.append(value["optionValue"])
        options_list.append(value["optionName"])
        options.append(options_list)
        # 将每个选项的id和选项标签数组成字典后续用
        optionValue_id[value['optionValue']] = value['id']
    # 对选项进行组合全部发出请求获取数据
    for combin in range(1,len(options)+1):
        for option in combinations(options,combin):
            optionNameMapStr = dict()
            keys_list = list()
            for key in option:
                tag_key = key[0]
                keys_list.append(tag_key)
                optionNameMapStr[str(tag_key)] = key[1]
            url_data = "http://dmp.taobao.com/api/analysis/coverage"
            post_data = {
                "csrfId":csrfid,
                "user":1,
                "options[0].operatorType":1,
                "options[0].optionGroupId":GroupId,
                "options[0].source":"detail",
                "options[0].tagId":tag_id,
                "options[0].value":keys_list,
                "options[0].optionNameMapStr":optionNameMapStr,
            }
            post_data2 = {
                'options[0].tagId': 110063,
                'options[0].optionGroupId': 111,
                'options[2].optionNameMapStr': "{2: '本科生'}",
                'options[2].value': [2],
                'options[1].source': 'all',
                'options[2].source': 'all',
                'options[0].value': '1~999999999',
                'options[1].optionNameMapStr': "{'36236493': '依俊服饰",
                'options[1].value': 36236493,
                'options[0].source': 'all',
                'options[1].optionGroupId': 304,
                'options[1].tagId': 110063,
                'csrfId': '3aed9369a6af50b4d2b202',
                'user': 1,
                'options[2].optionGroupId': 12164,
                'options[0].operatorType': 1,
                'options[2].operatorType': 1,
                'options[1].operatorType': 1,
                'options[2].tagId': 113736}
            post_data3 ={
                         'options[3].optionGroupId': 12164,
                         'options[0].value': '1~999999999',
                         'options[2].optionNameMapStr': "{7: '小学'}",
                         'options[3].optionNameMapStr': "{6: u'初中'}",
                         'options[0].tagId': 110063,
                         'options[4].source': 'all',
                         'options[2].value': [7],
                         'csrfId': '3aed9369a6af50b4d2b202',
                         'options[4].optionNameMapStr': "{2:'本科生'}",
                         'options[4].value': [2],
                         'options[3].operatorType': 1,
                         'options[1].tagId': 110063,
                         'options[3].tagId': 113736,
                         'options[0].operatorType': 1,
                         'options[1].operatorType': 1,
                         'options[4].operatorType': 1,
                         'options[2].operatorType': 1,
                         'options[1].optionGroupId': 304,
                         'options[2].source': 'all',
                         'options[1].value': 36236493,
                         'options[4].tagId': 113736,
                         'user': 1,
                         'options[2].optionGroupId': 12164,
                         'options[3].source': 'all',
                         'options[1].source': 'all',
                         'options[0].optionGroupId': 111,
                         'options[0].source': 'all',
                         'options[4].optionGroupId': 12164,
                         'options[1].optionNameMapStr': "{'36236493': '\\xe4\\xbe\\x9d\\xe4\\xbf\\x8a\\xe6\\x9c\\x8d\\xe9\\xa5\\xb0'}",
                         'options[2].tagId': 113736,
                         'options[3].value': [6]}
            response = requests.post(url_data,proxies=proxy,verify=False,headers=HEADER,cookies=cookie_dict,allow_redirects=False,data=post_data).text
            DATA['count'] = str(json.loads(response)['data']['coverage'])
            # 标签说明。。。。
            DATA['option_name'] = str(tag_data['dmp_msg'])
            # 标签名称
            DATA['option_name'] = str(tag_data['tag_name'])
            # 选项名称：
            count_name = str()
            for name in optionNameMapStr.values():
                count_name = count_name+name+"_"
            DATA['count_name'] = count_name[:-1]
            print "爬取{count_name}成功".format(count_name=count_name[:-1])
            # 标签id :
            a = str()
            for key in keys_list:
                a = a+"_"+str(optionValue_id[key])
            DATA['id'] = str(tag_id)+a
            DATA['crawl_time'] = int(time.time())
            # 将数据存在本地mongdb查看结果
            my_set.save(DATA)
            # json_data = json.dumps(DATA, ensure_ascii=False)
            # logging.info(json_data)
            TATAL_DATA.append(DATA)
            DATA = {}
            # tag_data['options'] = options
    #############开始重新发请求获取数据###################

    '''
    这里先对标签排序选择后的算法，事实证明反而过于复杂，弃用留档
    for combin in range(1,len(tags)+1):
        # 这里先对每个子标签进行组合
        for need_tags in list(combinations(tags,combin)):

            # 对每个组合都添加主标签
            # need_tags_list = list()
            # for need_tag in need_tags:
            #     need_tags_list.append(need_tag)
            # need_tags_list.append(main_tag)

            combin_tags = list()
            # 这里对标签进行处理，如果遇到新标签在这里进行增加处理
            for tag in list(need_tags):
                # 这里吧所有标签组合都列出来，然后取到标签对应的信息放入局部变量即可
                # 这里要把对应标签的options提取出来组成集合好去发送请求
                if tag in TAG_DATA.keys() and "CHECKBOX" in TAG_DATA[tag]['group_id_type']:
                    # 我需要把子选项封装成数组，但是这个数组是由字典构成的，因为我需要获取每个子选项的GroupId、tag_id、value
                    # tag_checkbox = dict()
                    tag_checkbox = list()
                    tag_dict = dict()
                    # tag_checkbox['CHECKBOX'] = tag_dict
                    tag_dict['GroupId'] = TAG_DATA[tag]['group_id_type']['CHECKBOX']
                    tag_dict['tagId'] = tag
                    for value in TAG_DATA[tag]['options']:
                        tag_dict['optionValue'] = value['optionValue']
                        tag_dict['optionName'] = value['optionName']
                        combin_tags.append(tag_dict)
                if tag in TAG_DATA.keys() and "SHOP" in TAG_DATA[tag]['group_id_type']:
                    tag_dict = dict()
                    tag_shop_list = list()
                    tag_dict['SHOP'] = tag_shop_list
                    # tag_dict['tagId'] = tag
                    # 这里写的有问题，应该对type进行遍历
                    for tag_type in TAG_DATA[tag]['group_id_type']:
                        if "SHOP" == tag_type:
                            shop_dict = dict()
                            shop_dict['GroupId'] = TAG_DATA[tag]['group_id_type']['SHOP']
                            shop_dict['shop_id'] = shop_id
                            shop_dict['shop_name'] = shop_name
                            tag_shop_list.append(shop_dict)
                        if "INPUT" == tag_type:
                            input_dict = dict()
                            input_dict['GroupId'] = TAG_DATA[tag]['group_id_type']['INPUT']
                            input_dict['value'] = "1~999999999"
                            tag_shop_list.append(input_dict)
                    combin_tags.append(tag_dict)
            # 这里写的有问题，如果将主标签和副标签加到一起再进行选择会造成大量的数据冗余，应该将主副标签分别进行排序后再合并
            combins = list()
            for combin_check in range(1,len(combin_tags)+1) :
                for need_check in list(combinations(combin_tags,combin_check)):
                    combins.append(need_check)
            return combins
        '''




if __name__ == '__main__':
    starttime = datetime.now()
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    get_data(114555)
    endtime = datetime.now()
    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    runningTime = (endtime - starttime).seconds
    print "共计爬取时间：{runtime}".format(runtime=runningTime)






























