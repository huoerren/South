#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.gxhchb.gov.cn/zwxx/hjwfbgt'

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
    url = 'http://www.gxhchb.gov.cn/zwxx/hjwfbgt/'
    doc = pq(url,encoding='utf-8')
    ul = doc('.list-ctn ul')
    lis = ul.children('li')
    for i in lis.items():
        link = prefix + i.children('a').attr('href')[1:]
        title = i.children('a').text()
        dataFlag = getDataFromUrl(link, title)
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


def getDataFromUrl(link, title):
    doc = pq(link, encoding='utf-8')
    content = textHandel(doc('.tb-inner').text(),1)
    if '行政处罚决定书' in content:
        LinkUrl = link
        Name = ''
        Legal = ''

        Category = ''
        According = ''
        Measure = ''

        UnifiedSocialCode = ''
        CreateDate = ''
        AdministrativeNumber = ''
        Area = '河池市'

        pattern = re.compile(r'河环罚字.\d{4}.\d{1,2}号')
        match = pattern.search(content)
        if match:
            AdministrativeNumber = match.group()
            if '统一社会信用' in content:
                Name = re.search(AdministrativeNumber + '(.*?)统一社会信用', content).group(1)
                Name = Name.replace('：', '')
        if Name.strip() == '':
            Name = doc('.ctn-tab h1').text().replace('行政处罚决定书', '').replace('关于', '').replace('未依法公开环境信息', '')

        if '一、环境违法事实、证据和陈述申辩及采纳情况' in content and '以上事实' in content:
            Category = re.search('一、环境违法事实、证据和陈述申辩及采纳情况(.*?)以上事实', content).group(1)
        elif '一、环境违法事实、证据和陈述申辩及采纳情况' in content and '以上违法事实' in content:
            Category = re.search('一、环境违法事实、证据和陈述申辩及采纳情况(.*?)以上违法事实', content).group(1)

        if '三、行政处罚决定' in content and '的规定' in content:
            According = re.search('三、行政处罚决定(.*?)的规定.', content).group(1)

        if '处以' in content and '罚款' in content:
            Measure = re.search('处以(.*?)罚款', content).group(0)



        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted('河池市')  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
            if Name.strip() != '':
                sendDataToDb(dataToDb)
                return False


getLinks()











































