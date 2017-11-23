# coding:utf-8

import random
import requests
import chardet
import requests.adapters
import urllib2
import cookielib
import ssl

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",

    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36 OPR/37.0.2178.32",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",

    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",

    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",

    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",

    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0)",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.3 Safari/537.36",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.9.2.1000 Chrome/39.0.2146.0 Safari/537.36",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.277.400 QQBrowser/9.4.7658.400",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 UBrowser/5.6.12150.8 Safari/537.36"
]


class Html_Downloader(object):
    @staticmethod
    def get_header():
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
        }

    @staticmethod
    def GetUserAgent():
        return random.choice(USER_AGENTS)

    @staticmethod
    def Download_Html(url, params, input_headers, post=False):
        try:
            headers = Html_Downloader.get_header()
            requests_params = {'timeout': 5, 'headers': headers}
            for k in input_headers:
                if k == "ip":
                    if input_headers[k]:
                        proxies = {"http": input_headers[k], "https": input_headers[k]}
                        requests_params['proxies'] = proxies
                        requests_params['verify'] = False
                elif k == "cookies":
                    requests_params['cookies'] = input_headers[k]
                elif k == "timeout":
                    requests_params['timeout'] = float(input_headers[k])
                else:
                    headers[k] = input_headers[k]
            requests_params['headers'] = headers
            requests.adapters.DEFAULT_RETRIES = 5
            if post:
                r = requests.post(url=url, data=params, **requests_params)
            else:
                r = requests.get(url=url, params=params, **requests_params)
            r.encoding = chardet.detect(r.content)['encoding']
            requests.packages.urllib3.disable_warnings()
            if r.ok:
                return r.ok, r
            else:
                return r.ok, r.text
        except Exception, e:
            return False, e.message


