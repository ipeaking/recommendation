import sys

sys.path.append('../../..')
print(sys.path)
from dao import mongo_db
from config import params
import time
import datetime
from dateutil import parser
from operator import itemgetter
# import lightgbm as lgb
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import GridSearchCV
from sklearn.utils import shuffle

import gc
import pickle

pd.set_option("display.max_columns", 32)


class ConstructData(object):
    def __init__(self):
        self.mongo_ai = mongo_db.MongoDB(params.mongodb, params.conf)
        self.user_label = self.mongo_ai
        self.MongoDB = mongo_db.MongoDB(params.mongodb, params.conf)
        self.user_search = self.MongoDB.db_jx3ugc['user_read_history']

        self.content_features = dict()
        self.person_features = dict()
        self.person_short_term_feats = dict()
        self.person_long_term_feats = dict()
        self.read_data = dict()
        self.recommend_data = dict()
        self.training_dataset = list()

    def get_read_recommend_data(self, start_month, day, init=1):
        if init:
            last_update_time = parser.parse('2019-11-20 00:00:00')
        else:
            last_update_time = parser.parse((datetime.datetime.now() - datetime.timedelta(days=2)).strftime(
                '%Y-%m-%dT%H:%M:%S'))
        update_time = parser.parse((datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
            '%Y-%m-%dT%H:%M:%S'))
        read_data = MongoDB(params.mongodb, params.conf).db_jx3ugc['dynamic'] \
            .find({"model": {'$eq': "Moment"}, "type": {'$eq': "ImageText"},
                   'create_time': {'$gte': last_update_time, '$lte': update_time}},
                  {'_id': 1, 'person_id': 1, 'create_time': 1})
        for info in read_data:
            item_id = str(info['_id'])
            person_id = info['person_id']
            if item_id not in self.content_features:
                continue
            year = info['create_time'].year
            month = info['create_time'].month
            day = info['create_time'].day
            label = 1
            self.construct_traningset(person_id, item_id, year, month, day, label)

            # short_title_kw_sec, short_content_kw_sec, short_topic = \
            #     self.compute_long_short_term_feats(person_id, item_id, year, month, day)
            # title_length, content_length, real_read_count, read_count, like_count, comment_count, \
            # zhijian_comment_count, favourite_count = \
            #     itemgetter(*['title_length', 'content_length', 'real_read_count', 'read_count', 'like_count',
            #                  'comment_count', 'zhijian_comment_count', 'favourite_count'])(
            #         self.content_features[item_id])
            # temp = [1, title_length, content_length, real_read_count, read_count, like_count, comment_count, \
            #         zhijian_comment_count, favourite_count, short_title_kw_sec, short_content_kw_sec]
            # self.training_dataset.append(temp + short_topic)

        if init:
            recommend_find = {"create_time": {'$regex': '2019-{}.*'.format(start_month)}}
            recommend_data = self.mongo_ai.db_jx3ai['rec_his_dynamic_2019{}'.format(start_month)] \
                .find(recommend_find, {'_id': 0, 'person_id': 1, 'rec_list': 1, 'create_time': 1})
        else:
            # 传入当前时间的前一天日期（年，月）
            recommend_find = {"create_time": {'$regex': '2019-12-{}.*'.format(day)}}

        for info in recommend_data:
            person_id = info['person_id']
            for item_id in info['rec_list'][:5]:
                # if person_id not in self.read_data:
                #     continue
                # if item_id not in self.read_data[person_id]:
                year = info['create_time'][:4]
                month = info['create_time'][5:7]
                day = info['create_time'][8:10]

                label = 0
                self.construct_traningset(person_id, item_id, year, month, day, label)
                # short_title_kw_sec, short_content_kw_sec, short_topic = \
                #     self.compute_long_short_term_feats(person_id, item_id, year, month, day)
                # title_length, content_length, real_read_count, read_count, like_count, comment_count, \
                # zhijian_comment_count, favourite_count = \
                #     itemgetter(*['title_length', 'content_length', 'real_read_count', 'read_count', 'like_count',
                #                  'comment_count', 'zhijian_comment_count', 'favourite_count'])(
                #         self.content_features[item_id])
                # temp = [0, title_length, content_length, real_read_count, read_count, like_count, comment_count, \
                #         zhijian_comment_count, favourite_count, short_title_kw_sec, short_content_kw_sec]
                # self.training_dataset.append(temp + short_topic)

    def get_data(self, init=1):
        """
        content features:title keyword, content keyword, topic
        person features:User long-term and short-term keyword characteristics,
                        User long-term and short-term topic characteristics,
                        User search keyword:
        :return:
        """
        for info in self.mongo_ai.db_jx3ai['content_label'].find():
            self.content_features[info['_id']] = info

        if init:
            find = {}
            last_update_time = parser.parse((datetime.datetime(2019, 10, 1)).strftime(
                '%Y-%m-%dT%H:%M:%S'))
            update_time = parser.parse((datetime.datetime(2020, 1, 1)).strftime(
                '%Y-%m-%dT%H:%M:%S'))
            find = {'log_time': {'$gte': last_update_time, '$lte': update_time}}


        else:
            # last_update_time = parser.parse((datetime.datetime.now() - datetime.timedelta(days=100)).strftime(
            #     '%Y-%m-%dT%H:%M:%S'))

            last_update_time = parser.parse((datetime.datetime(2019, 11, 1)).strftime(
                '%Y-%m-%dT%H:%M:%S'))
            update_time = parser.parse((datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
                '%Y-%m-%dT%H:%M:%S'))
            find = {'log_time': {'$gte': last_update_time, '$lte': update_time}}

        perosn_short_term_info = self.user_label.db_jx3ai['user_label_short'].find(
            find, {"person_id": 1, "short_content_kw": 1, "short_title_kw": 1, 'log_time': 1, 'short_topic': 1})
        for index, info in enumerate(perosn_short_term_info):
            person_id = info['person_id']
            log_time = info['log_time'].strftime('%Y-%m-%d')
            self.person_short_term_feats.setdefault(person_id, {})
            self.person_short_term_feats[person_id].setdefault(log_time, {})
            self.person_short_term_feats[person_id][log_time]['short_title_kw'] = info['short_title_kw']
            self.person_short_term_feats[person_id][log_time]['short_content_kw'] = info['short_content_kw']
            self.person_short_term_feats[person_id][log_time]['short_topic'] = info['short_topic']
            if index % 10000 == 0:
                print(index)

        perosn_long_term_info = self.user_label.db_jx3ai['user_label_long'].find(
            find, {"person_id": 1, "long_content_kw": 1, "long_title_kw": 1, 'log_time': 1, 'long_topic_title': 1,
                   'long_topic': 1})
        for index, info in enumerate(perosn_long_term_info):
            person_id = info['person_id']
            log_time = info['log_time'].strftime('%Y-%m-%d')
            self.person_long_term_feats.setdefault(person_id, {})
            self.person_long_term_feats[person_id].setdefault(log_time, {})
            self.person_long_term_feats[person_id][log_time]['long_title_kw'] = info['long_title_kw']
            self.person_long_term_feats[person_id][log_time]['long_content_kw'] = info['long_content_kw']
            self.person_long_term_feats[person_id][log_time]['long_topic'] = info['long_topic']
            if index % 10000 == 0:
                print(index)

        if init:
            self.save_data()

    def save_data(self):
        with open('../data/content_features_moment.pickle', 'wb') as _file:
            pickle.dump(self.content_features, _file)
        with open('../data/person_short_term_feats_moment.pickle', 'wb') as _file:
            pickle.dump(self.person_short_term_feats, _file)
        with open('../data/person_long_term_feats_moment.pickle', 'wb') as _file:
            pickle.dump(self.person_long_term_feats, _file)

    def load_data(self):
        with open('../data/person_short_term_feats.pickle', 'rb') as _file:
            self.person_short_term_feats = pickle.load(_file)

        with open('../data/person_long_term_feats.pickle', 'rb') as _file:
            self.person_long_term_feats = pickle.load(_file)

        with open('../data/content_features.pickle', 'rb') as _file:
            self.content_features = pickle.load(_file)

    def compute_long_short_term_feats(self, person_id, item_id, year, month, day):
        short_title_kw_sec, short_content_kw_sec, short_topic_multiple = 0, 0, [0, 0, 0]
        long_title_kw_sec, long_content_kw_sec, long_topic_multiple = 0, 0, [0, 0, 0]

        flag = 0
        log_time = (datetime.datetime(int(year), int(month), int(day)) - datetime.timedelta(days=1)).strftime(
            '%Y-%m-%d')
        if person_id in self.person_short_term_feats:
            if log_time in self.person_short_term_feats[person_id]:
                flag = 1
        if flag == 0:
            short_title_kw_sec, short_content_kw_sec, short_topic_multiple = 0, 0, [0, 0, 0]
            long_title_kw_sec, long_content_kw_sec, long_topic_multiple = 0, 0, [0, 0, 0]

        else:
            title_kw = [kw[0] for kw in self.content_features[item_id]['title_kw']]
            content_kw = [kw[0] for kw in self.content_features[item_id]['content_kw']]

            # short term feats
            for kw in self.person_short_term_feats[person_id][log_time]['short_title_kw']:
                if kw in title_kw:
                    short_title_kw_sec += 1
            for kw in self.person_short_term_feats[person_id][log_time]['short_content_kw']:
                if kw in content_kw:
                    short_content_kw_sec += 1
            short_topic_sec = 0
            short_topic_sum = 0
            short_topic_max = 0
            for topic in self.content_features[item_id]['specified_topic']:
                if topic in self.person_short_term_feats[person_id][log_time]['short_topic']:
                    short_topic_sec += 1
                    short_topic_sum += self.person_short_term_feats[person_id][log_time]['short_topic'][topic]
                    if self.person_short_term_feats[person_id][log_time]['short_topic'][topic] > short_topic_max:
                        short_topic_max = self.person_short_term_feats[person_id][log_time]['short_topic'][topic]

            short_topic_multiple = [short_topic_sec, short_topic_max, short_topic_sum]

            # long term feats

            for kw in self.person_long_term_feats[person_id][log_time]['long_title_kw']:
                if kw in title_kw:
                    long_title_kw_sec += 1
            for kw in self.person_long_term_feats[person_id][log_time]['long_content_kw']:
                if kw in content_kw:
                    long_content_kw_sec += 1

            long_topic_sec = 0
            long_topic_sum = 0
            long_topic_max = 0
            for topic in self.content_features[item_id]['specified_topic']:
                if topic in self.person_long_term_feats[person_id][log_time]['long_topic']:
                    long_topic_sec += 1
                    long_topic_sum += self.person_long_term_feats[person_id][log_time]['long_topic'][topic]
                    if self.person_long_term_feats[person_id][log_time]['long_topic'][topic] > long_topic_max:
                        long_topic_max = self.person_long_term_feats[person_id][log_time]['long_topic'][topic]
            long_topic_multiple = [long_topic_sec, long_topic_max, long_topic_sum]

        return short_title_kw_sec, short_content_kw_sec, short_topic_multiple, \
               long_title_kw_sec, long_content_kw_sec, long_topic_multiple

    def construct_traningset(self, person_id, item_id, year, month, day, label):
        short_title_kw_sec, short_content_kw_sec, short_topic_multiple, \
        long_title_kw_sec, long_content_kw_sec, long_topic_multiple = \
            self.compute_long_short_term_feats(person_id, item_id, year, month, day)

        title_length, content_length, real_read_count, read_count, like_count, comment_count, \
        zhijian_comment_count, favourite_count = \
            itemgetter(*['title_length', 'content_length', 'real_read_count', 'read_count', 'like_count',
                         'comment_count', 'zhijian_comment_count', 'favourite_count'])(
                self.content_features[item_id])
        temp = [int(label), title_length, content_length, real_read_count, read_count, like_count, comment_count, \
                zhijian_comment_count, favourite_count, short_title_kw_sec, short_content_kw_sec, long_title_kw_sec,
                long_content_kw_sec] + short_topic_multiple + long_topic_multiple
        temp = [str(i) for i in temp]
        # print(temp)
        # self.count += 1
        # if self.count % 10000 == 0:
        #     print('-----------------------------------', self.count)
        self._file.writelines(','.join(temp) + '\n')

    def scheduler(self, init):
        self.get_data()
        print('finish')
        # return 0

        print('content_features length:', len(self.content_features))
        num_of_reading = 0
        num_of_recommend = 0
        count = 0
        self._file = open('../data/training_data_moment_10-12.csv', 'a')
        if init:
            # self.load_data()
            with open('../data/ctr_recommend_data.csv') as _file:
                for index, line in enumerate(_file):
                    person_id, item_id, year, month, day, _, _, _, label = line.replace('\n', '').split(',')
                    if index == 0 or item_id not in self.content_features:
                        continue
                    try:
                        month, day = int(month), int(day)
                    except:
                        print(person_id, item_id, year, month, day, label)
                        continue
                    num_of_recommend += 1
                    if month < 10: continue
                    try:
                        self.construct_traningset(person_id, item_id, year, month, day, 0)
                    except:
                        print('recommend',person_id, item_id, year, month, day, label)
                    if index % 100000 == 0:
                        print('processing recommend data:', index)

            data_history = self.user_search.find({
                "create_time": {'$gte': parser.parse("2019-10-01 00:00:00"),
                                '$lte': parser.parse("2020-01-01 00:00:00")},
                "content_model": "Moment",
                "content_type": "ImageText"
            },
                {
                    "person_id": 1,
                    "content_id": 1,
                    "content_model": 1,
                    "content_type": 1,
                    "create_time": 1
                })
            for x in data_history:
                year = x['create_time'].year
                month = x['create_time'].month
                day = x['create_time'].day
                person_id = x['person_id']
                item_id = x['content_id']
                label = 1
                num_of_reading += 1
                if index == 0 or item_id not in self.content_features:
                    continue
                try:
                    self.construct_traningset(person_id, item_id, year, month, day, label)
                except:
                    print('reading',person_id, item_id, year, month, day, label)
                if count % 100000 == 0:
                    print('processing reading data:', count)
                count += 1
        else:
            pass
        self._file.close()
        print('num of reading:', num_of_reading)
        print('num of recommend:', num_of_recommend)


if __name__ == "__main__":
    ConstructData = ConstructData()
    # month_time = 12
    ConstructData.scheduler(1)
    # ConstructData.get_read_recommend_data(12)
    # ConstructData.get_data()
    # ConstructData.construct_features()
