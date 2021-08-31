#!/usr/bin/env python 
# -*- coding: utf-8 -*-
#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |// '.
#                 / \\|||  :  |||// \
#                / _||||| -:- |||||- \
#               |   | \\\  -  /// |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.' >' "".
#         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#         \  \ `_.   \_ __\ /__ _/   .-` /  /
#     =====`-.____`.___ \_____/___.-`___.-'=====
#                       `=---='
#
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#               佛祖保佑         永无BUG
# @Time    : 2021-08-24 20:29
# @Author  : Hongbo Huang
# @File    : SimpleRecList.py
from dao import redis_db
from dao.mongo_db import MongoDB
from bson import ObjectId


class SimpleRecList(object):
    def __init__(self):
        self._redis = redis_db.Redis()
        self._mongo = MongoDB(db='recommendation')
        self._collection = self._mongo.db_client['content_labels']

    def get_news_order_by_time(self):
        count = 10000
        data = self._collection.find().sort([{"news_date", -1}])
        for news in data:
            self._redis.redis.zadd("rec_list_by_time", {str(news['_id']): count})
            count -= 1


if __name__ == '__main__':
    simple = SimpleRecList()
    simple.get_news_order_by_time()