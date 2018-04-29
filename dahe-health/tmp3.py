#coding=utf8
import os
import pandas as pd
import json
import lxml.html as html


php_info = 'if(picResCount>0){\n\t\t\t\t\t\t\t\t\tdocument.getElementById("picres").style.display="block";\n\t\t\t\t\t\t\t\t\tdocument.write("<br>");\n\t\t\t\t\t\t\t\t}'
bugs = ['下一篇', '上一篇', php_info]
datas = []

files = [i for i in os.listdir('data')]
for fpath in files:
     fpath = os.path.join('data', fpath)
     for j in os.listdir(fpath):
         f2 = os.path.join(fpath, j)
         if f2.find('index.htm') > -1:continue
         for k in os.listdir(f2):
             if k.find('htm') > -1:
                 fpath2 = os.path.join(f2, k)
                 f = open(fpath2, encoding='utf8')
                 data = dict()
                 try:
                     dom = html.fromstring(f.read())
                 except Exception as e:
                     print(e)
                     continue
                 data['title'] = "".join(dom.xpath("//title/text()"))
                 content_xpath = '//div[@class="dContents"]//text()'
                 data["content"] = "".join([i.strip() for i in dom.xpath(content_xpath)])
                 for bug in bugs:
                     data["content"] = data["content"].replace(bug, '') 
                 json_fpath = k.replace('.htm', '.json')
                 f2_tmp = open(os.path.join(f2, json_fpath))
                 json_d = json.load(f2_tmp)
                 data['publish_time'] = json_d['publish_time']
                 data['id'] = json_d['id'] 
                 datas.append(data)
df = pd.DataFrame(datas)
df.to_csv('dahe2.csv',encoding='utf8', sep='#', index = False)

