import pandas as pd
import numpy as np


class DataPoint:
    def __init__(self):
        self.features={}
        self.label=None
        
        
def fill_na(df):
    fill_na_strategy = {
        'sex': 'unk',
        'age': 0,
        'n_siblings_spouses': 0,
        'parch': 0,
        'fare': 0,
        'class': 'unk',
        'deck':'unk',
        'embark_town': 'unk',
        'alone': 'unk'
    }
    for col in fill_na_strategy:
        df.loc[df[col].isnull(), col] = fill_na_strategy[col]

        
def preprocess(df,cate_cols,existed_cate=None):
    if not existed_cate:
        categories = {}
        for c in cate_cols:
            categories[c] = df[c].unique().tolist()
            
            #make sure 'unk' has code 0
            if 'unk' in categories[c]:
                categories[c].remove('unk')
            categories[c]=['unk']+categories[c]

            df[c] = pd.Categorical(df[c],
                                     categories=categories[c]).codes
        return categories
    else:
        for c in cate_cols:
            df[c] = pd.Categorical(df[c],
                                     categories=existed_cate[c]).codes
        return

        
def prepare_data(train_file,eval_file):
    #read data
    dftrain = pd.read_csv(train_file)
    dfeval = pd.read_csv(eval_file)
    dftrain.info()
    
    #fill na values
    fill_na(dftrain)
    fill_na(dfeval)
    
    #preprocess dataset
    meta_cate=preprocess(dftrain,
            cate_cols=['sex','class','deck','embark_town','alone']
                )
    preprocess(dfeval,
            cate_cols=['sex','class','deck','embark_town','alone'],
            existed_cate=meta_cate)
    
    return dftrain,dfeval

    
#we wrap each row of original dataset into a datapoint instance, thus the dataset becomes a list of datapoints
#this process is really convenient for further computation
def build_points_list(df,ft_names,label_name):
    res=[]
    for i in range(df.shape[0]):
        dp=DataPoint()
        for c in ft_names:
            dp.features[c]=df.loc[i,:][c]
        dp.label=df.loc[i,:][label_name]
                
        res.append(dp)
    return res


#build a data iterator to generate batch set
from collections import defaultdict
class DataInput:

    def __init__(self, data, batch_size, features_name, label_name):
        self.batch_size = batch_size
        self.data = data
        self.epoch_size = len(self.data) // self.batch_size
        '''
        if self.epoch_size * self.batch_size < len(self.data):
            self.epoch_size += 1
        '''
        self.i = 0
        
        self.features_name=features_name

    def __iter__(self):
        return self

    def __next__(self):

        if self.i == self.epoch_size:
            raise StopIteration

        ts = self.data[self.i * self.batch_size: min((self.i + 1) * self.batch_size,
                                                     len(self.data))]
        self.i += 1

        labels=[]
        features=np.zeros((len(ts),len(self.features_name)))
        
        for ii,dp in enumerate(ts):
            for jj,c in enumerate(self.features_name):
                features[ii,jj]=dp.features[c]
            labels.append(dp.label)
        
            
        return self.i, (features,labels)
