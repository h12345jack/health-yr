#coding=utf8
import os
import pandas as pd
import json
import lxml.html as html

datas = []
files = [i for i in os.listdir('data')]
for fpath in files:
     if fpath.find('.html') > -1: continue
     fpath = os.path.join('data', fpath)
     for j in os.listdir(fpath):
         f2 = os.path.join(fpath, j)
         if f2.find('.htm') > -1:continue
         f = open(f2)
         con = f.read()
         json_data = json.loads(con)
         content = html.fromstring(json_data["content"])
         json_data['content'] = "".join([i.strip() for i in content.xpath('//text()')])
         datas.append(json_data)
df = pd.DataFrame(datas)
df.to_csv('lifetimes.csv',encoding='utf8', sep='#', index = False)

