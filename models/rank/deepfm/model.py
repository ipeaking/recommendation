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
# @File    : model.py
import tensorflow.compat.v1 as tf

print(tf.__version__)


class deepFM(object):
    def __init__(self, parameters):
        super.__init__()
        self.fm_cols = parameters['fm_cols']
        self.label_name = parameters['label_name']
        self.fm_emb_dim = parameters['fm_emb_dim']
        self.hidden_units = parameters['hidden_units']
        self.dropout = parameters['dropout']
        self.batch_size = parameters['batch_size']
        self.epoch_size = parameters['epoch_size']
        self.lr = parameters['learning_rate']

    def build_graph(self):
        graph = tf.Graph()
        with graph.as_default():
            with tf.name_scope('ModelInput'):
                self.fm_cols_vals = tf.placeholder(dtype=tf.float32, shape=[self.batch_size,
                                                                            len(self.fm_cols)], name='features')
                self.labels = tf.placeholder(dtype=tf.float32, shape=[self.batch_size, 1], name='label')
                self.training = tf.placeholder(dtype=tf.bool, shape=[], name='training_flag')

        pass

    def train(self):
        pass

    def predict(self):
        pass

    def get_graph(self):

        pass

    def print_graph(self):
        pass

    def accuracy(self):
        pass
