# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yin Yu Fei
# Github: https://github.com/
# CreatDate: 2022-05-10 9:57
# Description:
import re
import requests
"""
1.下列程序段运⾏后，输出 C
String str = “123az45d67xyz89”;
str = str.replaceAll("[a-z]+", “***”);
System.out.println(str);
A.123az45d67xyz89
az***d***xyz
B.
C.123***45***67***89
D.123456789
"""
String_str = "123az45d67xyz89"
pattern = re.compile(r'[1-9]+[a-z]*')
result = pattern.findall(String_str)
print(result)

url_ture = "https://www.csdn.net/"
url_false = "ftp://110.110.110.110:8080"

pattern = re.compile(r'[a-zA-Z]{3,5}://\w*\.\w*\.\w+')
print(pattern.findall(url_false))

# 2.匹配由单个空格分隔的任意单词对，也就是姓和名

s = "Han meimei, Li lei, Zhan san, Li si"
pattern = re.compile(r'[a-zA-Z]+ [a-zA-Z]+,*')
print(pattern.findall(s))

# 3. 匹配由单个逗号和单个空白符分隔的任何单词和单个字母,如姓氏的首字母

s = "yu, Guan  bei, Liu  fei, Zhang"
pattern = re.compile(r'([a-zA-Z]+),\s([a-zA-Z])')
print(pattern.findall(s))

# 5. 根据美国街道地址格式,匹配街道地址。
# 美国接到地址使用如下格式:1180 Bordeaux Drive。
# 使你的正则表达式足够灵活,以支持多单词的街道名称,如3120 De la Cruz Boulevard

s = """street 1: 1180  Bordeaux Drive,"
    street 1: 3120 De la Cruz Boulevard"""
print (re.search(r'1:\s+\d+(\s+[a-zA-Z]+)',s))

# 6. 匹配以“www”起始且以“.com”结尾的简单Web域名:例如,http://www.yahoo.com ，也支持其他域名，如.edu .net等

s = "http://www.yahoo.com        www.foothill.edu"
pattern = re.compile(r'www\.\w+\.\w+')
print(pattern.findall(s))

# 7. 匹配所有能够表示Python整数的字符串集

s = '520a1    20L 0  156   -8 -10a  A58'
pattern = re.compile(r'\w?-?\d+\w?')
print(pattern.findall(s))

# 14、 只匹配包含字母和数字的行

s = "nihao fsadf\n \
789! 3asfd 1\n \
fds12df e4 4564"
pattern = re.compile(r'^([a-zA-Z\d ]+)$')
print(re.findall(r'^([a-zA-Z\d ]+)$',s,re.M))

# 15、提取每行中完整的年月日和时间字段

s="""time 1988-01-01 17:20:10 fsadf 2018-02-02 02:29:01"""
pattern = re.compile(r'[12]\d{3}-[01]\d-[0-3]\d\s+[0-2]\d:[0-6]\d:[0-6]\d')
print(pattern.findall(s))

# 2、匹配一行文字中的所有开头的数字内容

s = "i love you not because 12sd 34er 56df e4 54434"

if __name__ == '__main__':
    url = "http://www.baidu.com"
    response = requests.get(url=url)
    page_text = response.text
    print(page_text)



