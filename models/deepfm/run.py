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
# @Time    : 2020-12-24 20:33
# @Author  : Hongbo Huang
# @File    : run.py
import joblib
import pandas as pd
import numpy as np
import os
import time
import sys
import random
import matplotlib.pyplot as plt
import tensorflow as tf
# tf.disable_v2_behavior()
from sklearn.metrics import accuracy_score
from itertools import chain
from utils import fill_na, prepare_data, preprocess, build_points_list
from model import deepFM

# 准备数据集
dftrain, dfeval = prepare_data('titanic-train.csv', 'titanic-eval.csv')
batch_size = 32
epoch_num = 20
epoch_size = dftrain.shape[0]//batch_size

if dftrain.shape[0] % batch_size != 0:
    epoch_size += 1

ft_names = ['sex', 'age', 'n_siblings_spouses', 'parch', 'fare', 'class', 'deck', 'embark_town', 'alone']

label_name = 'survived'

train_points = build_points_list(dftrain, ft_names, label_name)
eval_points = build_points_list(dfeval, ft_names, label_name)

# 训练模型
parameters = {}
parameters['fm_cols'] = ft_names
parameters['label_name'] = label_name
parameters['fm_emb_dim'] = 32
parameters['hidden_units'] = [32, 16]
parameters['dropprob'] = 0.3
parameters['batch_size'] = batch_size
parameters['epoch_size'] = epoch_size
parameters['learning_rate'] = 0.005

mymodel = deepFM(parameters)
mymodel.train(train_points, eval_points, epoch_num, save_path='save/deepfm.ckpt', load_path=None)