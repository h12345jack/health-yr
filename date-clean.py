#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import re
import time

import requests
import lxml
import lxml.html as html
from multiprocessing.dummy import Pool as Threadpool


def get_img(f_name = './data/2010-05-13/01：头版/articles/11981.html'):
    with open(f_name) as f:
        content  = f.read()
        img_path = '//map/../img/@src'
        dom = html.fromstring(content)
        img = dom.xpath(img_path)
        f_path = f_name[:f_name.rfind('articles')] 
        img_dir = os.path.join(f_path, 'imgaes')
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)

        if len(img) > 0:
            img_url = "http://www.jksb.com.cn/" + img[0]
            img_path = os.path.join(img_dir, img[0][img[0].rfind('/')+1:])
            if not os.path.exists(img_path):
                with open(img_path, 'wb') as f:
                    f.write(requests.get(img_url).content)
                print(img_path, 'download!')

def loop_dir(data_dir = 'data'):
    f_list = []
    for date in os.listdir(data_dir):
        date_dir = os.path.join(data_dir, date)
        for channel in os.listdir(date_dir):
            if not channel.startswith('.'):
                articles_dir = os.path.join(date_dir, channel, 'articles')
                for f_name in os.listdir(articles_dir):
                    if f_name.endswith('.html'):
                        f_list.append(os.path.join(articles_dir, f_name))
    return f_list



def main():
    f_list = loop_dir()
    # f_list = f_list[:1]
    # print(f_list)
    pool = Threadpool(8)
    pool.map(get_img, f_list)
    pool.close()

if __name__ == '__main__':
    main()

