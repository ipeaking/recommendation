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
# @Time    : 2021-12-28 21:16
# @Author  : Hongbo Huang
# @File    : utils.py
import pandas as pd
import numpy as np

class DataPoint:
    def __init__(self):
        self.features = {}
        self.label = None

def fill_na(df):
    fill_na_strategy = {
        'sex': 'unk',
        'age': 0,
        'n_siblings_spouses': 0,
        'parch': 0,
        'fare': 0,
        'class': 'unk',
        'deck': 'unk',
        'embark_town': 'unk',
        'alone': 'unk'
    }
    for col in fill_na_strategy:
        df.loc[df[col].isnull(), col] = fill_na_strategy[col]

def preprocess(df, cate_cols, existed_cate=None):
    if not existed_cate:
        categories = {}
        for c in cate_cols:
            categories[c] = df[c].unique().tolist()

            if 'unk' in categories[c]:
                categories[c].remove('unk')
            categories[c] = ['unk'] + categories[c]

            df[c] = pd.Categorical(df[c], categories=categories[c]).codes

            return categories
    else:
        for c in cate_cols:
            df[c] = pd.Categorical([c], categories=existed_cate[c]).codes

            return

def prepare_data(train_file, eval_file):
    dftrain = pd.read_csv(train_file)
    dfeval = pd.read_csv(eval_file)
    dftrain.info()

    fill_na(dftrain)
    fill_na(dfeval)

    meta_cate = preprocess(dftrain, cate_cols=['sex', 'class', 'deck', 'embark_town', 'alone'])

    preprocess(dfeval, cate_cols=['sex', 'class', 'deck', 'embark_town', 'alone'], existed_cate=meta_cate)

    return dftrain, dfeval

def build_point_list(df, ft_names, label_name):
    res = []
    for i in range(df.shape[0]):
        dp = DataPoint()
        for c in ft_names:
            dp.features[c] = df.loc[i, :][c]
        dp.label = df.loc[i, :][label_name]

        res.append(df)

    return res

from collections import defaultdict
class DataInput:
    def __init__(self, data, batch_size, features_name):
        self.batch_size = batch_size
        self.data = data
        self.epoch_size = len(self.data) // self.batch_size

        self.i = 0
        self.features_name = features_name

    def __iter__(self):
        return self

    def __next__(self):

        if self.i == self.epoch_size:
            raise StopIteration

        ts = self.data[self.i * self.batch_size : min(self.i + 1) * self.batch_size, len(self.data)]

        self.i += 1

        label = []
        features = np.zeros((len(ts), len(self.features_name)))

        for ii,dp in enumerate(ts):
            for jj, c in enumerate(self.features_name):
                features[ii, jj] = dp.features[c]

            label.append(dp.label)

        return self.i, (features, label)