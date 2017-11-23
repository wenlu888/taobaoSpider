# -*- coding: utf-8 -*-
import os
import platform

SEPARATOR = '/'
if 'Windows' in platform.system():
    SEPARATOR = '\\'

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE__Crawler_Log="http://192.168.10.28:8080/pdd/CrawlerLogController/SaveCrawlerLog"
# SAVE_SALES_ORDER_INFO_API = "http://syjcapi.da-mai.com/salesInfoRearController/saveSalesOrderInfo"
SAVE_SALES_ORDER_INFO_API = "http://192.168.10.28:8080/pdd/salesInfoRearController/saveSalesOrderInfo"
# SAVE_SALES_ITEMS_INFO_API = "http://syjcapi.da-mai.com/salesInfoRearController/saveSalesItemsInfo"
SAVE_SALES_ITEMS_INFO_API = "http://192.168.10.28:8080/pdd/salesInfoRearController/saveSalesItemsInfo"
GET_SALES_ORDER_CNT_API = "http://192.168.10.28:8080/pdd/salesInfoRearController/getSalesOrderCount"
GET_SHOP_ID_API = "http://192.168.10.198:8080/pdd/recordInfoController/getKeywordRecordInfo?shop_id="
GET_SALES_TRADE_IDS_API = ""
GET_SALES_ORDER_CNT_API = "http://192.168.10.28:8080/pdd/salesInfoRearController/getSalesOrderCount"
GET_SHOP_ID_API = ""
GET_SALES_TRADE_IDS_API = ""
GET_SALES_ORDER_CNT_API = "http://syjcapi.da-mai.com/salesInfoRearController/getSalesOrderCount"
GET_SHOP_ID_API = "http://192.168.10.198:8080/pdd/recordInfoController/getKeywordRecordInfo?shop_id="
# GET_SHOP_ID_API = "192.168.10.28:8080/pdd/CrawlerLogController/getAllKw"
GET_ALLNick= "http:192.168.10.198:8080/pdd/CrawlerLogController/getAllNick"
GET_SALES_ORDER_IDS_API = ""
#SAVE__INSERT_API = "http://192.168.10.28:8080/pdd/competeShopRearController/saveCompeteShopInfo"
#SAVE_INSERT_KEYWORD_API="http://192.168.10.28:8080/pdd/keyWordItemController/saveKeyWordItem"
SAVE__INSERT_API = "http://192.168.10.28:8080/pdd/competeShopRearController/saveCompeteShopInfo"
SAVE_INSERT_KEYWORD_API="http://192.168.10.28:8080/pdd/keyWordItemController/saveKeyWordItem"
SAVE__INSERT_API_ZS= "http://syjcapi.da-mai.com/competeShopRearController/saveCompeteShopInfo"
SAVE_INSERT_KEYWORD_API_ZS="http://syjcapi.da-mai.com/keyWordItemController/saveKeyWordItem"
SAVE__INSERT_API="http://192.168.10.198:8080/pdd/competeShopRearController/saveCompeteShopInfo"
SAVE_INSERT_KEYWORD_API="http://192.168.10.198:8080/pdd/keyWordItemController/saveKeyWordItem"
#crwal_item_details3
SAVE__INSERT_API = "http://192.168.10.198:8080/pdd/competeShopRearController/saveCompeteShopInfo"
#crawlnid1
SAVE_INSERT_KEYWORD_API="http://syjcapi.da-mai.com/keyWordItemController/saveKeyWordItem"

#获取所有店铺信息
SAVE_OPPONET = "192.168.10.28:8080/pdd/CrawlerLogController/getAllNick"

