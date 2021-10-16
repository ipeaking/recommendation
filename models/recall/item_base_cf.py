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
import math
import time


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
                self.user_item_history.setdefault(user, [])
                self.train[user][item] = int(score)
                self.user_item_history[user].append(item)

    def cf_item_train(self):
        """

        :return:相似度矩阵：{content_id:{content_id:score}}
        """
        print("start train")
        self.item_to_item, self.item_count = dict(), dict()

        for user, items in self.train.items():
            for i in items.keys():
                self.item_count.setdefault(i, 0)
                self.item_count[i] += 1  # item i 出现一次就加1分

        for user, items in self.train.items():
            for i in items.keys():
                self.item_to_item.setdefault(i, {})
                for j in items.keys():
                    if i == j:
                        continue
                    self.item_to_item[i].setdefault(j, 0)
                    self.item_to_item[i][j] += 1 / (
                        math.sqrt(self.item_count[i] + self.item_count[j])) # item i 和 j 共现一次就加1

        # 计算相似度矩阵
        for _item in self.item_to_item:
            self.item_to_item[_item] = dict(sorted(self.item_to_item[_item].items(),
                                                   key=lambda x: x[1], reverse=True)[0:30])


    def cal_rec_item(self, user, N=5):
        """
        给用户user推荐前N个感兴趣的文章
        :param user:
        :param N:
        :return:  推荐的文章的列表
        """
        rank = dict()
        try:
            action_item = self.train[user]
            for item, score in action_item.items():
              for j, wj in self.item_to_item[item].items():
                if j in action_item.keys(): #如果文章j已经被阅读过了，那么我们就不会去推荐了
                    continue
                rank.setdefault(j, 0)
                rank[j] += score * wj / 10000

            res = dict(sorted(rank.items(), key=lambda x:x[1], reverse=True)[0:N])
            print(res)
            return res

        except:
            return {}