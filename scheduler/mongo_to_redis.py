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
# @Time    : 2021-08-21 21:09
# @Author  : Hongbo Huang
# @File    : mongo_to_redis.py

from dao import redis_db
from dao.mongo_db import MongoDB
import pymongo


class Write_to_redis(object):
    def __init__(self):
        self._redis = redis_db.Redis()
        self.mongo = MongoDB(db='recommendation')
        self.collection = self.mongo.db_client['content_labels']

    def get_from_mongo(self):
        pipelines = [{
            '$group': {
                '_id': "$type"
            }
        }]

        types = self.collection.aggregate(pipelines)
        count = 0
        for type in types:
            cx = {"type": type['_id']}
            data = self.collection.find(cx)
            for info in data:
                result = dict()
                result_title = dict()
                result['content_id'] = str(info['_id'])
                result['describe'] = str(info['describe'])
                result['type'] = str(info['type'])
                result['title'] = str(info['title'])
                result['news_date'] = str(info['news_date'])
                result['likes'] = info['likes']
                result['read'] = info['read']
                result['hot_heat'] = info['hot_heat']
                result['collections'] = info['collections']

                result_title['content_id'] = str(info['_id'])
                result_title['title'] = str(info['title'])
                # self._redis.redis.set("news_detail:" + str(info['_id']), str(result))
                self._redis.redis.set("news_title:" + str(info['_id']), str(result_title))
                if count % 100 == 0:
                    print(count)
                count += 1


if __name__ == '__main__':
    write_to_redis = Write_to_redis()
    write_to_redis.get_from_mongo()

