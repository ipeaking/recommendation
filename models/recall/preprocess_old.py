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
# @Time    : 2021-11-09 20:53
# @Author  : Hongbo Huang
# @File    : preprocess_old.py
from tqdm import tqdm
import numpy as np
import random
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
def gen_data_set(data, negsample=0):
    data.sort_values("timestamp", inplace=True)
    items_ids = data['item_id'].unique()

    train_set = list()
    test_set = list()

    for reviewrID, hist in tqdm(data.groupby('user_id')):
        pos_list = hist['item_id'].tolist()
        rating_list = hist['rating'].tolist()

        if negsample > 0:
            candidate_set = list(set(items_ids) - set(pos_list))
            neg_list = np.random.choice(candidate_set, size=len(pos_list) * neg_list, replace=True)
        for i in range(1, len(pos_list)):
            if i != len(pos_list) - 1:
                train_set.append((reviewrID, hist[::-1], pos_list[i], 1, len(hist[::-1]), rating_list[i]))
                for negi in range(negsample):
                    train_set.append((reviewrID, hist[::-1], neg_list[i * negsample + negi], 0, len(hist[::-1])))
            else:
                test_set.append((reviewrID, hist[::-1], pos_list[i], 1, len(hist[::-1]), rating_list[i]))

    random.shuffle(train_set)
    random.shuffle(test_set)

    return train_set, test_set

def gen_model_input(train_set, user_profile, seq_max_len):
    train_uid = np.array([line[0] for line in train_set])
    train_seq = [line[1] for line in train_set]
    train_iid = np.array([line[2] for line in train_set])
    train_label = np.array([line[3] for line in train_set])
    train_hist_len = np.array([line[4] for line in train_set])

    """
    pad_sequences数据预处理
    sequences：浮点型或者整数构成的两层嵌套列表
    maxlen: None或者整数，为序列的最大长度，大于此长度的序列将被截断，小于此长度的序列将在后面补0
    dtype: 返回的numpy array的数据类型
    padding：'pre'或'post'，确定当需要截断的时候，从起始位置还是从结尾开始截断
    value：浮点型，此值将在填充式代替默认的填充值0
    """
    train_seq_pad = pad_sequences(train_seq, maxlen=seq_max_len, padding='post', truncating='post', value=0)
    train_model_input = {"user_id": train_uid, "item_id": train_iid, "hist_item_id": train_seq_pad,
                         "hist_len": train_hist_len}

    for key in {"gender", "age", "city"}:
        train_model_input[key] = user_profile.loc[train_model_input['user_id']][key].values

    return train_model_input, train_label