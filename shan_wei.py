#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import random


global prefix
prefix = 'http://www.shanwei.gov.cn/'

global urls
urls = []


global dataForDb
dataForDb = []


def sendDataToDb():
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306,db='greentest',charset='utf8')
    cur = conn.cursor()

    if len(dataForDb) >0:
        try:
            for g in dataForDb:
                print(g[0])
                sqla = '''
                        insert into  xingzhengchufa_huanan(
                                LinkUrl,Name,Legal,CreateDate,Category,According,Measure,AdministrativeNumber,UnifiedSocialCode,Area
                             ) 
                        values
                            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                    '''

                B = cur.execute(sqla,(g[0],g[1],g[2],g[3],g[4],g[5],g[6],g[7],g[8],g[9]))
                conn.commit()
                print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None


def getLinks():
    for i in range(1,12):
        if i == 1:
            url = 'http://www.shanwei.gov.cn/swzdly/hjbh08/swlist2.shtml'
        else:
            url = 'http://www.shanwei.gov.cn/swzdly/hjbh08/swlist2_'+str(i)+'.shtml'

        doc = pq(url,encoding="utf-8")
        divs = doc('.list-right_title.fon_1')
        for i in divs.items():
            link  = prefix + i('a').attr('href')
            dataFlag = getDataFromUrl(link)
            if dataFlag:
                break


def textHandel(text, flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n', '').replace(' ', '').replace('\xa0', '')
        elif flag == 2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')


def getDataExisted(Area):
    data_For_Compare = []
    sql = 'select Name,Category,According,Measure,CreateDate,Area from xingzhengchufa_huanan where  Area = "' + Area + '" '
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306, db='greentest',
                           charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for i in result:
            data_For_Compare.append(list(i))
    except Exception as e:
        print(str(e))
    return data_For_Compare




def getDataFromUrl(link):

    LinkUrl = ''
    Name = ''
    AdministrativeNumber = ''
    UnifiedSocialCode = ''
    Legal = ''
    Category = ''
    According = ''
    Measure = ''

    Area = '汕尾市'
    CreateDate = ''


getLinks()






