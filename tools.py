#coding=utf8
import json
import re
import os

import lxml.html as html

from collections import defaultdict

import jieba
import jieba.analyse
#这些别改
USER_DICT = './others/user_dict.txt'
STOP_WORD = './others/stop_word.txt'
STOP_WORD_BASE = './others/stop_word_base.txt'
DATA_DIR = './data'
DATA_JSONLINE = './data.jl'


def statistic_place():
    place_dict = defaultdict(int)
    with open('data.jl') as f:
        for line in f.readlines():
            json_data = json.loads(line)
            content = json_data['content']
            for w, pos in content:
                if pos == 'ns':
                    place_dict[w] +=1
    result = sorted(place_dict.items(), key = lambda x:x[1], reverse=True)
    for i in result:
        print(i[0], i[1])


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
        content = "".join([i for i in dom.xpath("//text()")])
        keyword_list = jieba.analyse.textrank(content, allowPOS=('ns', 'n'))
        return keyword_list
        # cut_word = lambda x: [i for i in jieba.analyse.textrank(content, allowPOS=('ns', 'n'))]
        # result = []
        # for i in content:
            # cw = cut_word(i)
            # if len(cw) > 0:
                # result.extend([(w, pos) for w, pos in cw if w.strip()])
        # json_data["content"] = result
        # return json_data

def keyword_extract():
    '''
    遍历文件，然后将需要的文件导出来
    '''
    jieba.load_userdict(USER_DICT)
    jl_f = open('data2.txt', 'w')
    error_f = open('error.log', 'w')
    word_dict = defaultdict(int)
    for a in os.listdir(DATA_DIR):
        a_p = os.path.join(DATA_DIR, a)
        for b in os.listdir(a_p):
            b_p = os.path.join(a_p, b, 'articles')
            if os.path.exists(b_p):
                for c_p in os.listdir(b_p):
                    if c_p.endswith('.json'):
                        fpath = os.path.join(b_p, c_p)
                        keyword_list = handle_file(fpath)
                        print(c_p, '#', ",".join(keyword_list), file=jl_f)
                        for w in keyword_list:
                            word_dict[w] +=1


    result = sorted(word_dict.items(), key = lambda x:x[1], reverse=True)
    for i in result:
        print(i[0], i[1])
                        # try:
                        #     datas = handle_file(fpath)
                        #     datas["path"] = fpath
                        #     jl_f.write(json.dumps(datas)+'\n')
                        # except Exception as e:
                        #     # print(e, fpath)
                        #     print(fpath,e, file=error_f)


def main():
    # statistic_place()
    # handle_file('./data/2010-05-13/01：头版/articles/11981.json')
    keyword_extract()

if __name__ == '__main__':
    main()