#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import re
import time
import argparse

import lxml.html as html
import jieba
import jieba.posseg as pseg
from gensim import corpora, models
from gensim.models import LdaModel
import pyLDAvis
import pyLDAvis.gensim

#这些别改
USER_DICT = './others/user_dict.txt'
STOP_WORD = './others/stop_word.txt'
STOP_WORD_BASE = './others/stop_word_base.txt'
DATA_DIR = './data'
DATA_JSONLINE = './data.jl'


# 这些改
WORD_WITH_POS = True
LDA_TOPIC_NUM = 20

#这些可以改，但是最好啊别改
DICTIONARY_PATH = './models/lda_dictionary.txt'
CORPUS_PATH = './models/lda_corpus.mm'


if not os.path.exists('models'):
    os.mkdir('models')

def parse_args():
    parser = argparse.ArgumentParser(description='LDA for yiran. Jun jie')

    help_ = 'set topic num'
    parser.add_argument('-n', '--tn', default=LDA_TOPIC_NUM, help=help_)

    help_ = 'set pos flag. if filter is 1, then with pos,' \
            ' if 0, without pos. default is 1.'
    parser.add_argument('-f', '--flag', default='1', help=help_)

    help_ = 'set word_cut flag. if filter is 1, then word segment,' \
            ' if 0, no word segment. default is 0.'
    parser.add_argument('-w', '--word', default='0', help=help_)

    args_ = parser.parse_args()
    return args_


def read_stopword():
    '''
    读取停用词，返回一个集合
    '''
    stopword=set()
    with open(STOP_WORD, encoding='utf8') as f:
        for i in f.readlines():
            w = i.strip()
            if w:
                stopword.add(w)
    with open(STOP_WORD_BASE, encoding='utf8') as f:
        for i in f.readlines():
            w = i.strip()
            if w:
                stopword.add(w)
    return stopword


def handle_file(fpath):
    '''
    处理数据，切词返回
    '''
    with open(fpath, encoding='utf8') as f:
        json_data = json.loads(f.read())
        content = json_data["content"]
        content = content.replace('\n','')
        content = content.replace('\r','')
        content = content.replace('\t','')
        content = content.replace(r'\s{2,}','')
        dom = html.fromstring(content)
        content = dom.xpath("//text()")
        cut_word = lambda x: [i for i in pseg.cut(x.strip())]
        result = []
        for i in content:
            cw = cut_word(i)
            if len(cw) > 0:
                result.extend([(w, pos) for w, pos in cw if w.strip()])
        json_data["content"] = result
        return json_data

def word_segments():
    '''
    遍历文件，然后将需要的文件导出来
    '''
    jieba.load_userdict(USER_DICT)
    jl_f = open(DATA_JSONLINE, 'w')
    error_f = open('error.log', 'w')
    for a in os.listdir(DATA_DIR):
        a_p = os.path.join(DATA_DIR, a)
        for b in os.listdir(a_p):
            b_p = os.path.join(a_p, b, 'articles')
            if os.path.exists(b_p):
                for c_p in os.listdir(b_p):
                    if c_p.endswith('.json'):
                        fpath = os.path.join(b_p, c_p)
                        try:
                            datas = handle_file(fpath)
                            datas["path"] = fpath
                            jl_f.write(json.dumps(datas)+'\n')
                        except Exception as e:
                            # print(e, fpath)
                            print(fpath,e, file=error_f)
    
def lda_main(word_with_pos = WORD_WITH_POS, topic_num = LDA_TOPIC_NUM):
    LDA_MODEL = './models/lda_{}.model'.format(topic_num)
    stop_word = read_stopword()
    begin_t = time.time()
    perplexity_f = open('perplexity.txt', 'a')
    def func(line):
        '''
        捆绑词性是否
        '''
        line = line.strip()
        json_data = json.loads(line)
        content = json_data['content']
        if word_with_pos:
            word_list = [j[0] + j[1] for j in content if j[0] not in stop_word]
        else:
            word_list = [j[0]for j in content if j[0] not in stop_word]
            
        return word_list
    
    with open(DATA_JSONLINE) as f:
        
        # words = [func(i) for i in f.readlines()]
        words = []
        for i in f.readlines():
            words.append(func(i))
        print('数据装载完毕！ use ', time.time()-begin_t, 'sec.\n begin lda modeling')
        dic = corpora.Dictionary(words)
        corpus = [dic.doc2bow(text) for text in words]
        dic.save(DICTIONARY_PATH)
        corpora.MmCorpus.serialize(CORPUS_PATH, corpus)
        lda = LdaModel(corpus=corpus, id2word=dic, num_topics=topic_num)
        lda.save(LDA_MODEL)
        print(topic_num, ',', lda.log_perplexity(corpus), file=perplexity_f)
        vis_data = pyLDAvis.gensim.prepare(lda, corpus, dic)
        vis_html_path = 'ldavis_{}.html'.format(topic_num)
        pyLDAvis.save_html(vis_data, vis_html_path)
        print('LDA 建模完成!\nTotal use:', time.time()- begin_t, 'sec.')

def main2():
    for topic_num in range(100, 101):
        lda_main(False, topic_num=topic_num)

def main():
    main2()

if __name__ == "__main__":
    main()
