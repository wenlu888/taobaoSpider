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
# ua = UserAgent()
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
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
COOKIE = "UM_distinctid=15e7a46caf311b-0188d989dac01e-5c153d17-144000-15e7a46caf4552; thw=cn; ali_apache_id=11.131.226.119.1505353641652.239211.1; miid=2033888855982094870; l=AllZcEkSLTy0io2vJcWc-ksY6U4zk02Y; _cc_=WqG3DMC9EA%3D%3D; tg=0; cna=dNU/EvGIRjsCAQ4XY4PdDkHN; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; _tb_token_=3d73497b6b4b1; x=124660357; uc3=sg2=AVMH%2FcTVYAeWJwo98UZ6Ld9wxpMCVcQb0e1XXZrd%2BhE%3D&nk2=&id2=&lg2=; uss=VAmowkFljKPmUhfhc%2B1GBuXNJWn9cLMEX%2FtIkJ5j0tQgoNppvUlaKrn3; tracknick=; sn=%E4%BE%9D%E4%BF%8A%E6%9C%8D%E9%A5%B0%3A%E8%BF%90%E8%90%A5; skt=da75e42fd35a3180; v=0; cookie2=17f5415096176ca88c03d1fed693a1d4; unb=2077259956; t=1630b104e4d32df897451d6c96642469; _m_h5_tk=02fd605dba1a80ebc9444074cb377d69_1510882811789; _m_h5_tk_enc=004ba35aa81ab5d71be35fa0633a5784; ali_ab=14.23.99.131.1510570522194.8; uc1=cookie14=UoTde9570gt2uw%3D%3D&lng=zh_CN; isg=AldXem3BwaDDjEabePbCaOBS5sthNCDr6YNhCamEaiaN2HcasGy7ThXyTE69"
cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in COOKIE.split(';')}
TAG_DATA = dict()
SHARE_Q = Queue.Queue()
conn = MongoClient('192.168.10.198', 27017)
# local_set = conn.pdd.t_new_dmp_coverage
local_set = conn.pdd.sycm_items
local_set_gettags = conn.pdd.count_name_tags


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
            tag_data['group_id'] = group['id']
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
    options_list = list()
    '''
    for cross_tag in cross_tags:
        # 选取第一个交叉标签并获得所有其options进行遍历，最后删除遍历过的cross_tag
        cross_tags.remove(cross_tag)
        # 对选取到的tag的options进行遍历本别加到数组中
        # 尝试使用递归的办法来解决标签不断增加的问题：
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
                            # 需要对new_options_list做去重操作
                            # new_options_list = list(set(new_options_list))
                            # other_tag_dict[cross_tag] = tag_option['id']
                        options_list += new_options_list
    '''
    if [7] == cross_tags:
        for_input_dict = dict()
        for_input_dict[cross_tags[0]] = "123"
        options_list.append(for_input_dict)
        return options_list
    elif [8] == cross_tags:
        for_input_dict = dict()
        for_input_dict[cross_tags[0]] = "123"
        options_list.append(for_input_dict)
        return options_list
    else:
        for cross_tag in cross_tags:
            # cross_tags.remove(cross_tag)
            cross_tag_options = get_options(cross_tag)
            if len(options_list) == 0:
                options_list += cross_tag_options
            else:
                for option in copy.deepcopy(options_list):
                    for cross_tag_option in cross_tag_options:
                        new_option = copy.deepcopy(option)
                        new_option.update(cross_tag_option)
                        options_list.append(new_option)
                options_list += cross_tag_options
        need_options_list = list()
        for need_option in options_list:
            # if len(need_option.keys()) == 3:
            need_options_list.append(need_option)
        return need_options_list


def get_options(tag):
    tag_options = TAG_DATA[tag]['options']
    total_need_tag = list()
    for tag_option in tag_options:
        need_tag = dict()
        need_tag[tag] = tag_option['id']
        total_need_tag.append(need_tag)
    return total_need_tag


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
        # post_data["options[{a}].value".format(a=0)] = 36236493  # 填shopId
        # post_data["options[{a}].optionNameMapStr".format(a=0)] = '{"36236493":"依俊服饰"}'  # 填店铺信息
        post_data["options[{a}].optionNameMapStr".format(a=0)] = '{"145841584":"麦斯威尔旗舰店"}'  # 填店铺信息
        post_data["options[{a}].operatorType".format(a=1)] = 1
        post_data["options[{a}].optionGroupId".format(a=1)] = 111
        post_data["options[{a}].source".format(a=1)] = "all"
        post_data["options[{a}].tagId".format(a=1)] = 110063
        post_data["options[{a}].value".format(a=1)] = "1~999999999"
        key_list = option.keys()
        for key in key_list:
            # 每个key代表一个tagId
            option_id = option[key]
            options = TAG_DATA[key]['options']
            # DATA['tag_name'] += TAG_DATA[key]['tag_name'] + '_'
            for get_right_option in options:
                DATA = dict()
                DATA['id'] = str()
                # DATA['tag_name'] = str()
                DATA['option_value'] = str()
                DATA['option_group_id'] = str()
                DATA['option_name'] = "本店圈定人数"
                DATA['id'] += '110063_110063_'
                DATA['option_value'] += '145841584_1~9999999_'
                DATA['option_group_id'] += '304_111_'
                DATA['id'] += str(key) + '_'
                DATA['option_group_id'] += str(TAG_DATA[key]['group_id']) + '_'
                optionGroupId = get_right_option['optionGroupId']
                optionValue = get_right_option['optionValue']
                optionName = get_right_option['optionName']
                if option_id == get_right_option['id']:
                    post_data['options[{num}].operatorType'.format(num=num)] = 1
                    post_data['options[{num}].optionGroupId'.format(num=num)] = optionGroupId
                    post_data['options[{num}].source'.format(num=num)] = 'all'
                    post_data['options[{num}].tagId'.format(num=num)] = key
                    post_data['options[{num}].value'.format(num=num)] = optionValue
                    optionNameMapStr = dict()
                    optionNameMapStr[optionValue] = str(optionName)
                    DATA['count_name'] = get_right_option['optionName']
                    post_data['options[{num}].optionNameMapStr'.format(num=num)] = str(optionNameMapStr)
                    DATA['option_value'] += get_right_option['optionValue'] + '_'
                    # DATA['option_group_id'] += get_right_option
                    num += 1
                    time.sleep(2)
                    response = requests.post(url_data, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict,
                             allow_redirects=False, data=post_data).text
                    DATA['count'] = str(json.loads(response)['data']['coverage'])
                    DATA['crawl_time'] = int(time.time())
                    # DATA['tag_name'] = str(DATA['tag_name'])[:-1]
                    DATA['id'] = str(DATA['id'])[:-1]
                    DATA['option_group_id'] = str(DATA['option_group_id'])[:-1]
                    DATA['option_value'] = str(DATA['option_value'])[:-1]
                    print DATA
                    local_set.save(DATA)
            if key == 8:
                for value in ['0~4', '5~9', '10~20', '21~31', '32~42', '43~53', '53~99999']:
                    DATA = dict()
                    DATA['id'] = str()
                    # DATA['tag_name'] = str()
                    DATA['option_value'] = str()
                    DATA['option_group_id'] = str()
                    DATA['option_name'] = "本店圈定人数"
                    DATA['id'] += '110063_110063_'
                    DATA['option_value'] += '145841584_1~9999999_'
                    DATA['option_group_id'] += '304_111_'
                    DATA['id'] += str(key) + '_'
                    DATA['option_group_id'] += str(TAG_DATA[key]['group_id']) + '_'
                    post_data['options[{num}].operatorType'.format(num=num)] = 1
                    post_data['options[{num}].optionGroupId'.format(num=num)] = 8
                    post_data['options[{num}].source'.format(num=num)] = 'all'
                    post_data['options[{num}].tagId'.format(num=num)] = key
                    post_data['options[{num}].value'.format(num=num)] = value
                    DATA['count_name'] = value
                    DATA['option_value'] += value
                    response = requests.post(url_data, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict,
                                             allow_redirects=False, data=post_data).text
                    DATA['count'] = str(json.loads(response)['data']['coverage'])
                    DATA['crawl_time'] = int(time.time())
                    # DATA['option_group_id'] += "8"
                    # DATA['id'] += "8"
                    # DATA['tag_name'] = str(DATA['tag_name'])[:-1]
                    DATA['id'] = str(DATA['id'])[:-1]
                    DATA['option_group_id'] = str(DATA['option_group_id'])[:-1]
                    DATA['option_value'] = str(DATA['option_value'])
                    print DATA
                    local_set.save(DATA)
                    DATA['option_value'] = '145841584_1~9999999_'
                    DATA['option_group_id'] = '304_111_'
                    DATA['id'] = '110063_110063_'
                break
            if key == 7:
                for value in ['0~500', '500~1000', '1000~2000', '2000~3000', '3000~99999']:
                    DATA = dict()
                    DATA['id'] = str()
                    # DATA['tag_name'] = str()
                    DATA['option_value'] = str()
                    DATA['option_group_id'] = str()
                    DATA['option_name'] = "本店圈定人数"
                    DATA['id'] += '110063_110063_'
                    DATA['option_value'] += '145841584_1~9999999_'
                    DATA['option_group_id'] += '304_111_'
                    DATA['id'] += str(key) + '_'
                    DATA['option_group_id'] += str(TAG_DATA[key]['group_id']) + '_'
                    post_data['options[{num}].operatorType'.format(num=num)] = 1
                    post_data['options[{num}].optionGroupId'.format(num=num)] = key
                    post_data['options[{num}].source'.format(num=num)] = 'all'
                    post_data['options[{num}].tagId'.format(num=num)] = key
                    post_data['options[{num}].value'.format(num=num)] = value
                    DATA['count_name'] = value
                    DATA['option_value'] += value
                    response = requests.post(url_data, proxies=proxy, verify=False, headers=HEADER, cookies=cookie_dict,
                                             allow_redirects=False, data=post_data).text
                    DATA['count'] = str(json.loads(response)['data']['coverage'])
                    DATA['crawl_time'] = int(time.time())
                    # DATA['tag_name'] = str(DATA['tag_name'])[:-1]
                    DATA['option_group_id'] += "7"
                    DATA['id'] += "7"
                    DATA['id'] = str(DATA['id'])[:-2]
                    DATA['option_group_id'] = str(DATA['option_group_id'])[:-1]
                    DATA['option_value'] = str(DATA['option_value'])
                    print DATA
                    local_set.save(DATA)
                    DATA['option_value'] = '145841584_1~9999999_'
                    DATA['option_group_id'] = '304_111_'
                    DATA['id'] = '110063_110063_'
                break

        # return DATA


if __name__ == '__main__':
    csrfid = get_csrfId()
    main_tag = 110063
    cross_tag = [123]
    tag_dict = dict()
    # tag_names = local_set_gettags.find()
    for tag_name in [114554,7,8,113736,113741,113671,114555,113448,113861,113410,113713,22212,123,114604]:
        # name = tag_name['tag_name']
        # tags = tag_name['tags']
        get_tag_details(tag_name, csrfid)
        options_list = get_options_list(tag_name)
        get_coverage(options_list, csrfid)
    # total_tag = ["用户性别":[114554],"教育程度":[113736]]
    # cross_tag.append(main_tag)
    # for tag in total_tag:
    #     get_tag_details(tag, csrfid)
    #     options_list = get_options_list(tag)
    #     get_coverage(options_list, csrfid)
