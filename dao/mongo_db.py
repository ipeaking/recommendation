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
# @Time    : 2021-08-10 21:05
# @Author  : Hongbo Huang
# @File    : mongo_db.py
import pymongo
import datetime


class MongoDB(object):
    def __init__(self, db):
        mongo_client = self._connect('127.0.0.1', '27017', '', '', db)
        self.db_client = mongo_client[db]
        self.collection_test = self.db_client['test_collections']

    def _connect(self, host, port, user, pwd, db):
        mongo_info = self._splicing(host, port, user, pwd, db)
        mongo_clent = pymongo.MongoClient(mongo_info, connect=False)
        return mongo_clent

    @staticmethod
    def _splicing(host, port, user, pwd, db):
        client = 'mongodb://' + host + ":" + str(port) + "/"
        if user != '':
            client = 'mongodb://' + user + ":" + pwd + "@" + host + ":" + str(port) + "/"
            if db != '':
                client + db

        return client

    def test_insert(self):
        testcollection = dict()
        testcollection['name'] = 'Ricky'
        testcollection['job'] = 'AI programmer'
        testcollection['date'] = datetime.datetime.utcnow()
        self.collection_test.insert_one(testcollection)


if __name__ == '__main__':
    mongo = MongoDB(db='recommendation')
    mongo.test_insert()