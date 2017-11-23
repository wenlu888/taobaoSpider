# -*- coding: utf-8 -*-

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import os
from config import PROJECT_PATH, SEPARATOR


class ChromeDriver(object):
    def __init__(self, proxy=None):
        # self.url = "https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&sub=true&from=subway&enup=false&full_redirect=false&tpl_redirect_url=https://sycm.taobao.com"
        self.url = "https://login.taobao.com/"
        dcap = dict(DesiredCapabilities.CHROME)

        # 进入浏览器设置
        options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2  # 不显示图片
            }
        }
        if proxy:
            options.add_argument(('--proxy-server=http://' + proxy))
        options.add_experimental_option('prefs', prefs)
        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')
        # 更换头部
        # options.add_argument('user-agent=' + self.user_agent)
        options.add_argument('incognito')

        self.driver = webdriver.Chrome(
                executable_path=PROJECT_PATH + SEPARATOR + 'driver' + SEPARATOR + 'chromedriver.exe',
                desired_capabilities=dcap,
                chrome_options=options)

    # 等待如果检测到页面跳转了就返回,否则填充账户名密码
    def check(self, driver, account, pwd):
        if "login.jhtml" in driver.current_url:
            if not driver.execute_script("document.getElementById('TPL_username_1').value"):
                driver.execute_script("document.getElementById('TPL_username_1').value='%s'" % account)
            if not self.driver.execute_script("document.getElementById('TPL_password_1').value"):
                driver.execute_script("document.getElementById('TPL_password_1').value='%s'" % pwd)
        return "sycm.taobao.com/portal/home.htm" in driver.current_url

    # 等待登陆完成并获取cookie
    def login_an_get(self, account, pwd):
        self.driver.get(self.url)
        try:
            result = WebDriverWait(self.driver, 60).until(lambda dr: self.check(self.driver, account, pwd))
        except:
            print("Time out error %s  %s" % (self.driver.current_url, self.driver.title))
        return self.driver.get_cookies(), ';'.join("%s=%s" % (i['name'], i['value']) for i in self.driver.get_cookies())

    def load_url(self, url):
        self.driver.get(url)

    def quite(self):
        self.driver.quit()

    def get_driver(self):
        return self.driver

    def set_cookie(self, cookies):
        for item in cookies.split(';'):
            if len(item.split('=')):
                result = self.driver.add_cookie(
                        {'name': item.split('=')[0], 'value': item.split('=')[1]})

    def wait_if_finish(self, url, timeout, method):
        self.driver.get(self.url)
        try:
            result = WebDriverWait(self.driver, timeout).until(method)
        except:
            print("Time out error %s  %s" % (self.driver.current_url, self.driver.title))
            return False
        return True
