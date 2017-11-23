# -*- coding: utf-8 -*-
import requests
import time
from fake_useragent import UserAgent
from utils.utils import Utils
from datetime import datetime
import logging
import json
import Queue
import copy
from itertools import combinations, groupby
from pymongo import MongoClient

today = str(datetime.today()).split(' ')[0]
default_encoding = 'utf-8'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='E:\wenlu\Log\{name}.log'.format(name=today + " crwalDMP_level2"),
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
}
COOKIE = "UM_distinctid=15e7a46caf311b-0188d989dac01e-5c153d17-144000-15e7a46caf4552; thw=cn; " \
         "ali_apache_id=11.131.226.119.1505353641652.239211.1; miid=2033888855982094870; " \
         "l=AllZcEkSLTy0io2vJcWc-ksY6U4zk02Y; _cc_=WqG3DMC9EA%3D%3D; tg=0; cna=dNU/EvGIRjsCAQ4XY4PdDkHN; " \
         "hng=CN%7Czh-CN%7CCNY%7C156; linezing_session=qKhw9v9MNbMaPdxWJOwzyaJi_1510389248783ExqV_1; x=124660357; " \
         "uc3=sg2=AVMH%2FcTVYAeWJwo98UZ6Ld9wxpMCVcQb0e1XXZrd%2BhE%3D&nk2=&id2=&lg2=; " \
         "uss=WqVc8b%2FD1lylGiw0Mk3jz8Ln6ra1uQpmnmD%2FKUDIaPt9G72f%2FD%2B6vInw; tracknick=; " \
         "sn=%E4%BE%9D%E4%BF%8A%E6%9C%8D%E9%A5%B0%3A%E8%BF%90%E8%90%A5; skt=8d21e8aef771edef; v=0; " \
         "cookie2=61e122e137a1f9035a0fa694e8dc3160; unb=2077259956; t=1630b104e4d32df897451d6c96642469; " \
         "_m_h5_tk=ebee2ef9a0feee8271013f28324bb8cd_1510533964063; _m_h5_tk_enc=c5eed5fdd3b3c9b927f3b7c75cb51425; " \
         "uc1=cookie14=UoTde9Nd5U4%2BlQ%3D%3D&lng=zh_CN; _tb_token_=3b137a6feed6d; " \
         "isg=Ajs7zvr-5Us5xtpP_GqmVNzmyh9lOERBpVfdPS35GzpzjFlutWGN4kAO0Bo5 "
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in COOKIE.split(';')}
TAG_DATA = dict()
SHARE_Q = Queue.Queue()
conn = MongoClient('127.0.0.1', 27017)
local_set = conn.admin.MSWR


def get_csrfId():
    url = "http://dmp.taobao.com/api/login/loginuserinfo"
    proxy = dict()
    proxy['HTTP'] = Utils.GetMyAgent()
    response = requests.get(url=url, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict).text
    csrfid = json.loads(response)['data']['csrfId']
    return str(csrfid)


# 先获取所有标签中的数据：包括tag_id,tag_name，optionGroupId
def get_tag_details(tags, csrfid):
    global TAG_DATA
    if type(tags) != list:
        tags = [tags]
    for tag in tags:
        url = "http://dmp.taobao.com/api/tag/{tag_id}?csrfId={csrfid}&t={time}977" \
            .format(tag_id=tag, csrfid=csrfid, time=int(time.time()))
        proxy = dict()
        proxy['HTTP'] = Utils.GetMyAgent()
        # allow_redirects 是用来解决URI重定向问题
        response = requests.get(url=url, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict,
                                allow_redirects=False).text
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
        tag_data['group_id_type'] = group_id_type
        for group in option_groups:
            group_type = group['type']
            group_id_type[group_type] = group['id']
        TAG_DATA[tag] = tag_data


# 对所有标签的options进行排序
def get_options_list(cross_tags):
    # 应该返回一个队列，这个队列里面的每个数据是一个列表里面为tagid和optionId构成的字典
    # options_list = list()
    # 先处理主标签，将主标签封装好后，再对每个子标签构成的列表中append进去即可,主标签好像不用处理了。。。
    # 处理子标签 获取tagid和对应的optionid封装成字典即可
    '''
    for cross_tag in cross_tags:
        # 这里应该对单标签进行处理
        cross_tags.remove(cross_tag)
        for other_tag in cross_tags:
            cross_tag_options = TAG_DATA[cross_tag]['options']
            # for tag in other_tag:
            #    tag_options = TAG_DATA[tag]['options']
            other_tag_options = TAG_DATA[other_tag]['options']
            for tag_option in other_tag_options:
                tag_option_dict = dict()
                tag_option_dict[other_tag] = tag_option['id']
                for cross_tag_option in cross_tag_options:
                    tag_option_dict[cross_tag] = cross_tag_option['id']
                    # options_list.append(tag_option_dict)
                    SHARE_Q.put(str(tag_option_dict))
    '''

    # 这里要改，传入参数就应该为数组
    if type(cross_tags) != list:
        cross_tags = [cross_tags]
    # 第二种排序算法：判断列表中是否还有tag去迭代
    for cross_tag in cross_tags:
        # 选取第一个交叉标签并获得所有其options进行遍历，最后删除遍历过的cross_tag
        cross_tags.remove(cross_tag)
        # 对选取到的tag的options进行遍历本别加到数组中
        # 尝试使用递归的办法来解决标签不断增加的问题：

        def get_all_tags_options():
            options_list = list()
            tag_options = TAG_DATA[cross_tag]['options']
            for tag_option in tag_options:
                tags_dic_single = dict()
                # 组成标签id和对应optionId组成的字典
                tags_dic_single[cross_tag] = tag_option['id']
                options_list.append(tags_dic_single)
                # 如果还存在标签则进行循环遍历操作
                while len(cross_tags) != 0:
                    for other_tag in cross_tags:
                        other_tag_options = TAG_DATA[other_tag]['options']
                        for other_tag_option in other_tag_options:
                            other_tag_dict = dict()
                            new_options_list = list()
                            # 这里是关键，要实现对列表中字典的拼接，不用直接指定父类的字典
                            for option_list in copy.deepcopy(options_list):
                                other_tag_dict[other_tag] = other_tag_option['id']
                                option_list.update(other_tag_dict)
                                new_options_list.append(option_list)
                                # other_tag_dict[cross_tag] = tag_option['id']
                            options_list += new_options_list
        get_all_tags_options()

    return options_list


# 发送请求，并序列化
def get_coverage(options_list, csrfid):
    proxy = dict()
    proxy['HTTP'] = Utils.GetMyAgent()
    url_data = "http://dmp.taobao.com/api/analysis/coverage"
    for option in options_list:
        num = 2
        post_data = dict()
        post_data['csrfId'] = csrfid
        post_data['user'] = 1
        # 开始组合post数据，先组成主标签即店铺标签
        post_data["options[{a}].operatorType".format(a=0)] = 1
        post_data["options[{a}].optionGroupId".format(a=0)] = 304
        post_data["options[{a}].source".format(a=0)] = "all"
        post_data["options[{a}].tagId".format(a=0)] = 110063
        post_data["options[{a}].value".format(a=0)] = 145841584  # 填shopId
        post_data["options[{a}].optionNameMapStr".format(a=0)] = '{"145841584":"麦斯威尔旗舰店"}'  # 填店铺信息
        post_data["options[{a}].operatorType".format(a=1)] = 1
        post_data["options[{a}].optionGroupId".format(a=1)] = 111
        post_data["options[{a}].source".format(a=1)] = "all"
        post_data["options[{a}].tagId".format(a=1)] = 110063
        post_data["options[{a}].value".format(a=1)] = "1~999999999"
        DATA = dict()
        DATA['tag_id'] = str()
        DATA['tag_name'] = str()
        DATA['option_name'] = str()
        key_list = option.keys()
        for key in key_list:
            # 每个key代表一个tagId
            option_id = option[key]
            options = TAG_DATA[key]['options']
            DATA['tag_name'] += TAG_DATA[key]['tag_name'] + '_'
            DATA['tag_id'] += str(key) + '_'
            for get_right_option in options:
                if option_id == get_right_option['id']:
                    optionGroupId = get_right_option['optionGroupId']
                    optionValue = get_right_option['optionValue']
                    optionName = get_right_option['optionName']
                    post_data['options[{num}].operatorType'.format(num=num)] = 1
                    post_data['options[{num}].optionGroupId'.format(num=num)] = optionGroupId
                    post_data['options[{num}].source'.format(num=num)] = 'all'
                    post_data['options[{num}].tagId'.format(num=num)] = key
                    post_data['options[{num}].value'.format(num=num)] = optionValue
                    optionNameMapStr = dict()
                    optionNameMapStr[optionValue] = str(optionName)
                    post_data['options[{num}].optionNameMapStr'.format(num=num)] = str(optionNameMapStr)
                    DATA['option_name'] += get_right_option['optionName'] + '_'
                    num += 1
        response = requests.post(url_data, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict,
                                 allow_redirects=False, data=post_data).text
        DATA['tag_name'] += "制定店铺用户_"
        DATA['tag_id'] += '110063_'
        DATA['option_name'] += '1~9999999_麦斯威尔旗舰店_'
        DATA['count'] = str(json.loads(response)['data']['coverage'])
        DATA['crawl_time'] = int(time.time())
        DATA['tag_name'] = str(DATA['tag_name'])[:-1]
        DATA['tag_id'] = str(DATA['tag_id'])[:-1]
        DATA['option_name'] = str(DATA['option_name'])[:-1]
        print DATA
        local_set.save(DATA)
        # return DATA


if __name__ == '__main__':
    csrfid = get_csrfId()
    main_tag = 110063
    cross_tag = [123]
    total_tag = [[114554,113736],113741,113671,114555,113448,113861,113410,113713,22212,123,114604]
    cross_tag.append(main_tag)
    for tag in total_tag:
        get_tag_details(tag, csrfid)
        options_list = get_options_list(tag)
        get_coverage(options_list, csrfid)
