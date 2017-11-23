# -*- coding: utf-8 -*-

# 用于抓取指定宝贝的规格属性


from lxml import etree
from utils.utils import Utils
from utils.JsDriver import PhantomDriver
from utils.html_downloader import Html_Downloader
import multiprocessing
# from pyvirtualdisplay import Display
import time
from time import sleep
import random
import demjson  # 解析js特有的不带引号的json
import re
import json


def startItemCrawl(keyword):
    crawl = CrawlItem(keyword)
    crawl.run()


class CrawlItem(object):
    def __init__(self, nid):
        self.nid = nid

    def run(self):
        items = "546733763111,530562796654,548179705841,43552599643,549542948551,551158235011,549071593227,550967373036,544506608226,552210965788,552161872818,549807528121,539033363694,552932235106,550405053950,553898239319,552907035560,546222114517,537517153693,553174567864,550062035350,547200942604,551972228533,551972356233,553854799602,552906555730,550517737468".split(
                ',')
        # while len(items) > 0:
        for i in range(1, 3):
            sleep(5)
            nid = random.choice(items)
            p = multiprocessing.Process(target=self.crawl, args=(nid,))
            p.start()
            CrawlItem.crawl(nid)

    @staticmethod
    def crawl(driver, nid):

        driver.get("https://item.taobao.com/item.htm?id=" + nid)
        source = driver.page_source
        # ok, resutl = Html_Downloader.Download_Html("https://item.taobao.com/item.htm?id=" + nid, {},
        #                                            {'ip': agentIp}, False)
        # source = resutl.text
        html = etree.HTML(source)
        item = {}
        if 'tb-prop' in source:
            item['item_id'] = nid
            item['category_id'] = re.compile("item%5f(.*?)(?=&)").findall(source)[0]
            for prop in html.xpath("//dl[contains(@class,'tb-prop')]"):
                prop_name = prop.xpath(".//dt/text()")[0].encode('utf-8')
                prop_value = []
                for value in prop.xpath(".//dd/ul/li"):
                    sub_value = []
                    sku_id = value.get('data-value')
                    sub_value.append(sku_id)
                    if value.xpath('./a')[0].get('style') and re.compile("/([^/]*)(?=_!!)").findall(
                            value.xpath('./a')[0].get('style')):
                        sku_img_id = re.compile("/([^/]*)(?=_!!)").findall(value.xpath('./a')[0].get('style'))[
                            0]
                        sub_value.append(sku_img_id)
                    if value.xpath('./a/span/text()'):
                        sku_name = value.xpath('./a/span/text()')[0].encode('utf-8')
                        sub_value.append(sku_name)
                    prop_value.append(";".join(sub_value))
                item[prop_name] = "&&||".join(prop_value)
            if html.xpath("//meta[@name='microscope-data']"):
                for meta in html.xpath("//meta[@name='microscope-data']")[0].get('content').split(';'):
                    if 'shopid' in meta.lower():
                        item['shop_id'] = meta.split("=")[1]
            item['crawl_time'] = int(time.time())

            # 要用chrome浏览器渲染,被检测几率较大暂不考虑
            # match_salecount = html.xpath("//li/div/div[@class='tb-sell-counter']/a/@title")
            # if False and len(match_salecount) > 0:
            #     salecount = str(match_salecount[0].encode('utf-8')).replace("30天内已售出", "")[
            #                 :str(match_salecount[0].encode('utf-8')).replace("30天内已售出", "").rindex("件，其")]
            # else:
            #     print("页面无法渲染尝试json获取")
            #     matchs = html.xpath("//script[contains(.,'Hub.config.set')]")
            #     if len(matchs) > 0:
            #         match_urls = re.compile("Hub.config.set\('sku'\,(.*?)(?=\);)").findall(
            #                 matchs[0].text.replace("\n\n", "\n").replace("\n", "").replace(" ", ""))
            #         if len(match_urls) > 0:
            #             info_urls = demjson.decode(match_urls[0])
            #             url = ("https:%s" % info_urls['wholeSibUrl']).replace("&amp;", "&")
            #             headers = {'Referer': 'https://item.taobao.com/item.htm?id=' + nid, 'ip': agentIp,
            #                        'cookies': driver.get_cookies()}
            #             ok, data = Html_Downloader.Download_Html(url, {}, headers)
            #             if ok and "soldQuantity" in data.text:
            #                 salecount = json.loads(data.text)['data']['soldQuantity']['confirmGoodsCount']
            return item
        else:
            return None


if __name__ == "__main__":
    startItemCrawl("552451981497")
