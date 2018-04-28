#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import json
import re


import requests
import lxml
import lxml.html as html
from lxml import etree


DATE_DONE = './dates_done.txt'
DATE_LIST_FILE = './dates.txt'
COOKIES_RAW = './cookies.txt'
DATA_DIR = './data'

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

HEADERS = {
    "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
}


def main():
    url = 'http://survey.huanqiu.com/app/smsblist.php?&paperId=5ab06b1704a6e3536326027d&no={}'
    url2 = 'http://survey.huanqiu.com/app/smsb.php?&articleId={}'
    done_f = open(DATE_DONE, 'a')
    for i in range(1, 1210):
        url = url.format(i)
        req = requests.get(url, headers=HEADERS)
        content = req.text
        html_content = content[content.find('(')+1 : content.rfind(')')]
        js_data = json.loads(html_content)
        with open(os.path.join(DATA_DIR, '{}.html'.format(i)), 'w') as f:
            f.write(js_data)
        dom = html.fromstring(js_data)
        fpath = os.path.join(DATA_DIR, str(i))
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        urls = set(dom.xpath('//td/a/@href'))
        for url in urls:
            articleId = url[url.rfind('articleId') + len('articleId='):]
            article_url = url2.format(articleId)
            print(article_url)
            req = requests.get(article_url, headers=HEADERS)
            content = req.text
            html_content = content[content.find('(')+1 : content.rfind(')')]
            js_data = json.loads(html_content)
            detail_path = os.path.join(fpath, articleId + '.htm')
            with open(detail_path, 'w') as f:
                f.write(js_data)
            dom2 = html.fromstring(js_data)

            data = dict()
            data["id"] = articleId
            content_xpath = '//div[@class="textCon"]'
            data["title"] = "".join(dom2.xpath('//title/text()'))
            data["publish_time"] = "".join(dom2.xpath('//div[@class="topLeft2"]/text()')).strip()
            for content in dom2.xpath(content_xpath):
                data["content"] = html.tostring(content, encoding='utf-8').decode('utf8')
                break     
            with open(detail_path.replace('.htm', '.json'), 'w') as f:
                f.write(json.dumps(data))
            time.sleep(0.1)
        print(i, file=done_f)
        time.sleep(2)

if __name__ == '__main__':
    main()