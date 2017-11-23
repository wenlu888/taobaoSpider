# -*- coding: utf-8 -*-

# 需要安装selenium库
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import ProxyType
from html_downloader import Html_Downloader
from selenium import webdriver
import os
import sys
import re

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


class PhantomDriver(object):
    def __init__(self, type, proxy_ip, time_out):
        self.time_out = time_out
        self.user_agent = Html_Downloader.GetUserAgent()
        # self.user_agent = "Mozilla/5.0 (Linux; U; Android 6.0.1; zh-cn; OPPO R9s Plus Build/MMB29M) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/1.0.0.100 U3/0.8.0 Mobile Safari/534.30 AliApp(TB/6.7.6) WindVane/8.0.0 1080X1920 GCanvas/1.4.2.21"
        app_path = os.path.dirname(__file__) + "\\driver"

        if type == 1:  # phantomJS,需要指定phantomJS.exe
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = self.user_agent
            dcap["phantomjs.page.settings.resourceTimeout"] = self.time_out * 1000
            dcap["phantomjs.page.settings.loadImages"] = False  # 不加载图片
            dcap["phantomjs.page.settings.disk-cache"] = False  # 不启用缓存
            if proxy_ip is not None:
                proxy = webdriver.Proxy()
                proxy.proxy_type = ProxyType.MANUAL
                proxy.http_proxy = proxy_ip
                # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
                proxy.add_to_capabilities(dcap)
            self.driver = webdriver.PhantomJS(executable_path='c:\\driver\\phantomjs.exe',
                                              desired_capabilities=dcap)
        elif type == 2:  # chrome,需要安装chrome和指定chrome驱动  chromedriver
            dcap = dict(DesiredCapabilities.CHROME)

            # 进入浏览器设置
            options = webdriver.ChromeOptions()
            prefs = {
                'profile.default_content_setting_values': {
                    'images': 2  # 不显示图片
                }
            }
            options.add_experimental_option('prefs', prefs)
            # 设置中文
            options.add_argument('lang=zh_CN.UTF-8')
            # 更换头部
            options.add_argument('user-agent=' + self.user_agent)
            options.add_argument('incognito')
            options.add_argument('headless')
            if proxy_ip is not None:
                options.add_argument(('--proxy-server=http://' + proxy_ip))
            self.driver = webdriver.Chrome(executable_path='c:\\driver\\chromedriver.exe', desired_capabilities=dcap,
                                           chrome_options=options)
        elif type == 3:  # firefox,需要安装firefox和指定firefox驱动  geckodriver
            profile = webdriver.FirefoxProfile()
            cap = dict(webdriver.DesiredCapabilities.FIREFOX)
            if proxy_ip is not None:
                ip_ip = proxy_ip.split(":")[0]
                ip_port = int(proxy_ip.split(":")[1])
                profile.set_preference('network.proxy.type', 1)  # 默认值0，就是直接连接；1就是手工配置代理。
                profile.set_preference('network.proxy.http', ip_ip)
                profile.set_preference('network.proxy.http_port', ip_port)
                profile.set_preference('network.proxy.ssl', ip_ip)
                profile.set_preference('network.proxy.ssl_port', ip_port)
            cap['firefox.page.settings.userAgent'] = self.user_agent
            profile.set_preference('permissions.default.image', 2)  # 禁止加载图片某些firefox只需要这个
            profile.set_preference('browser.migration.version', 9001)  # 部分需要加上这个
            profile.set_preference('general.useragent.override', self.user_agent)  # 部分需要加上这个
            profile.update_preferences()
            self.driver = webdriver.Firefox(profile, executable_path='c:\\driver\\geckodriver', capabilities=cap)

    def Download(self, url):
        result = {'ok': False}
        try:
            self.driver.get(url)
            cookie_lst = self.driver.get_cookies()
            cookie_str = ""
            cookie_dict = {}
            for item in cookie_lst:
                cookie_str += item['name'] + "=" + item['value'] + ';'
                cookie_dict[item['name']] = item['value']
            result['cookie_lst'] = cookie_lst
            result['cookie_str'] = cookie_str
            result['cookie_dict'] = cookie_dict
            result['user_agent'] = self.user_agent
            result['page_source'] = self.driver.page_source
            result['ok'] = True
        except Exception, e:
            result['ok'] = False
            result['message'] = e.message
        self.driver.quit()
        return result

    def download_no_quit(self, url):
        result = {'ok': False}
        try:
            self.driver.get(url)
            cookie_lst = self.driver.get_cookies()
            cookie_str = ""
            cookie_dict = {}
            for item in cookie_lst:
                cookie_str += item['name'] + "=" + item['value'] + ';'
                cookie_dict[item['name']] = item['value']
            result['cookie_lst'] = cookie_lst
            result['cookie_str'] = cookie_str
            result['cookie_dict'] = cookie_dict
            result['user_agent'] = self.user_agent
            result['page_source'] = self.driver.page_source
            result['ok'] = True
        except Exception, e:
            result['ok'] = False
            result['message'] = e.message
        return result

    def return_driver(self):
        return self.driver
