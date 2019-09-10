#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix_1
prefix_1 = 'http://baise.gxepb.gov.cn/hjzf/xzcf'  # ../../

global predix_2
predix_2 = 'http://baise.gxepb.gov.cn'

global unfit_urls
unfit_urls = []


global urls
urls = []
global urls_pdf
urls_pdf = []


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
    for i in range(0,6):
        if i == 0:
            url = 'http://baise.gxepb.gov.cn/hjzf/xzcf/index.html'
        else:
            url = 'http://baise.gxepb.gov.cn/hjzf/xzcf/index_'+str(i)+'.html'

        doc = pq(url,encoding='utf-8')
        ul = doc('.list-ctn ul')
        lis = ul.children('li')
        for li in lis.items():
            AdministrativeNumber = ''
            title = li.children('a').text()
            pattern2 = re.compile(r'百环罚字.\d{4}.\d{1,3}号')
            match2 = pattern2.search(title)
            if match2:
                AdministrativeNumber = match2.group()

            href = li.children('a').attr('href')
            link = ''
            Name = ''

            if '行政处罚决定书' in title:
                if '../..' in href:
                    link = predix_2 + href.replace('../..','')
                else:
                    link = prefix_1 + href[1:]

                if '-' in title:
                    Name = title.split('-')[1]
                elif '（' in  title and '）' in title:
                    pattern2 = re.compile(r'（.*?）')
                    match2 = pattern2.search(title)
                    if match2:
                        Name = match2.group()
                elif '(' in title and  ')' in title:
                    pattern2 = re.compile(r'\(.*?\)')
                    match2 = pattern2.search(title)
                    if match2:
                        Name = match2.group()


                if ('（' in Name and '）' in Name) or ('(' in Name and ')' in Name):
                    Name_sub =  Name
                    Name = Name[1:len(Name_sub)-1]

                dataFlag = getDataFromUrl(link ,Name,AdministrativeNumber , title)
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



def getDataFromUrl(link ,Name,AdministrativeNumber , title):
    LinkUrl = link
    Name = Name
    Legal = ''
    Category = ''
    According = ''
    Measure = ''
    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = AdministrativeNumber
    Area = '百色市'

    doc = pq(link , encoding='utf-8')

    content = doc('.tb-inner').text().replace('\n', '').replace(' ', '').replace('\xa0', '')
    if AdministrativeNumber.strip() == '':
        pattern2 = re.compile(r'百环罚字.\d{4}.\d{1,3}号')
        match2 = pattern2.search(content)
        if match2:
            AdministrativeNumber = match2.group()

    if '一、环境违法事实和证据' in content and '以上事实' in content:
        Category = re.search('一、环境违法事实和证据(.*?)以上事实', content).group(1)
    elif '下违法行为' in content and '以上事实' in content:
        Category = re.search('下违法行为.(.*?)以上事实', content).group(1)
    elif '一、环境违法事实和证据' in content and '以上违法事实' in content:
        Category = re.search('一、环境违法事实和证据(.*?)以上违法事实', content).group(1)

    if '二、行政处罚的依据、种类' in content and '根据上述规定' in content:
        According = re.search('二、行政处罚的依据、种类(.*?)根据上述规定', content).group(1)
    elif '二、行政处罚的依据、种类' in content and '根据上述法律规定' in content:
        According = re.search('二、行政处罚的依据、种类(.*?).根据上述法律规定', content).group(1)
    elif '二、行政处罚的依据、种类' in content and '根据以上法律规定' in content:
        According = re.search('二、行政处罚的依据、种类(.*?).根据以上法律规定', content).group(1)
    elif '二、责令改正和行政处罚的依据、种类' in content and '根据上述规定' in content:
        According = re.search('二、责令改正和行政处罚的依据、种类(.*?).根据上述规定', content).group(1)
    elif '二、责令改正和行政处罚的依据、种类' in content and '我局对你' in content:
        According = re.search('二、责令改正和行政处罚的依据、种类(.*?).我局对你', content).group(1)

    if '我局决定' in content and '三、行政处罚决定的履行方式和期限' in content:
        Measure = re.search('我局决定(.*?)三、行政处罚决定的履行方式和期限', content).group(1)
    elif '我局决定' in content and '三、处罚决定的履行方式和期限' in content:
        Measure = re.search('我局决定.(.*?)三、处罚决定的履行方式和期限', content).group(1)
    elif '如下处理决定' in content and '三、处罚决定的履行方式和期限' in content:
        Measure = re.search('如下处理决定.(.*?)三、处罚决定的履行方式和期限', content).group(1)
    elif '下行政处罚' in content and '限于接到' in content:
        Measure = re.search('下行政处罚.(.*?)限于接到', content).group(1)
    elif '我局决定' in content and '三、处以决定的履行方式和期限' in content:
        Measure = re.search('我局决定.(.*?)三、处以决定的履行方式和期限', content).group(1)

    pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
    jieshu = content.split('百色市环境保护局 ')[-1]
    if '年' in jieshu and '月' in jieshu and '日' in jieshu:
        match3 = pattern3.search(jieshu)
        CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]

    data_For_Compare = getDataExisted('百色市')  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        if Name.strip() != '':
            sendDataToDb(dataToDb)
            return False






getLinks()













































