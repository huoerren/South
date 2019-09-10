#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import random


global prefix
prefix = 'http://www.gdzjepb.gov.cn'

global urls
urls = []


global dataForDb
dataForDb = []


def sendDataToDb(dataToDb):
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306,db='greentest',charset='utf8')
    cur = conn.cursor()
    if dataToDb != None:
        try:
            print(dataToDb[0])
            sqla = '''
                    insert into  xingzhengchufa_huanan(
                            LinkUrl,Name,Legal,CreateDate,Category,According,Measure,AdministrativeNumber,UnifiedSocialCode,Area
                         ) 
                    values
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                '''
            B = cur.execute(sqla,(dataToDb[0],dataToDb[1],dataToDb[2],dataToDb[3],dataToDb[4],dataToDb[5],dataToDb[6],dataToDb[7],dataToDb[8],dataToDb[9]))
            conn.commit()
            print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None


def getLinks():
    url = 'http://www.gdzjepb.gov.cn/home/special/get_list/id/25.html'
    doc = pq(url,encoding="utf-8")
    ul = doc('#news_list li')
    for li in ul.items():
        link = prefix + li('a').attr('href')
        title = li('a').attr('title')
        if  '处罚决定书' in  title:
            sub_title = title.split('处罚决定书')[1]
            Name = sub_title[1:len(sub_title)-1]
            dataFlag = getDataFromUrl(link,Name)
            if dataFlag:
                break


def textHandel(text,flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')
        elif flag ==2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')


def getDataExisted(Area):
    data_For_Compare = []
    sql = 'select Name,Category,According,Measure,CreateDate,Area from xingzhengchufa_huanan where  Area = "'+ Area +'" '
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306, db='greentest', charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for i in result:
            data_For_Compare.append(list(i))
    except Exception as e:
        print(str(e))
    return data_For_Compare




def getDataFromUrl(link,Name):
    doc = pq(link , encoding="utf-8")
    content = textHandel(doc('#news_content').text(),1)
    content_02 = textHandel(doc('#news_content').text(),2)

    LinkUrl = link
    Name = Name
    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = ''
    Legal = ''
    Category = ''
    According = ''
    Measure = ''
    Area = '湛江市'

    pattern = re.compile(r'\d{4}年\d{0,2}月\d{0,2}日')
    if '湛江市环境保护局' in content:
        jieshu = content.split('湛江市环境保护局')[-1]
    if '年' in jieshu and '月' in jieshu and '日' in jieshu:
        match = pattern.search(jieshu)
        if match:
            CreateDate = match.group().replace('年','-').replace('月','-').replace('日','')

    pattern2 = re.compile(r'湛环罚字.\d{4}.\d{0,3}号{0,1}')
    match2 = pattern2.search(content)
    if match2:
        AdministrativeNumber = match2.group()

    if '统一社会信用代码' in content_02:
        UnifiedSocialCode = re.search('统一社会信用代码.(.*?)\n', content_02).group(1)

    if '法定代表人' in content_02:
        Legal = re.search('法定代表人.(.*?)\n', content_02).group(1)


    if '一、环境违法事实和证据' in content and '以上事实' in content:
        Category = re.search('一、环境违法事实和证据(.*?)以上事实', content).group(1)

    if '二、行政处罚的依据和种类' in content and '我局决定对' in content:
        According = re.search('二、行政处罚的依据和种类(.*?).我局决定对', content).group(1)

    if '我局决定' in content and '的行政处罚。' in content:
        Measure = re.search('我局决定(.*?)的行政处罚。', content).group(1)

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted('湛江市')  # 获得最新的本地域的 已经存在的 数据
    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        sendDataToDb(dataToDb)
        return False


getLinks()




