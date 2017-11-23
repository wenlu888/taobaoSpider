# -*- coding: utf-8 -*-

#用于抓取指定关键词top100宝贝的id和销量(付款人数)


from lxml import etree
from Utils.utils import Utils
from Utils.html_downloader import Html_Downloader
import sys
import re
import json
from datetime import datetime
import time


def startNidCrawl(keyword):
    crawl = CrawlNid(keyword)
    crawl.run()


class CrawlNid(object):
    def __init__(self, keyword):
        self.key_word = keyword
    def run(self):
        str = 'CrawlNid----->>>>>>>>beginning'
        sys.stdout.write(str + "\r\n")
        sys.stdout.flush()
        agentip = Utils.GetAgentIp()
        search_url = "https://s.taobao.com/search?q={q}&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_{day}&ie=utf8&bcoffset=1&ntoffset=1&p4ppushleft=1%2C48&s={s}&sort=sale-desc"
        day = datetime.now().strftime("%Y%m%d")
        total = 8
        for i in range(1, total):
            t_url = search_url.format(q=self.key_word, day=day, s=i)
            header = {'ip': agentip}
            try:
                ok, response = Html_Downloader.Download_Html(t_url, {}, header)
                if ok:
                    html = etree.HTML(response.text)
                    matchs = html.xpath("//script[contains(.,'g_page_config')]")
                    if len(matchs) > 0:
                        data = re.compile("g_page_config=(.*)?;g_srp_loadCss").match(
                                matchs[0].text.replace("\n\n", "\n").replace("\n", "").replace(" ", ""))
                        if data.lastindex > 0:
                            data = json.loads(data.group(1).encode('utf-8'))
                            if data.has_key('mods'):
                                self.crawlNid(data)
                                totalpage = data['mods']['pager']['data']['totalPage']
                                total = totalpage if totalpage < total else total
                        else:
                            print("无法匹配有效的json")
                    else:
                        print("无法匹配到宝贝列表")
            except Exception, e:
                print("关键词{p}第{i}页抓取错误{m}".format(p=self.key_word, i=i, m=e.message))

    def crawlNid(self, data):
        items = data['mods']['itemlist']['data']['auctions']
        nid_str = ""
        for item in items:
            if not item['shopcard']['isTmall']:
                nid_str += item['nid'] + ','
        print(nid_str)


if __name__ == "__main__":
    startNidCrawl("连衣裙")
    pass
