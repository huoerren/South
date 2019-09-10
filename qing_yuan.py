# coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
from urllib import request
from urllib import error

global prefix
prefix = 'http://www.gdqy.gov.cn'

global urls
urls = []

global dataForDb
dataForDb = []


def sendDataToDb(dataToDb):
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306, db='greentest',
                           charset='utf8')
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

            B = cur.execute(sqla, (
            dataToDb[0], dataToDb[1], dataToDb[2], dataToDb[3], dataToDb[4], dataToDb[5], dataToDb[6], dataToDb[7],
            dataToDb[8], dataToDb[9]))
            conn.commit()
            print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None



def getLinks():
    for i in range(1, 5):
        if i == 1:
            url = 'http://www.gdqy.gov.cn/0112/405/list.shtml'
        else:
            url = 'http://www.gdqy.gov.cn/0112/405/list_' + str(i) + '.shtml'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        doc = pq(response.text)

        xxlblbe = doc('.xxlblbe')
        xxlblbe_table = xxlblbe.children('table')
        xxlblbe_table_tr_td_table2 = xxlblbe_table.children('tr').children('td').children('table:nth-child(2)')
        xxlblbe_table_tr_td_table2_tr_td = xxlblbe_table_tr_td_table2.children('tr').children('td')
        xxlblbe_table_tr_td_table2_tr_td_tables = xxlblbe_table_tr_td_table2_tr_td.children('table')
        for table in xxlblbe_table_tr_td_table2_tr_td_tables.items():
            td = table('tr').children('td:nth-child(1)')
            href = td.children('a').attr('href')
            title = td.children('a').attr('title')
            if '行政处罚决定书' in title:
                link = prefix + href
                link = link.replace('../..', '')
                if 'relate:002' not in link:
                    if '.shtml' in link:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
                        }
                        response = requests.get(link, headers=headers)
                        doc_sub = pq(response.text)
                        if doc_sub('#zoom').children().length > 0:
                            dataFlag = getDataFromUrl(link, title)
                            if dataFlag:
                                break
                    else:
                        dataFlag = getDataFromUrl(link, title)
                        if dataFlag:
                            break



def getDataExisted(Area):
    data_For_Compare = []
    sql = 'select Name, AdministrativeNumber,LinkUrl , Area from xingzhengchufa_huanan where  Area = "' + Area + '" '
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


def getDataFromUrl(link, title):

    AdministrativeNumber = ''
    Name = ''
    LinkUrl = link
    Area = '清远市'
    Legal = ''
    CreateDate = ''
    Category = ''
    According = ''
    Measure = ''
    UnifiedSocialCode = ''


    pattern = re.compile(r'清环(罚|法).\d{4}.\d{1,3}号')
    match = pattern.search(title.replace(' ', ''))
    if match:
        AdministrativeNumber = match.group()

    Name = title.replace(' ', '').replace('关于', '').replace(AdministrativeNumber, '').replace('行政处罚决定书', '').replace(
        '－', '').replace('清远市环境保护局', '').replace('（）', '')
    if '英德' not in Name:
        Name = Name.replace('（', '').replace('）', '').replace('(', '').replace(')', '')

    dataFromPage = [Name, AdministrativeNumber,LinkUrl , Area]
    data_For_Compare = getDataExisted('清远市')  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        if Name.strip() != '':
            sendDataToDb(dataToDb)
            return False





getLinks()








