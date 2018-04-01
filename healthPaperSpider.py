#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import json
import re


import requests
import lxml
import lxml.html as html

DATE_DONE = './dates_done.txt'
DATE_LIST_FILE = './dates.txt'
COOKIES_RAW = './cookies.txt'
DATA_DIR = './data'

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "www.jksb.com.cn",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
}

class healthPaperSpider(object):
    """docstring for healthPaperSpider"""
    def __init__(self):
        self.spider  = requests.Session()
        self.spider.headers = HEADERS
        cookies = self.read_cookies()
        requests.utils.add_dict_to_cookiejar(self.spider.cookies, cookies)

    def read_dates(self, filename):
        dates = []
        with open(filename) as f:
            for line in f.readlines():
                dates.append(line.strip())
        return dates


    def read_cookies(self):
        '''make cookies raw to a json'''
        with open(COOKIES_RAW) as f:
            line=f.readline()
            line=line.split(';')
            cookies=dict()
            for i in line:
                index=i.find('=')
                value=i[index+1:].strip()
                value=value.replace('"','')
                cookies[i[:index].strip()]=value
        return cookies     

    def scrapy_article(self, url_prefix, url_last_path, dir_path):
        '''抓取页面数据，主要包括的字段是title，作者，发布时间，查看次数，正文'''

        url = url_prefix + url_last_path
        req = self.spider.get(url)
        dom = html.fromstring(req.text)

        title_xpath = '//td[@class="title"]/text()'
        author_xpath = '//td[@class="title"]/..//following-sibling::tr[1]/text()'
        publish_time_xpath = '//td[@class="title"]/..//following-sibling::tr[2]/text()'
        content_xpath = '//div[@class="PaperT"]'

        id = "".join(re.findall('[0-9]+',url_last_path))
        
        raw_html = os.path.join(dir_path, id + '.html')
        with open(raw_html, 'w') as f:
            f.write(req.text)

        viwes_url = 'http://www.jksb.com.cn/newspaper/Include/Hits.php?ID={}'.format(id)
        req = self.spider.get(viwes_url)
        view_times = "".join(re.findall('[0-9]+', req.text))
        

        data = dict()
        data["id"] = id
        data["title"] = "".join(dom.xpath(title_xpath))
        data["author"] = "".join(dom.xpath(author_xpath))
        data["publish_time"] = "".join(dom.xpath(publish_time_xpath))
        data["content"] = html.tostring(dom.xpath(content_xpath)[0], encoding='utf-8').decode('utf8')
        data["view_times"] = view_times

        filename = os.path.join(dir_path, id+'.json')
        with open(filename, 'w') as f:
            f.write(json.dumps(data))

    def scrapy_chapter(self, url_prefix, url_last_path, channel, html_dir_path):
        '''
        该日期的章节
        url_prefix 包含日期
        url_last_path 具体到html,
        channel  是什么板块
        '''

        data_dir = os.path.join(html_dir_path, channel)
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        
        url = url_prefix + url_last_path
        req = self.spider.get(url)
        content = req.text

        filename = os.path.join(data_dir, url_last_path)
        # save index.html of channel
        with open(filename, 'w') as f:
                f.write(content)

        dom = html.fromstring(content)
        articles_xpath = '//div[@class="PaperB"]/table//td/a/@href'
        article_dir = os.path.join(data_dir, 'articles')
        
        if not os.path.exists(article_dir):
            os.mkdir(article_dir)

        for article in dom.xpath(articles_xpath):
            url_prefix = url_prefix
            url_last_path = article
            dir_path = article_dir

            self.scrapy_article(url_prefix, url_last_path, dir_path)
            
            time.sleep(0.2)


    def scrapy(self, date):
        '''爬去一个日期的开始'''
        url_prefix = 'http://www.jksb.com.cn/newspaper/Html/{}/'.format(date)
        url = url_prefix + 'Qpaper.html'

        req = self.spider.get(url)
        content = req.text
        channel_xpath = '//div[@class="Paper"]//td'
        dom = html.fromstring(content)

        date_dir_path = os.path.join(DATA_DIR, date)
        if not os.path.exists(date_dir_path):
            os.mkdir(date_dir_path)

        for channel in dom.xpath(channel_xpath):

            url_last_path = ''.join(channel.xpath('./a/@href'))
            channel = channel.xpath('./a/text()')[0]
            html_dir_path = date_dir_path
            print(url_prefix, url_last_path, channel, html_dir_path)
            self.scrapy_chapter(url_prefix, url_last_path, channel, html_dir_path)
            time.sleep(0.1)

    def run(self):
        ''' 爬虫总控制 '''
        dates = self.read_dates(DATE_LIST_FILE)
        dates_done = self.read_dates(DATE_DONE)
        dates = set(dates) - set(dates_done)
        dates = sorted([i for i in list(dates) if len(i) > 0])
        # print(dates)
        f = open(DATE_DONE, 'a')
        for date in dates:
            try:
                self.scrapy(date)
                print(date, file=f)
            except Exception as e:
                print(e)



def main():
    spider = healthPaperSpider()
    spider.run()


if __name__ == "__main__":
    main()

