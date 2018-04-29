#coding=utf8
import os
import pandas as pd
import json
import lxml.html as html

datas = []
files = [i for i in os.listdir('data')]
for fpath in files:
     fpath = os.path.join('data', fpath)
     for j in os.listdir(fpath):
         f2 = os.path.join(fpath, j)
         if f2.find('index.htm') > -1:continue
         for k in os.listdir(f2):
             if k.find('json') > -1:
                 fpath2 = os.path.join(f2, k)
                 f = open(fpath2)
                 con = f.read()
                 print(con.decode('utf8'))
                 json_data = json.loads(con.encode('utf8'))
                 #print(json_data["content"])
                 content = html.fromstring(json_data["content"])
                 json_data['content'] = "".join([i.strip() for i in content.xpath('//text()')])
                 datas.append(json_data)
         break
     break
df = pd.DataFrame(datas)
print(df)
df.to_csv('dahe2.csv',encoding='utf8', sep='#', index = False)

