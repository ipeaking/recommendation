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
# @Time    : 2021-12-07 20:41
# @Author  : Hongbo Huang
# @File    : gbdtlr.py
import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import lightgbm as lgb
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.linear_model import LogisticRegression
import numpy as np
import pickle


class GLR(object):
    def __init__(self):
        pass

    """
    1. 加载数据
    2. 处理数据
    3. 训练模型
        gbdt模型
        lr模型
        gbdt+lr
    """
    def load_data(self):
        # 数据特征的提取
        data = pd.read_csv('../../data/trainningset.csv', header=None)
        for _file in ['../../data/trainningset_10', '../../data/trainningset_11', '../../data/trainningset_12']:
            temp = pd.cut(_file, header=None)
            data = pd.concat([data, temp], axis=0, ignore_index=True)
        data = data.reset_index(drop=True)
        temp = ['var' + str(i) for i in range(len(data.columns))]
        data.columns = temp
        return data

    def data_process(self):
        data = self.load_data()
        print('data processing')
        data = shuffle(data, random_state=2019)
        features = [col for col in data.columns if col not in ['var0']]
        print('Length Features', len(features))
        data_len = len(data)
        x_test = data[features].loc[int(data_len * 0.9):]
        y_test = data['var0'].loc[int(data_len * 0.9):]

        x = data[features].loc[:int(data_len * 0.9)]
        y = data['var0'].loc[:int(data_len * 0.9)]
        print('y length', len(y))

        x_train, x_valid, y_train, y_valid = train_test_split(x, y, test_size=0.1, random_state=2019)
        print('data processing has finished...')
        return x_train, x_valid, y_train, y_valid, x_test, y_test

    def train_model(self):
        x_train, x_valid, y_train, y_valid, x_test, y_test = self.data_process()
        def gbdt(num_leaves=15, num_tree=100):
            train = lgb.Dataset(x_train, y_train)
            valid = lgb.Dataset(x_valid, y_valid, reference=True)
            params = {
                'task': 'train',
                'boosting_type': 'gbdt',
                'objective': 'binary',
                'metric': {'binary_logloss'},
                'num_leaves': num_leaves,
                'num_tree': num_tree,
                'learning_rate': 0.1,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': 0,
                'n_thread': 12
            }
            print('training lgb model')
            self.gbdt = lgb.train(params,
                                  train,
                                  early_stopping_rounds=100,
                                  num_boost_round=100,
                                  valid_sets=valid,
                                  verbose_eval=300)
            y_test_pred = self.gbdt.predict(x_test)
            y_test_pred[y_test_pred < 0.5] = 0
            y_test_pred[y_test_pred >= 0.5] = 1
            accuracy = accuracy_score(y_test, y_test_pred)
            precision = precision_score(y_test, y_test_pred)
            recall = recall_score(y_test, y_test_pred)
            f1 = f1_score(y_test, y_test_pred)

            print('accuracy:{}, precision:{}, recall:{}, f1:{}'.format(accuracy, precision, recall, f1))

        def lr():
            print('training LR model')
            self.Lr = LogisticRegression(penalty='l2', C=0.05)
            self.Lr.fit(x_train, y_train)
            y_test_pred = self.Lr.predict(x_test)
            accuracy = accuracy_score(y_test, y_test_pred)
            precision = precision_score(y_test, y_test_pred)
            recall = recall_score(y_test, y_test_pred)
            f1 = f1_score(y_test, y_test_pred)
            print('accuracy:{}, precision:{}, recall:{}, f1:{}'.format(accuracy, precision, recall, f1))

        def gbdtLr(x_train, x_valid, y_train, y_valid, x_test, y_test):
            num_leaves = 15
            num_trees = 20
            train = lgb.Dataset(x_train, y_train)
            valid = lgb.Dataset(x_valid, y_valid, reference=True)
            params = {
                'task': 'train',
                'boosting_type': 'gbdt',
                'objective': 'binary',
                'num_leaves': num_leaves,
                'num_trees': num_trees,
                'learning_rate': 0.1,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': 0
            }
            self.Gbdt_transform = lgb.train(params,
                                            train,
                                            early_stopping_rounds=100,
                                            num_boost_round=100,
                                            valid_sets=valid,
                                            verbose_eval=300)
            x_train_gbdt = self.Gbdt_transform.predict(x_train, pred_leaf=True)
            del x_train
            transformed_training_matrix = np.zeros([len(x_train_gbdt), len(x_train_gbdt[0] * num_leaves)], dtype=np.int8)
            for i in range(0, len(y_train)):
                temp = np.arange(len(x_train_gbdt[0])) * num_leaves + np.array(x_train_gbdt[i])
                transformed_training_matrix[i][temp] += 1

            x_test_gbdt = self.Gbdt_transform.predict(x_test, pred_leaf=True)
            del x_test
            transformed_test_matrix = np.zeros([len(x_test_gbdt), len(x_train_gbdt[0] * num_leaves)], dtype=np.int8)
            for i in range(0, len(x_test_gbdt)):
                temp = np.arange(len(x_test_gbdt[0])) * num_leaves + np.array(x_test_gbdt[i])
                transformed_test_matrix[i][temp] += 1

            self.GbdtLr = LogisticRegression(penalty='l2', C=0.05)
            self.GbdtLr.fit(transformed_training_matrix, y_train)

            y_test_pred = self.GbdtLr.predict(transformed_test_matrix)
            accuracy = accuracy_score(y_test, y_test_pred)
            precision = precision_score(y_test, y_test_pred)
            recall = recall_score(y_test, y_test_pred)
            f1 = f1_score(y_test, y_test_pred)
            print('accuracy:{}, precision:{}, recall:{}, f1:{}'.format(accuracy, precision, recall, f1))
        # gbdt()
        # lr()
        gbdtLr(x_train, x_valid, y_train, y_valid, x_test, y_test)


if __name__ == '__main__':
    model = GLR()
    model.train_model()
    with open('../../data/GLR.model', 'wb') as _file:
        pickle.dump(model, _file)
