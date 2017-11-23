# -*- coding: utf-8 -*-
import requests
import json
import random
import logging
import re


class Utils:
    # 获取代理ip
    # @staticmethod
    # def GetAgentIp(mark=False):
        # url = "http://yunying.da-mai.com/?r=api/default/GetAgentIp"
        # res = json.loads(requests.get(url).content)
        #
        # if res['flag'] and 'ERROR' not in ','.join(res['ip']) and type(res['ip']) == list:
        #     proxy_ip = random.choice(res['ip'])
        # else:
        #     print(res['ip'])
        #     proxy_ip = None

        # if mark:
        #     proxy_ip = random.choice("211.149.189.148:16816", "122.114.173.129:16816")
        # else:
        #     proxy_ip = random.choice(
        #             ("211.149.189.148:16816", "122.114.173.129:16816", "101.234.76.118:16816", "123.206.197.28:16816",
        #              "120.24.171.107:16816", "121.42.177.10:16816", "120.24.171.107:16816", "123.207.150.34:16816",
        #              "115.159.147.178:16816",
        #              "123.206.121.190:16816")
        #     )
        # if not len(re.compile("[\d]*.[\d]*.[\d]*.[\d]*").findall(str(proxy_ip))):
        #     proxy_ip = None
        # return proxy_ip

    # @staticmethod
    # def GetMyAgent():
    #     url = "http://108.61.181.155:8432/?count=10"
    #     try:
    #         res = json.loads(requests.get(url).content)
    #         data = random.choice(res)
    #         ip = "%s:%s" % (data[0], data[1])
    #         return ip
    #     except Exception, e:
    #         logging.error(e.message)
    #         return None
    @staticmethod
    def GetMyAgent():
        url = "http://dps.kuaidaili.com/api/getdps/?orderid=960267305819890&num=50&ut=1&sep=2"
        # f = open('E:\ip.html')
        # content = f.read()
        ips = ["115.226.150.31:20343",
               "221.212.66.254:17679",
               "121.234.224.82:22818",
               "180.119.76.14:29115",
               "171.13.36.102:26516",
               "123.55.95.57:27554",
               "27.40.153.73:16515",
               "171.12.234.1:28787",
               "113.121.242.129:18080",
               "118.190.146.42:15524",
               "27.11.7.198:20475",
               "115.205.9.76:29851",
               "106.14.210.102:28216",
               "60.167.134.212:16506",
               "221.203.1.101:21282",
               "118.190.208.146:15524",
               "115.203.180.252:15312",
               "14.112.76.137:29645",
               "39.108.228.69:20189",
               "125.105.48.171:24814",
               "115.202.236.74:16136",
               "101.200.50.220:27041",
               "182.244.143.168:16510",
               "183.167.92.206:23004",
               "180.111.227.109:29171",
               "182.255.47.108:16653"]
        try:
            res = requests.get(url).content.split("\n")
            # res =content.split("\n")
            ip= random.choice(res)
            return ip
        except Exception, e:
            logging.error(e.message)
            return None

