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
# @File    : model.py
import tensorflow.compat.v1 as tf
import random
import numpy as np
from itertools import chain
from sklearn.metrics import accuracy_score
from utils import DataInput

tf.disable_v2_behavior()


class deepFM(object):
    def __init__(self, parameters):
        super().__init__()
        self.fm_cols = parameters['fm_cols']
        self.label_name = parameters['label_name']
        self.fm_emb_dim = parameters['fm_emb_dim']
        self.hidden_units = parameters['hidden_units']
        self.dropprob = parameters['dropprob']
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

            with tf.name_scope('Embedding'):
                self.fm_emb = tf.Variable(tf.random.normal([len(self.fm_cols), self.fm_emb_dim], 0, 0.01)
                                          , name='fm_embed_matrix')
                for i in range(len(self.fm_cols)):
                    fm_col_emb = tf.tile(tf.gather(self.fm_emb, [i], axis=0), [self.batch_size, 1])
                    fm_col_emb = fm_col_emb * tf.expand_dims(self.fm_cols_vals[:, i], axis=1)
                    if i == 0:
                        fm_col_embs = tf.expand_dims(fm_col_emb, axis=1)
                    else:
                        fm_col_emb = tf.concat([fm_col_embs, tf.expand_dims(fm_col_emb, axis=1)], axis=1)

            with tf.name_scope('LowOrder'):
                summed_ft_emb = tf.reduce_sum(fm_col_embs, axis=1)
                summed_ft_emb_squre = tf.square(summed_ft_emb)

                squared_ft_emb = tf.square(fm_col_embs)
                squared_ft_emb_sum = tf.reduce_sum(squared_ft_emb, axis=1)

                second_orders = 0.5 * tf.subtract(summed_ft_emb_squre, squared_ft_emb_sum)

            with tf.name_scope('HighOrder'):
                self.hidden_layers = []
                for i, unit in enumerate(self.hidden_units):
                    self.hidden_layers += [
                        tf.keras.layers.Dense(unit, activation=tf.nn.relu, name='dnn_layer_%d'%i),
                        tf.keras.layers.BatchNormalization(),
                        tf.keras.layers.Dropout(rate=self.dropprob)
                    ]
                high_orders = tf.reshape(fm_col_embs, [-1, len(self.fm_cols) * self.fm_emb_dim])

                for i in range(len(self.hidden_layers)//3):
                    high_orders = self.hidden_layers[3*i](high_orders)
                    high_orders = self.hidden_layers[3*i+1](high_orders)
                    high_orders = self.hidden_layers[3*i+2](high_orders, training=self.training)

            with tf.name_scope('ModelOutput'):
                self.final_bn = tf.keras.layers.BatchNormalization()
                self.final_do = tf.keras.layers.Dropout(rate=self.dropprob)
                self.final_output_logits = tf.keras.layers.Dense(1, activation=None, name='output_layer')

                all_i = tf.concat([self.fm_cols_vals, second_orders, high_orders], axis=1)
                all_i = self.final_bn(all_i)
                all_i = self.final_do(all_i)
                output_logits = self.final_output_logits(all_i)

                self.output_prob = 1/(1 + tf.exp(-output_logits))

            with tf.name_scope('Loss'):
                self.loss = tf.reduce_mean(
                    tf.nn.sigmoid_cross_entropy_with_logits(output_logits=output_logits, labels=self.labels)
                )

            with tf.name_scope('Optimizer'):
                self.opt = tf.train.GradientDescentOptimizer(self.lr)
                self.update = self.opt.minimize(self.loss)

        return graph

    def train(self, train_points, eval_point, epoch_num, ob_step=5, save_path=None, load_path=None):
        if load_path is None:
            self.graph = self.build_graph()

        else:
            self.graph = tf.Graph()

        with self.graph.as_default():
            with tf.Session() as sess:
                if load_path is None:
                    saver = tf.train.Saver()
                    tf.initialize_all_variables().run()
                else:
                    saver = tf.train.import_meta_graph(load_path + '.meta')
                    saver.restore(sess, load_path)

                    self.fm_cols_vals = self.graph.get_operation_by_name("ModelInput/features").outputs[0]
                    self.labels = self.graph.get_tensor_by_name("ModelInput/labels:0")
                    self.training = self.graph.get_tensor_by_name("ModelInput/training_flag:0")

                    self.update = self.graph.get_operation_by_name("Optimizer/GradientDescent")
                    self.loss = self.graph.get_operation_by_name("Loss/Mean").outputs[0]
                    self.output_prob = self.graph.get_operation_by_name("ModelOutput/truediv").outputs[0]

                print("Start Training")
                step = 0
                cnt = 0
                metric_train_loss = 0
                train_pred = []
                train_labels = []
                for ep in range(epoch_num):
                    print("-------------- epoch %d: ----------------" % ep)
                    random.shuffle(train_points)
                    for batch_id, (ft, labels) in DataInput(train_points, self.batch_size, self.fm_cols, self.label_name):

                        feed_vals = {}
                        feed_vals[self.fm_cols_vals] = ft
                        feed_vals[self.labels] = np.expand_dims(np.array(labels), axis=1)
                        feed_vals[self.training] = True

                        _, l, predictions = sess.run(
                            [self.update, self.loss, self.output_prob],
                            feed_dict=feed_vals
                        )
                        metric_train_loss += l * len(labels)
                        cnt += len(labels)
                        train_pred.append(predictions)
                        train_labels.append(labels)

                        if step > 0 and step % ob_step ==0:
                            accuracy = self.accuracy(np.concatenate(train_pred, axis=0),
                                                     np.expand_dims(np.array(list(chain(*train_labels))), axis = 1))

                            print('Minibatch loss at step %d: %f' % (step, metric_train_loss/cnt))
                            print('Minibatch accuracy %.1f %%\n' % (100 * accuracy))

                            train_pred = []
                            train_labels = []
                            metric_train_loss = 0
                            cnt = 0

                        if step == self.epoch_size - 1:
                            step = 0
                            eval_cnt = 0
                            eval_loss = 0
                            eval_pred = []
                            eval_labels = []
                            for batch_id, (ft, labels) in DataInput(eval_point, self.batch_size, self.fm_cols, self.label_name):
                                feed_vals = {}
                                feed_vals[self.fm_cols_vals] = ft
                                feed_vals[self.labels] = np.expand_dims(np.array(labels), axis=1)
                                feed_vals[self.training] = False
                                l, predictions = sess.run([self.loss, self.output_prob], feed_dict=feed_vals)
                                eval_loss += l * len(labels)
                                cnt += len(labels)
                                eval_pred.append(predictions)
                                eval_labels.append(labels)

                            accuracy = self.accuracy(np.concatenate(eval_pred, axis=0),
                                                     np.expand_dims(np.array(list(chain(*eval_labels))), axis=1))

                            print('DEV_SET loss at step %d: %f' % (step, eval_loss/cnt))
                            print('DEV_SET accuracy: %.1f%%\n' % (100%accuracy))

                        else:
                            step += 1

                if save_path is not None:
                    saver.save(sess, save_path)

    def predict(self, data_points, load_path):
        res = []
        self.graph = tf.Graph()
        with self.graph.as_default():
            with tf.Session() as sess:
                saver = tf.train.import_meta_graph(load_path + '.meta')
                saver.restore(sess, load_path)

                graph = tf.get_default_graph()
                self.fm_cols_vals = self.graph.get_operation_by_name("ModelInput/features").outputs[0]
                self.training = self.graph.get_tensor_by_name("ModelInput/training_flag:0")
                self.output_prob = self.graph.get_operation_by_name("ModelOutput/truediv").outputs[0]

                print('start Predict.')
                for batch_id, (ft, labels) in DataInput(data_points, self.batch_size, self.fm_cols, self.label_name):
                    feed_vals = {}
                    feed_vals[self.fm_cols_vals] = ft
                    feed_vals[self.training] = False

                    predictions = sess.run(self.output_prob, feed_dict=feed_vals)
                    res.append(predictions)

        return np.concatenate(res)

    def get_graph(self):
        return self.graph

    def print_graph(self):
        tensor_name_list = [tensor.name for tensor in self.graph.as_graph_def().node]
        for tensor_name in tensor_name_list:
            print(tensor_name, '\n')

    def accuracy(self, predictions, labels):
        _predictions = np.where(predictions > 0.5, 1.0)
        return accuracy_score(_predictions, labels)