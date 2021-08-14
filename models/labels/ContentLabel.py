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
# @Time    : 2021-08-14 20:34
# @Author  : Hongbo Huang
# @File    : ContentLabel.py
from dao.mysql_db import Mysql
from dao.mongo_db import MongoDB
from sqlalchemy import distinct
from models.labels.entity.content import Content
from datetime import datetime
from models.keywords.tfidf import Segment
import re


class ContentLabel(object):
    def __init__(self):
        self.seg = Segment(stopword_files=[], userdict_files=[])
        self.engine = Mysql()
        self.sesion = self.engine._DBSession()
        self.mongo = MongoDB(db='recommendation')
        self.collection = self.mongo.db_client['content_labels']

    def get_data_from_mysql(self):
        types = self.sesion.query(distinct(Content.type))
        for i in types:
            res = self.sesion.query(Content).filter(Content.type == i[0])
            if res.count() > 0:
                for x in res.all():
                    keywords = self.get_keywords(x.content, 10)
                    word_nums = self.get_words_nums(x.content)
                    create_time = datetime.utcnow()
                    content_collection = dict()
                    content_collection['describe'] = x.content
                    content_collection['keywords'] = keywords
                    content_collection['word_num'] = word_nums
                    content_collection['news_date'] = x.times
                    content_collection['hot_heat'] = 10000
                    content_collection['type'] = x.type
                    content_collection['title'] = x.title
                    content_collection['likes'] = 0
                    content_collection['read'] = 0
                    content_collection['collections'] = 0
                    content_collection['create_time'] = create_time
                    self.collection.insert_one(content_collection)

    def get_words_nums(self, contents):
        ch = re.findall('([\u4e00-\u9fa5])', contents)
        num = len(ch)
        return num

    def get_keywords(self, contents, num=10):
        keywords = self.seg.extract_keyword(contents)[:num]
        return keywords


if __name__ == '__main__':
    content_label = ContentLabel()
    content_label.get_data_from_mysql()