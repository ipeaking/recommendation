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
# @Time    : 2020-12-16 20:18
# @Author  : Hongbo Huang
# @File    : model_predict.py
from dao.mongo_db import MongoDB
from util.file_locator import getfile
MODEL_FILE = getfile(r"../../data/GLR.model")
import pickle
from operator import itemgetter
from util import log_utils
logger = log_utils.Logger()
import pandas as pd
import numpy as np


class Predict(object):
    def __init__(self):
        self.mongo = MongoDB(db='loginfo')
        self.db_client = self.mongo.db_client  # 数据库的客户端
        self.content = self.db_client['content_labels']
        self.user_short_label = self.db_client['user_short_label']
        self.user_long_label = self.db_client['user_long_label']
        self.content_features = dict()
        self.person_short_term_feats = dict()
        self.person_long_term_feats = dict()

    def test_mongo(self):
        datas = self.user_short_label.find()
        for data in datas:
            print(data['short_kw'])

    """
    从MongoDB里取数据
    """
    def load_data_from_mongo(self):
        with open(MODEL_FILE, 'rb') as _file:
            self.model = pickle.load(_file)
        data = self.content.find()
        for info in data:
            self.content_features[info['content_id']] = info

    """
    数据处理（用户特征数据）
    """
    def get_data(self, person_id):
        person_short_term_info = self.user_short_label.find(
            {'user_id': person_id},
            {"user_id": 1, "short_title_kw": 1, "content_kw": 1, "log_time": 1}
        ).sort([('log_time', -1)])
        for info in person_short_term_info:
            person_id = info['person_id']
            self.person_short_term_feats.setdefault(person_id, {})
            self.person_short_term_feats[person_id]['short_title_kw'] = info['short_title_kw']
            self.person_short_term_feats[person_id]['short_content_kw'] = info['content_kw']

        person_long_term_info = self.user_long_label.find(
            {'user_id': person_id},
            {"user_id": 1, "long_title_kw": 1, "content_kw": 1, "log_time": 1}
        ).sort([('log_time', -1)])
        for info in person_long_term_info:
            person_id = info['person_id']
            self.person_long_term_feats[person_id]['long_title_kw'] = info['long_title_kw']
            self.person_long_term_feats[person_id]['content_kw'] = info['content_kw']

    """
    数据特征组合
    """
    def combine_data(self, person_id, content_recall_list):
        data = list()
        for item_id in content_recall_list:
            if item_id not in self.content_features or person_id not in self.person_short_term_feats:
                data.append([0] * 18)
                logger.info("the record have been return 0:" + person_id + "," + item_id)
                continue
            short_title_kw_sec, short_content_kw_sec, long_title_kw_sec, long_content_kw_sec \
                = self.compute_long_short_term_feats(person_id, item_id)

            word_num, read_count, likes_count, collections = itemgetter(*['word_num', 'read_count', 'likes_count',
                                                                          'collections'])(self.content_features[item_id])
            temp =[word_num, read_count, likes_count, collections, short_title_kw_sec, short_content_kw_sec,
                   long_title_kw_sec, long_content_kw_sec]
            data.append(temp)

        return pd.DataFrame(data)

    """
    数据预测
    """
    def predict(self, person_id, content_recall_list, model_type='gbdtlr'):
        self.get_data(person_id)
        data = self.combine_data(person_id, content_recall_list)
        if model_type == 'gbdt_lr':
            x_test_gbdt = self.model.Gbdt_transform.predict(data.values, pred_leaf=True)
            transformed_test_matrix = np.zeros([len(data.values), len(x_test_gbdt[0]) * 15], dtype=np.int8)
            for i in range(0, len(x_test_gbdt)):
                temp = np.arange(len(x_test_gbdt[0])) * 15 + np.array(x_test_gbdt[i])
                transformed_test_matrix[i][temp] += 1
            pred = self.model.Gbdt_transform.predict_proba(transformed_test_matrix)
            pred = pred[:, 1]
            return {content_id: click_pred for content_id, click_pred in zip(content_recall_list, pred)}

    def compute_long_short_term_feats(self, person_id, item_id):
        short_title_kw_sec, short_content_kw_sec = 0, 0
        long_title_kw_sec, long_content_kw_sec = 0, 0
        title_kw = [kw[0] for kw in self.content_features[item_id]['title_kw']]
        content_kw = [kw[0] for kw in self.content_features[item_id]['content_kw']]

        for kw in self.person_short_term_feats[person_id]['short_title_kw']:
            if kw in title_kw:
                short_title_kw_sec += 1
        for kw in self.person_short_term_feats[person_id]['short_content_kw']:
            if kw in content_kw:
                short_content_kw_sec += 1

        for kw in self.person_long_term_feats[person_id]['long_title_kw']:
            if kw in title_kw:
                long_title_kw_sec += 1
        for kw in self.person_long_term_feats[person_id]['long_content_kw']:
            if kw in content_kw:
                long_content_kw_sec += 1

        return short_title_kw_sec, short_content_kw_sec, long_title_kw_sec, long_content_kw_sec


if __name__ == '__main__':
    person_id = "244"
    content_recall_list = ['54a55b1f6d4e1c5a4d5e1f5', '45454654a56e4e8dcb6a5']
    gbdt_model = Predict()
    result = gbdt_model.predict(person_id, content_recall_list, model_type='gbdtlr')
    print(sorted(result.items(), key=lambda x: x[1]))

