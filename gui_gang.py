#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://gg.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf'  # ../../

global unfit_urls
unfit_urls = []

global urls
urls = []

global dataForDb
dataForDb = []


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
    for i in range(0,3):
        if i == 0:
            url = 'http://gg.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/index.html'
        else:
            url = 'http://gg.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/index_'+str(i)+'.html'

        doc = pq(url,encoding='utf-8')
        ul = doc('.list-ctn ul')
        lis = ul.children('li')
        for i in lis.items():
            title = i.children('a').text()
            if '行政处罚决定书' in title:
                href = i.children('a').attr('href')[1:]
                link = prefix+href

                dataFlag = getDataFromUrl(link)
                if dataFlag:
                    break

                # urls.append([link])

def getDataFromUrl(link):
    doc = pq(link, encoding='utf-8')
    content = doc('.tb-inner').text().replace('\n', '').replace(' ', '').replace('\xa0', '')

    LinkUrl = link
    Name = ''
    Legal = ''
    Category = ''
    According = ''
    Measure = ''
    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = ''
    Area = '贵港市'

    content_obj = doc('.tb-inner p:nth-child(1)')
    Name = content_obj.text().replace('：', '').replace(':', '')

    if '信用代码' in content and '法定代表人' in content:
        UnifiedSocialCode = re.search('信用代码.(.*?)法定代表人', content).group(1)

    if '法定代表人' in content and '地址' in content:
        Legal = re.search('法定代表人.(.*?)地址', content).group(1)

    if '一、环境违法事实和证据' in content and '以上违法事实' in content:
        Category = re.search('一、环境违法事实和证据(.*?)以上违法事实', content).group(1)
    elif '一、环境违法事实和证据' in content and '以上事实' in content:
        Category = re.search('一、环境违法事实和证据(.*?)以上事实', content).group(1)

    if '二、行政处罚的依据' in content and '根据以上规定' in content:
        According = re.search('二、行政处罚的依据(.*?)根据以上规定', content).group(1)
    elif '二、行政处罚的依据' in content and '我局决定' in content:
        According = re.search('二、行政处罚的依据(.*?)我局决定', content).group(1)
    elif '二、行政处罚的依据' in content and '对你公司' in content:
        According = re.search('二、行政处罚的依据(.*?).对你公司', content).group(1)

    if '我局决定' in content and '三、行政处罚的履行方式和期限' in content:
        Measure = re.search('我局决定(.*?)三、行政处罚的履行方式和期限', content).group(1)
    elif '如下行政处罚' in content and '三、责令改正和行政处罚的履行方式和期限' in content:
        Measure = re.search('如下行政处罚.(.*?)三、责令改正和行政处罚的履行方式和期限', content).group(1)
    elif '如下行政处罚' in content and '三、行政处罚的履行方式和期限' in content:
        Measure = re.search('如下行政处罚.(.*?)三、行政处罚的履行方式和期限', content).group(1)
    elif '作出如下处理' in content and '三、责令改正和行政处罚的履行方式和期限' in content:
        Measure = re.search('作出如下处理.(.*?)三、责令改正和行政处罚的履行方式和期限', content).group(1)

    content_sub = doc('.ctn-tab h1').text()
    pattern = re.compile(r'贵环罚字.\d{4}.\d{1,3}号')
    match2 = pattern.search(content_sub)
    if match2:
        AdministrativeNumber = match2.group()

    if '贵港市环境保护局' in content:
        CreateDate_sub_text = content.split('贵港市环境保护局')[1]
        pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        match3 = pattern3.search(CreateDate_sub_text)
        if match3:
            CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]


    data_For_Compare = getDataExisted('贵港市')  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber,
                    UnifiedSocialCode, Area]
        if Name.strip() != '':
            sendDataToDb(dataToDb)
            return False






getLinks()













































