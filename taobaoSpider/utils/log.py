# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from itertools import combinations,permutations

list = list(combinations([1,2,3,4,5],2))

today = str(datetime.today()).split(' ')[0]
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='E:\wenlu\Log\{name}.log'.format(name=today+"name"),
                filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def get_date():
    today = str(datetime.today()).split(' ')[0]
    logging.info("测试log保存地点和命名规范")
    logging.getLogger('message')
   #  print getattr(logging,'')


import logging
import time

rq = time.strftime('%Y%m%d',time.localtime(time.time()))
setting = {
           'logpath':'/xxx/xxx/logs/',
           'filename':'xxx_' + rq + '.log'
           }

class Log(object):
    ''' '''
    def __init__(self, name):
        self.path = setting['logpath']
        self.filename = setting['filename']
        self.name = ip
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.fh = logging.FileHandler(self.path + self.filename)
        self.fh.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s')
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def close(self):
        self.logger.removeHandler(self.fh)



if __name__ == '__main__':
    get_date()