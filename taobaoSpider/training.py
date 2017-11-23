# -*- coding: utf-8 -*-

#用于测试功能,无实际作用

import random
import requests
import urllib
import cookielib, urllib2
from Utils.HtmlDownloader import Html_Downloader
from Utils.Utils import Utils


def deleteIp(agentIp):
    url = "http://108.61.181.155:8432/delete?ip=%s&port=%s" % (agentIp.split(':')[0], agentIp.split(':')[1])
    result = requests.get(url)


if __name__ == "__main__":
    # items = "546733763111,530562796654,548179705841,43552599643,549542948551,551158235011,549071593227,550967373036,544506608226,552210965788,552161872818,549807528121,539033363694,552932235106,550405053950,553898239319,552907035560,546222114517,537517153693,553174567864,550062035350,547200942604,551972228533,551972356233,553854799602,552906555730,550517737468".split(
    #         ',')
    # while len(items) > 0:
    #     agentIp = Utils.GetMyAgent()
    #     while agentIp is None:
    #         agentIp = Utils.GetMyAgent()
    #     #agentIp = "127.0.0.1:8888"
    #     nid = random.choice(items)
    #     url = "https://item.taobao.com/item.htm?id=" + nid
    #     cj = cookielib.CookieJar()
    #     opener = urllib2.build_opener(
    #         urllib2.HTTPCookieProcessor(cj))
    #     urllib2.install_opener(opener)
    #     resp = urllib2.urlopen(url)
    #     page = opener.open(url).read()
    #     for index, cookie in enumerate(cj):
    #         print '[',index, ']',cookie
    #     # ok, result = Html_Downloader.Download_Html(url, {}, {'ip': agentIp, 'timeout': "10", 'connection': "close"})
    #     # if not ok:
    #     #     print("error:%s  delete%s" % (result, agentIp))
    #     #     deleteIp(agentIp)
    #     # else:
    #     #     print("---success:" + agentIp)
    #     print(page)
    cookie_str="_euacm_ac_l_uid_=857889334; 2077227951_euacm_ac_c_uid_=1722465766; 2077227951_euacm_ac_rs_uid_=1722465766; _euacm_ac_rs_sid_=104659280; _portal_version_=new; 857889334_euacm_ac_c_uid_=78550821; 857889334_euacm_ac_rs_uid_=78550821; t=f92667cecb7871bc5b8f37557e14aa36; cna=0pTkEaPp+RsCAQ4XY4M9/5F4; l=Atvb7Anfj9E9wRIei2B-FEQRKzBH8O-y; isg=AuHh3NZPHNz8CbCoo33rFXKi-K37jlWAZpl_k0O22-hHqgF8i95lUA_gWObT; uc3=sg2=AVAJ%2F%2FuFgrZrwbvpPwMpeUNJWGnNVTEcpZhNLKPoZwE%3D&nk2=&id2=&lg2=; uss=AibnArdKXOYSGwijaWuJf8ZdgKo91PC9YbwzW6mScqrb8sAPUjB8wfus; tracknick=; _cc_=W5iHLLyFfA%3D%3D; tg=0; cookie2=14b8d0263b796e42bf3ad9e778cd0580; _tb_token_=e7935e33bbe3; x=78550821; uc1=cookie14=UoTcDzD9VaGPUg%3D%3D&lng=zh_CN; sn=%E8%8B%B1%E8%AF%AD%E4%BA%8C%E6%B2%B9%E6%9D%A1%3A%E6%8E%A8%E5%B9%BF; unb=857889334; skt=741a0815554f10d8; v=0"
    cookie_dict = {item.split('=')[0]: item.split('=')[1] for item in cookie_str.split(';')}
    ok, result = Html_Downloader.Download_Html("https://sycm.taobao.com/adm/execute/preview.json?app=op&date=2017-07-10,2017-07-16&dateId=1006960&dateType=static&desc=&filter=[6,7]&id=null&itemId=null&name=&owner=user&show=[{%22id%22:1007104},{%22id%22:1006964},{%22id%22:1016013},{%22id%22:1007108},{%22id%22:1007563},{%22id%22:1006969},{%22id%22:1007562},{%22id%22:1014477},{%22id%22:1006971},{%22id%22:1006978},{%22id%22:1007113},{%22id%22:1007122},{%22id%22:1007117},{%22id%22:1007126},{%22id%22:1016040},{%22id%22:1016031},{%22id%22:1011647}]", {}, {'ip': '115.159.147.178:16816',"cookies": cookie_dict,'Referer':'https://sycm.taobao.com/adm/index.htm'}, False)
    print(ok)
