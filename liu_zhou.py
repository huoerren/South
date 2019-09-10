#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.lzepb.gov.cn/'

global unfit_urls
unfit_urls = []


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
    for i in range(1,10):
        url = 'http://www.lzepb.gov.cn/xzcfxzfy.aspx?page='+str(i)
        doc = pq(url,encoding='utf-8')
        ul = doc('.news_txt')
        lis = ul.children('li')
        for li in lis.items():
            title = li('a').attr('title')
            if '行政处罚决定书' in title:
                link = prefix + li('a').attr('href')
                dataFlag = getDataFromUrl(link, title)
                if dataFlag:
                    break


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




def getDataFromUrl(link, title):

    LinkUrl = link
    Name = ''
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = ''
    Area = '柳州市'

    pattern2 = re.compile(r'柳环罚字.\d{4}.\d{1,2}号')
    match2 = pattern2.search(title)
    AdministrativeNumber = match2.group()

    Name_Category = title.split(AdministrativeNumber)[1]

    pattern3 = re.compile(r'-{1,3}')
    match3 = pattern3.search(Name_Category)
    splitModel = match3.group()

    Name = Name_Category.split(splitModel)[0]
    Category = Name_Category.split(splitModel)[1]
    Category = Category[0:len(Category) - 1]

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted('柳州市')  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        if Name.strip() != '':
            sendDataToDb(dataToDb)
            return False

    # data = [LinkUrl, Name, Legal, Category, According, Measure, UnifiedSocialCode, CreateDate, AdministrativeNumber, Area]
    # 'LinkUrl , Name,Legal,Category,According,Measure,UnifiedSocialCode ,CreateDate,AdministrativeNumber,Area'

    # print(data)
    # dataForDb.append(data)



getLinks()








































