import os
import jieba
import jieba.posseg as pseg
import re
import jieba.analyse


class Segment(object):
    def __init__(self, stopword_files=[], userdict_files=[], jieba_tmp_dir=None):
        if jieba_tmp_dir:       #jieba分词的临时文件
            jieba.dt.tmp_dir = jieba_tmp_dir
            if not os.path.exists(jieba_tmp_dir):   #如果不存在,进行创建
                os.makedirs(jieba_tmp_dir)

        self.stopwords = set()
        for stopword_file in stopword_files:     #停用词文件都是准备好了的
            with open(stopword_file, "r", encoding="utf-8") as rf:
                for row in rf.readlines():
                    word = row.strip()
                    if len(word) > 0:
                        self.stopwords.add(word)    #将停用词文件增加到停用词中

        for userdict in userdict_files:         
            jieba.load_userdict(userdict)           #jieba加载用户字典

    def cut(self, text):
        word_list = []
        text.replace('\n', '').replace('\u3000', '').replace('\u00A0', '')  # 换行,全角的空白符,不间断的空白符,
        text = re.sub('[a-zA-Z0-9.。:：,，]', '', text)   # 从字符串中删除所有特殊字符，标点和空格
        words = pseg.cut(text)    #jieba工具进行切词

        for word in words:
            print(word.word, word.flag)    # 词性标注'n', 'nr', 'ns', 'vn', 'v'
            word = word.strip()
            if word in self.stopwords or len(word) == 0:      #去掉一些停用词和一些长度为0的词
                continue
            word_list.append(word)

        return word_list      #返回词典

    # 关键词提取
    def extract_keyword(self, text, algorithm='tfidf', use_pos=True):
        text = re.sub('[a-zA-Z0-9.。:：,，]', '', text)   # 从字符串中删除所有特殊字符，标点和空格
        if use_pos:
            allow_pos = ('n', 'nr', 'ns', 'vn', 'v')    #关键字词性
        else:
            allow_pos = ()

         
        # 基于TF-IDF算法的关键词抽取   基于 TextRank 算法的关键词抽取   algorithm  [ˈælɡərɪðəm]   算法 

        if algorithm == 'tfidf':
            tags = jieba.analyse.extract_tags(text, withWeight=False) #jieba提取关键字,withWeight 是否返回每个关键词的权重
            return tags
        elif algorithm == 'textrank':
            textrank = jieba.analyse.textrank(text, withWeight=False, allowPOS=allow_pos)  #allowPOS是允许的提取的词性，默认为allowPOS=‘ns’, ‘n’, ‘vn’, ‘v’，提取地名、名词、动名词、动词
            return textrank


if __name__ == '__main__':
    seg = Segment(stopword_files=[], userdict_files=[])
    text = "孙新军介绍，北京的垃圾处理能力相对比较宽松，全市有44座处理设施，总设计能力是每天处理3.2万吨，焚烧场11座，处理能力是1.67万吨每天，生化设施23座，日处理能力达8130吨，包括餐饮单位厨余垃圾日处理能力2380吨，家庭厨余垃圾日处理能力5750吨。"
    textrank = seg.extract_keyword(text,algorithm='textrank', use_pos=True)[:10]
    tfidfs = seg.extract_keyword(text,algorithm='tfidf', use_pos=True)[:10]
    print(textrank)
    print(tfidfs)
    print(set(textrank) & set(tfidfs))
