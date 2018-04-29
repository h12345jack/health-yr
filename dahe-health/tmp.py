#coding=utf8
import os
files = [i for i in os.listdir('data')]
for fpath in files:
     fpath = os.path.join('data', fpath)
     for j in os.listdir(fpath):
         f2 = os.path.join(fpath, j)
         if f2.find('index.htm') > -1:continue
         for k in os.listdir(f2):
             if k.find('?') != -1:
                 old = os.path.join(f2, k)
                 new = old[:old.rfind('?')]
                 os.rename(old, new)
                 print(old, new)


