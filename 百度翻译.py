# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yin Yu Fei
# Github: https://github.com/
# CreatDate: 2022-05-11 14:07
# Description:

import requests,json

if __name__ == '__main__':
    url = 'https://fanyi.baidu.com/sug'
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4089.0 Safari/537.36'
    }
    kw = input('Enter a word : ')
    data = {
        'kw' : kw
    }
    response = requests.post(url=url,data=data,headers = headers)
    json_obj = response.json()
    fileName = kw + '.json'
    fp = open(fileName, 'w' ,encoding='utf-8')
    json.dump(json_obj, fp=fp,ensure_ascii=False,indent=4)