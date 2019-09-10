#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import ssl
from  urllib import  request ,parse


global prefix
prefix = 'http://www.mzepb.gov.cn/'

global urls
urls = []
global urls_2
urls_2 = []


global dataForDb
dataForDb = []
global dataForDb2
dataForDb2 = []



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
    for i in range(1,3):
        url = 'http://www.mzepb.gov.cn/list/index/267/'+str(i)
        doc = pq(url,encoding="utf-8")
        ul = doc('.news ul:nth-child(2)')
        lis = ul.children('li')

        for li in lis.items():
            link = li('a').attr('href')
            title = li('a').attr('title')
            # print([link , title])
            if title != '2016年8月26日以后行政处罚信息':
                dataFlag = getDataFromUrl(link, title)
                if dataFlag:
                    break
            else:
                continue
                # print(link)


def getLinks2():
    url = 'https://www.meizhou.gov.cn/sgs/deptlists?type=xzcf&deptId=007208154'

    for i in range(1,3):
        dictParam={
            'type': 'xzcf',
            'depId':'007208154',
            'page':i,
            'pagesize':10
        }

        data = bytes(parse.urlencode(dictParam),encoding='utf-8')
        page = request.urlopen(url,data)
        html = page.read()
        html = html.decode('utf-8')
        doc = pq(html)
        tr = doc('.xzxx-table tbody tr')
        if tr.length >0:
            for  j in tr.items():
                td = j('td:nth-child(2)')
                link = td('a').attr('href')
                title = td('a').text()
                name = re.search('【(.*?)】',title).group(1)
                dataFlag2 = getDataFromUrl2(link, title)
                if dataFlag2:
                    break

                # cp = [link,name]
                # urls_2.append(cp)


def textHandel(text, flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n', '').replace(' ', '').replace('\xa0', '')
        elif flag == 2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')
    else:
        return None

def getDataExisted(Area):
    data_For_Compare = []
    sql = 'select Name,Category,According,Measure,CreateDate,Area from xingzhengchufa_huanan where  Area = "' + Area + '" '
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

def getDataExisted_2(Area):
    data_For_Compare_2 = []
    sql = 'select LinkUrl,Name,Category,According,Measure,CreateDate,Area from xingzhengchufa_huanan where  Area = "' + Area + '" '
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306, db='greentest',
                           charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for i in result:
            data_For_Compare_2.append(list(i))
    except Exception as e:
        print(str(e))
    return data_For_Compare_2


def getDataFromUrl(link, title):

    LinkUrl = link
    Name = ''
    AdministrativeNumber = ''
    UnifiedSocialCode = ''
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    CreateDate = ''
    Area = '梅州市'

    pattern = re.compile(r'（梅市环罚字.\d{4}.\d{1,2}号）')
    match = pattern.search(title)
    if match:
        AdministrativeNumber = match.group()
    Name = title.replace(AdministrativeNumber, '')

    dataFromPage_2 = [LinkUrl , Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare_2 = getDataExisted_2('梅州市')  # 获得最新的本地域的 已经存在的 数据
    if dataFromPage_2 in data_For_Compare_2:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        if Name.strip() != '':
            sendDataToDb(dataToDb)
            return False

def getDataFromUrl2(link, title):

    LinkUrl = ''
    Name = ''
    Legal = ''
    CreateDate = ''
    Category = ''
    According = ''
    Measure = ''
    AdministrativeNumber = ''
    UnifiedSocialCode = ''
    Area = '梅州市'

    data = []
    dataAvail = []
    page = request.urlopen(link)
    html = page.read()
    html = html.decode('utf-8')
    doc = pq(html)
    trs = doc('.content.infoType-content table tbody').children('tr')
    for tr in trs.items():
        text = tr('td:nth-child(2)').text()
        data.append(text)
    data.append(link)

    Category = data[4]
    According = data[5]
    Measure = data[6]
    Name = data[7]
    Legal = data[9]
    CreateDate = data[10].replace('/', '-')
    LinkUrl = data[17]

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted('梅州市')  # 获得最新的本地域的 已经存在的 数据
    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        sendDataToDb(dataToDb)
        return False



getLinks()

ssl._create_default_https_context = ssl._create_unverified_context

getLinks2()




