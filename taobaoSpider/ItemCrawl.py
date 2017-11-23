# coding:utf-8

from gevent import monkey

monkey.patch_all()

from multiprocessing import Value, Queue, Process
from crawl.crawlNid import startNidCrawl

if __name__ == "__main__":
    q1 = Queue()
    q2 = Queue()
    p0 = Process(target=startNidCrawl, args=("连衣裙", q1))
    p0.start()
    p0.join()
