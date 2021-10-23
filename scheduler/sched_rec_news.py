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
# @Time    : 2021-10-12 20:49
# @Author  : Hongbo Huang
# @File    : sched_rec_news.py
from read_data import read_news_data
from models.recall.item_base_cf import ItemBaseCF
import pickle
from dao import redis_db


class SchedRecNews(object):
    def __init__(self):
        self.news_data = read_news_data.NewsData()
        self.Redis = redis_db.Redis()

    def schedule_job(self):
        """
        1、首先我们要知道要推荐给谁，也就是说，我们要先计算一下推荐用户的列表，分成冷启动、有推荐记录的两种，我们只需要给有阅读记录的人计算
        2、我们通过训练，得到协同过滤矩阵
        3、做推荐
        4、把推荐的结果写到数据库里面，以备后面应用
        :return:
        """
        user_list = self.news_data.rec_user()
        # self.news_data.cal_score()
        self.news_model_train = ItemBaseCF("../data/news_score/news_log.csv")
        self.news_model_train.cf_item_train()
        # 模型固化
        with open("../data/recall_model/CF_model/cf_news_recommend.m", mode='wb') as article_f:
            pickle.dump(self.news_model_train, article_f)
        for user_id in user_list:
            self.rec_list(user_id)

    def rec_list(self, user_id):
        recall_result = self.news_model_train.cal_rec_item(str(user_id))
        recall = []
        scores = []
        for item, score in recall_result.items():
            recall.append(item)
            scores.append(score)
        data = dict(zip(recall_result, scores))
        self.to_redis(user_id, data)
        print("item_cf to redis finish...")

    def to_redis(self, user_id, rec_conent_score):
        rec_item_id = "rec_item:" + str(user_id)
        res = dict()
        for content, score in rec_conent_score.items():
            res[content] = score

        if len(res) > 0:
            data = dict({rec_item_id: res})
            for item, value in data.items():
                self.Redis.redis.zadd(item, value)


if __name__ == '__main__':
    sched = SchedRecNews()
    sched.schedule_job()