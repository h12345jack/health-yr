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

import threading


from multiprocessing.dummy import Pool as Threadpool

lock1 = threading.Lock()

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
    "Host": "newpaper.dahe.cn",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
# Accept: 
# Accept-Encoding: gzip, deflate
# Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
# Cache-Control: no-cache
# Connection: keep-alive
# Cookie: Hm_lvt_5c23145ed8ee138c73ce6eaafd2c33ae=1524066904; Hm_lpvt_5c23145ed8ee138c73ce6eaafd2c33ae=1524914527
# Host: newpaper.dahe.cn
# Pragma: no-cache
# Referer: http://newpaper.dahe.cn/dhjkb/html/2017-02/03/node_147.htm
# User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36
# X-Prototype-Version: 1.5.0_rc0
# X-Requested-With: XMLHttpRequest

def get_nodes():
    '''
    获取period.xml，然后获取需要抓取的时间
    输出dates.txt
    '''
    paper_urls = []
    url = 'http://newpaper.dahe.cn/dhjkb/html/{}/period.xml'
    for year in range(2006, 2019):
        for m in range(1, 13):
            # year = 2018
            # m = 2
            date_time = str(year) + '-' + str(m).rjust(2, '0')
            xml_url = url.format(date_time)
            req = requests.get(xml_url, headers = HEADERS)
            try:
                root = etree.fromstring(req.content)
                period_date = root.xpath('//period_name/text()')
                front_pages = root.xpath('//front_page/text()')
                for front_page, period_date in zip(front_pages, period_date):
                    index = period_date.rfind('-')
                    y1 = period_date[:index]
                    m1 = period_date[index+1:]
                    paper_url = 'http://newpaper.dahe.cn/dhjkb/html/{}/{}/{}'.format(y1, m1, front_page)
                    paper_urls.append(paper_url)
                    print(paper_url)
                # print(paper_url)
            except lxml.etree.XMLSyntaxError as e:
                print(req.content)
            
    with open(DATE_LIST_FILE, 'w') as f:
        for url in paper_urls:
            print(url, file=f)

def crawl_date(url):
    req = requests.get(url ,headers = HEADERS)
    date_dir = url[url.rfind('html') + 5:url.rfind('/')].replace('/', '-')
    publish_time = date_dir
    date_dir = os.path.join(DATA_DIR, date_dir)
    if not os.path.exists(date_dir):
        os.mkdir(date_dir)
    dom = html.fromstring(req.text)
    with open(date_dir+'/index.htm', 'w') as f:
        f.write(str(req.content, 'utf8'))
    banben_xpath = '//tbody//a[@id="pageLink"]/@href'
    banben_urls = set()
    for banben_url in dom.xpath(banben_xpath):
        if banben_url.find('/') == -1:
            banben_urls.add(banben_url)

    for banben_url in banben_urls:
        fpath = os.path.join(date_dir, banben_url[:banben_url.rfind('.')])
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        banben_url = url[:url.rfind('/')] + '/' + banben_url
        req = requests.get(banben_url)
        dom = html.fromstring(req.text)
        detail_url = '//div[@class="dConL"]//tbody//td[@valign]/a/@href'
        for detail_url in dom.xpath(detail_url):
            id = "".join(re.findall('[0-9]+', detail_url))
            
            detail_path = os.path.join(fpath, detail_url)
            detail_url = banben_url = url[:url.rfind('/')] + '/' + detail_url
            print(detail_url)
            req = requests.get(detail_url, headers =HEADERS)
            with open(detail_path, 'w', encoding='utf8') as f:
                try:
                    f.write(str(req.content, 'utf8'))
                except UnicodeDecodeError as e:
                    print(req.text)
            data = dict()
            dom2 = html.fromstring(req.text)
            data["id"] = id
            content_xpath = '//div[@class="dContents"]'
            data["title"] = "".join(dom2.xpath('//title/text()'))
            data["publish_time"] = publish_time
            for content in dom2.xpath(content_xpath):
                data["content"] = html.tostring(content, encoding='utf-8').decode('utf8')
                break     
            with open(detail_path.replace('.htm', '.json'), 'w') as f:
                f.write(json.dumps(data))




    # for banben_url in banben_urls
    #     req = requests.get(banben_url)
    #     detain_url = '//tbody//td[@class="black"]/a/@href'
    #     data["id"] = id
    #     data["title"] = "".join(dom.xpath(title_xpath))
    #     data["author"] = "".join(dom.xpath(author_xpath))
    #     data["publish_time"] = "".join(dom.xpath(publish_time_xpath))
    #     data["content"] = html.tostring(dom.xpath(content_xpath)[0], encoding='utf-8').decode('utf8')
    #     data["view_times"] = view_times

def main():
    # get_nodes()
    with open('dates.txt') as f:
        for url in f.readlines():
            time.sleep(1)
            # url = 'http://newpaper.dahe.cn/dhjkb/html/2011-10/11/node_364.htm'
            crawl_date(url.strip())

if __name__ == "__main__":
    main()

