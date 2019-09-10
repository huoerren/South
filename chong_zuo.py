#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix_1
prefix_1 = 'http://www.gxczhb.gov.cn'  # ../../

global predix_2
predix_2 = 'http://www.gxczhb.gov.cn/xxgk/hjzf'

global unfit_urls
unfit_urls = []


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
                        LinkUrl,Name,Legal,Category,According,Measure,UnifiedSocialCode,CreateDate,AdministrativeNumber,Area
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
    for i in range(0,6):
        if i == 0:
            url = 'http://www.gxczhb.gov.cn/xxgk/hjzf/index.html'
        else:
            url = 'http://www.gxczhb.gov.cn/xxgk/hjzf/index_'+str(i)+'.html'

        doc = pq(url,encoding='utf-8')
        ul = doc('.list-ctn ul')
        lis = ul.children('li')
        for li in lis.items():
            title = li.children('a').text()
            link = ''
            Name = ''
            if '行政处罚决定书' in title:
                href = li.children('a').attr('href')
                if '../..' in href:
                    link = prefix_1 + href.replace('../..','')
                else:
                    link = predix_2 + href[1:]

                pattern = re.compile(r'（.*?）')
                match = pattern.search(title)
                if match:
                    Name = match.group()

                pattern2 = re.compile(r'\(.*?\)')
                match2 = pattern2.search(title)
                if match2:
                    Name = match2.group()

                if Name.strip() != '':
                    Name_sub = Name
                    Name = Name[1:len(Name_sub)-1]


                dataFlag = getDataFromUrl(link,Name,title)
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


def getDataFromUrl(link,Name,title):
    LinkUrl = link
    Name = Name
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = ''

    Area = '崇左市'

    doc = pq(link, encoding='utf-8')
    content = doc('.tb-inner').text().replace('\n', '').replace(' ', '').replace('\xa0', '')
    div = doc('.auto')
    table = div.children('table')
    tr = table.children('tr:nth-child(3)')
    td = tr.children('td:nth-child(2)').text()
    AdministrativeNumber = td.replace('【', '〔').replace('】', '〕').replace('[', '〔').replace(']', '〕')

    if AdministrativeNumber.strip() == '':
        pattern = re.compile(r'崇环罚字.\d{4}.\d{1,3}号')
        match = pattern.search(content)
        if match:
            AdministrativeNumber = match.group()

    a_s = doc('.tb-inner').children('a')

    content = doc('.tb-inner').text().replace('\n', '').replace(' ', '').replace('\xa0', '')

    if '一、环境违法事实和证据' in content and '以上行为' in content:
        Category = re.search('一、环境违法事实和证据(.*?)以上行为', content).group(1)
    elif '一、环境违法事实和证据' in content and '以上违法事实' in content:
        Category = re.search('一、环境违法事实和证据(.*?)以上违法事实', content).group(1)
    elif '一、环境违法事实与证据' in content and '以上违法事实' in content:
        Category = re.search('一、环境违法事实与证据(.*?)以上违法事实', content).group(1)
    elif '一、环境违法事实与证据' in content and '认定以上' in content:
        Category = re.search('一、环境违法事实与证据(.*?)认定以上', content).group(1)
    elif '以下环境违法行为' in content and '以上事实' in content:
        Category = re.search('以下环境违法行为.(.*?)以上事实', content).group(1)
    elif '审查终结' in content and '以上事实' in content:
        Category = re.search('审查终结.(.*?)以上事实', content).group(1)

    if '依据' in content and '的规定' in content:
        According = re.search('依据(.*?)的规定', content).group(1)

    if '如下行政处罚' in content and '限于接到' in content:
        Measure = re.search('如下行政处罚.(.*?)限于接到', content).group(1)
    elif '我局决定如下' in content and '三、行政处罚的履行方式和期限' in content:
        Measure = re.search('我局决定如下.(.*?)三、行政处罚的履行方式和期限', content).group(1)
    elif '我局决定' in content and '三、行政处罚的履行方式和期限' in content:
        Measure = re.search('我局决定(.*?)三、行政处罚的履行方式和期限', content).group(1)
    elif '我局决定：' in content and '根据《' in content:
        Measure = re.search('我局决定：(.*?)根据《', content).group(1)
    elif '以上合并' in content and '根据《' in content:
        Measure = re.search('以上合并(.*?)根据《', content).group(1)

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted('崇左市')  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        if Name.strip() != '':
            sendDataToDb(dataToDb)
            return False



getLinks()

# getDatas()

# sendDataToDb()












































