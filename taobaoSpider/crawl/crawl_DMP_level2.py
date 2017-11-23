# -*- coding: utf-8 -*-
import requests
import time
from fake_useragent import UserAgent
from utils.utils import Utils
from datetime import datetime
import logging
import json
from itertools import combinations,groupby
from pymongo import MongoClient
today = str(datetime.today()).split(' ')[0]
default_encoding = 'utf-8'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='E:\wenlu\Log\{name}.log'.format(name=today+" crwalDMP_level2"),
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
# 链接mongdb数据库查询和增加
conn = MongoClient('127.0.0.1',27017)
# conn2 = MongoClient('192.168.10.198',27017)
local_set = conn.admin.NEW_DMP2
# 1024数据库查询
# search_set = conn.pdd.Copy_of_t_dmpopen_tag_detail
TAG_DATA = dict()
COOKIE = "UM_distinctid=15e7a46caf311b-0188d989dac01e-5c153d17-144000-15e7a46caf4552; thw=cn; ali_apache_id=11.131.226.119.1505353641652.239211.1; miid=2033888855982094870; l=AllZcEkSLTy0io2vJcWc-ksY6U4zk02Y; _cc_=WqG3DMC9EA%3D%3D; tg=0; cna=dNU/EvGIRjsCAQ4XY4PdDkHN; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; _tb_token_=558ae75b8ee76; x=124660357; uc3=sg2=AVMH%2FcTVYAeWJwo98UZ6Ld9wxpMCVcQb0e1XXZrd%2BhE%3D&nk2=&id2=&lg2=; uss=BxeNWNDuh5bWvG7cn7%2FxeZukmY3gkNrY7k0XsJpuil0t2SN%2BVbliBXWD; tracknick=; sn=%E4%BE%9D%E4%BF%8A%E6%9C%8D%E9%A5%B0%3A%E8%BF%90%E8%90%A5; skt=aad047a355dc4c23; v=0; cookie2=62f3e2c68bd8333fb75d4b24d6372dd4; unb=2077259956; t=1630b104e4d32df897451d6c96642469; _m_h5_tk=9d0eceafbbd4b42d04163d4a5ffc8230_1510189201269; _m_h5_tk_enc=3361e03831fd4cff7d0f1c7b2f54718a; uc1=cookie14=UoTde9fXMHSABQ%3D%3D&lng=zh_CN; isg=AmJi2a1bTL74glNYPSkf-y21s-gEG23Y9ESUiqz7w1WAfwL5lEO23eh_2Y14"
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in COOKIE.split(';')}
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
          }


def get_csrfId():
    url = "http://dmp.taobao.com/api/login/loginuserinfo"
    proxy = dict()
    proxy['HTTP'] = Utils.GetMyAgent()
    response = requests.get(url=url, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict).text
    csrfid = json.loads(response)['data']['csrfId']
    return str(csrfid)


# 先获取所有标签中的数据：包括tag_id,tag_name，optionGroupId
def get_tag_details(tags,csrfid):
    global TAG_DATA
    for tag in tags:
        url = "http://dmp.taobao.com/api/tag/{tag_id}?csrfId={csrfid}&t={time}977" \
        .format(tag_id=tag, csrfid=csrfid, time=int(time.time()))
        proxy = dict()
        proxy['HTTP'] = Utils.GetMyAgent()
        # allow_redirects 是用来解决URI重定向问题
        response = requests.get(url=url, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict, allow_redirects=False).text
        data = json.loads(response)
        tag_data = dict()
        tag_data['dmp_msg'] = str(data["data"]["tag"]["tagDesc"].split(",")[0])[9:-1]
        # 标签信息
        tag_data['dmp_msg'] = str(data["data"]["tag"]["tagDesc"].split(",")[0])[9:-1]
        # 获取标签数
        tag_data['qualityScore'] = str(data["data"]["tag"]["qualityScore"])
        # 标签标题
        tag_data['tag_name'] = str(data["data"]["tag"]["tagName"])
        # 获取选项信息
        tag_data['options'] = data["data"]["tag"]["options"]
        # 获取该标签的GroupId
        # tag_data['GroupIds'] = data["data"]["tag"]["optionGroups"]
        # 获取标签的type
        option_groups = data["data"]["tag"]["optionGroups"]
        group_id_type = dict()
        tag_data['group_id_type'] =group_id_type
        for group in option_groups:
            group_type = group['type']
            group_id_type[group_type] = group['id']
        TAG_DATA[tag] = tag_data


# 获取所有标签选项后，围绕主标签对标签进行重组，再对重组后的标签进行二次重组
def gettags_combin(main_tag,cross_tags):
    shop_id = 145841584
    shop_name = "麦斯威尔旗舰店"
    main_combins = maketags_combin(main_tag,shop_id,shop_name)
    cross_combins = maketags_combin(cross_tags,shop_id,shop_name)
    total_combins = list()
    for main_combin in main_combins:
        for cross_combin in cross_combins:
            total_combins.append(list(cross_combin)+(list(main_combin)))
    # 发送请求
    get_coverage(total_combins)


# 该方法用来对tags进行排序选择
def maketags_combin(tags, shop_id, shop_name):
    # 先对副标签的tags的选项等信息进行排序选择
    if type(tags) != list:
        tags = [tags]
    combin_tags = list()
    for tag in tags:
        # 这里吧所有标签组合都列出来，然后取到标签对应的信息放入局部变量即可
        # 这里要把对应标签的options提取出来组成集合好去发送请求
        if tag in TAG_DATA.keys() and "CHECKBOX" in TAG_DATA[tag]['group_id_type']:
            # 我需要把子选项封装成数组，但是这个数组是由字典构成的，因为我需要获取每个子选项的GroupId、tag_id、value
            # tag_checkbox = dict()
            # tag_checkbox = list()
            tag_dict_checkbox = dict()
            # tag_checkbox['CHECKBOX'] = tag_dict
            for value in TAG_DATA[tag]['options']:
                tag_dict_checkbox['GroupId'] = TAG_DATA[tag]['group_id_type']['CHECKBOX']
                tag_dict_checkbox['tagId'] = tag
                tag_dict_checkbox['optionValue'] = value['optionValue']
                tag_dict_checkbox['optionName'] = value['optionName']
                combin_tags.append(tag_dict_checkbox)
                tag_dict_checkbox = dict()
        if tag in TAG_DATA.keys() and "SHOP" in TAG_DATA[tag]['group_id_type']:
            tag_dict = dict()
            tag_shop_list = list()
            tag_dict['SHOP'] = tag_shop_list
            tag_dict['tagId'] = tag
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


# 定义请求，对标签数进行请求数据遍历
def get_coverage(total_combins):
    csrfid = get_csrfId()
    for combine in total_combins:
        DATA = dict()
        # tag的tagName 通过tagid获得并存储
        DATA['tag_name'] = str()
        # option内容的标签，通过optionName直接获得
        DATA['option_name'] = str()
        # tagid集合标签
        DATA['tagids'] = str()
        proxy = dict()
        proxy['HTTP'] = Utils.GetMyAgent()
        url_data = "http://dmp.taobao.com/api/analysis/coverage"
        # 要对post数据进行循环重组好发送数据
        post_data = dict()
        post_data['csrfId'] = csrfid
        post_data['user'] = 1
        # 这里的i 最好也为字典
        # @@这里有个很大的问题就是当这个标签有需要输入的信息时就需要单独添加标签@@
        same_group_list = list()
        same_group_dict = dict()
        for same_group in combine:
            if 'SHOP' not in str(same_group):
                if same_group['GroupId'] not in same_group_dict.keys():
                    some_group_list2 = list()
                    some_group_list2.append(same_group)
                    same_group_dict[same_group['GroupId']] = some_group_list2
                elif same_group['GroupId'] in same_group_dict.keys():
                    same_group_dict[same_group['GroupId']].append(same_group)
            if 'SHOP' in str(same_group):
                same_group_list.append(same_group)
        same_group_list.append(same_group_dict)
        # num_post = len(same_group_list)
        # if "SHOP" in str(combine):num_post += 1
        # same_group_list = list(set(same_group_list))
        num_post = 0
        for single_combine in same_group_list:
            # 开始对单个请求信息进行解析，目标为字典
            if 'SHOP' in single_combine:
                shop_list = single_combine['SHOP']
                tagId =  single_combine['tagId']
                DATA['tagids'] += str(tagId)+"_"
                for shop in shop_list:
                    if 'shop_id' in str(shop):
                        post_data["options{a}.operatorType".format(a=[num_post])] = 1
                        post_data["options{a}.optionGroupId".format(a=[num_post])] = shop['GroupId']
                        post_data["options{a}.source".format(a=[num_post])] = "all"
                        post_data["options{a}.tagId".format(a=[num_post])] = tagId
                        post_data["options{a}.value".format(a=[num_post])] = shop['shop_id']
                        post_data["options{a}.optionNameMapStr".format(a=[num_post])] = str({str(shop['shop_id']):shop['shop_name']})
                        num_post += 1
                        # DATA['tag_name'].append(shop['shop_name']+"_")
                        DATA['option_name']+=str(shop['shop_name'])+"_"
                    else:
                        post_data["options{a}.operatorType".format(a=[num_post])] = 1
                        post_data["options{a}.optionGroupId".format(a=[num_post])] = shop['GroupId']
                        post_data["options{a}.source".format(a=[num_post])] = "all"
                        post_data["options{a}.tagId".format(a=[num_post])] = tagId
                        # post_data["options{a}.value".format(a=[num_post])] = shop['shop_id']
                        # 这里input的value写死了，因为产品要求输入为1
                        post_data["options{a}.value".format(a=[num_post])] = "1~999999999"
                        num_post += 1
                        DATA['tag_name']+="最近180天店内购买频次"+"_"
                        DATA['option_name']+="1~999999999_"
            else:
                # @@@@@@这里要注意啊！要按照groupid进行分组操作，现在没有。。。。。。所以数据有误
                for key in single_combine.keys():
                    # key = single_combine.keys()[keys]
                    optionNameMapStr = dict()
                    value =list()
                    for same_groop_tag in single_combine[key]:
                        optionValue = int(same_groop_tag['optionValue'])
                        optionNameMapStr[str(optionValue)] = same_groop_tag['optionName']
                        tagId = same_groop_tag['tagId']
                        option_name_forDATA =list()
                        option_name_forDATA.append(str(same_groop_tag['optionName']))
                        value.append(optionValue)
                        for data in option_name_forDATA:
                            DATA['option_name'] += data+"_"
                    DATA['tagids'] += str(tagId)+"_"
                    post_data["options{a}.operatorType".format(a=[num_post])] = 1
                    post_data["options{a}.optionGroupId".format(a=[num_post])] = key
                    post_data["options{a}.source".format(a=[num_post])] = "all"
                    post_data["options{a}.tagId".format(a=[num_post])] = tagId
                    post_data["options{a}.value".format(a=[num_post])] = value
                    post_data["options{a}.optionNameMapStr".format(a=[num_post])] = str(optionNameMapStr)
                    DATA['tag_name'] += str(TAG_DATA[tagId]['tag_name'])+"_"
                    num_post += 1
        logging.info(post_data)
        try:
            response = requests.post(url_data,proxies=proxy,verify=False,headers=HEADER,cookies=cookie_dict,allow_redirects=False,data=post_data).text
            DATA['count'] = str(json.loads(response)['data']['coverage'])
        except Exception,e:
            logging.error("解析得到响应数据时发生错误{e}".format(e=e))
            response = requests.post(url_data, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict,allow_redirects=False, data=post_data).text
        DATA['tag_name'] = str( DATA['tag_name'])[:-1]
        DATA['option_name'] = str(DATA['option_name'])[:-1]
        DATA['tagids'] = str(DATA['tagids'])[:-1]
        DATA['crawl_time'] = int(time.time())
        local_set.save(DATA)
        print response


if __name__ == '__main__':
    # 最近180天店内购买频次
    main_tag = 110063
    # 教育程度和物流导向
    # tags = [113736, 130519]   22212
    tags = [123]
    #cross_tags = [113736, 130519]
    csrfid = get_csrfId()
    total_tags=tags
    total_tags.append(main_tag)
    get_tag_details(total_tags,csrfid)
    # shop_id = 36236493
    # shop_name = "依俊服饰"
    cross_tags = [123]
    gettags_combin(main_tag,cross_tags)