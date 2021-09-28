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
# @Time    : 2021-09-28 21:16
# @Author  : Hongbo Huang
# @File    : item_base_cf.py
from tqdm import tqdm


class ItemBaseCF(object):
    def __init__(self, train_file):
        """
        读取文件
        用户和item历史
        item相似度计算
        训练
        """
        self.train = dict()
        self.user_item_history = dict()
        self.item_to_item = dict()
        self.read_data(train_file)

    def read_data(self, train_file):
        """
        读文件，并生成数据集（用户、分数、新闻，user,score,item）
        :param train_file: 训练文件
        :return: {"user_id":{"content_id":predict_score}}
        """
        with open(train_file, mode='r', encoding='utf-8') as rf:
            for line in tqdm(rf.readlines()):
                user, score, item = line.strip().split(",")
                self.train.setdefault(user, {})
                self.user_item_history.setdefault(user, {})
                self.train[user][item] = int(score)
                self.user_item_history[user].append(item)

    def cf_item_train(self):
        """
        基于item的协同过滤，计算相似度
        :return: 相似度矩阵{content_id?:{content_id:score}}
        """
        pass

    def cal_rec_item(self, user, N=50):
        pass