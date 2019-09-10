#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql


global prefix
prefix = 'http://hbj.maoming.gov.cn/wryhjjgxx/xzcf/'


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
    for i in range(0,7):
        if i == 0:
            url = 'http://hbj.maoming.gov.cn/wryhjjgxx/xzcf/index.html'
        else:
            url = 'http://hbj.maoming.gov.cn/wryhjjgxx/xzcf/index_'+str(i)+'.html'

        doc = pq(url,encoding="utf-8")
        ul = doc('.fylist dd ul')
        lls = ul.children('li')
        for li in lls.items():
            link = prefix + li('a').attr('href')[1:]
            title = li('a').attr('title')
            if ('茂环罚字' in title or '行政处罚' in title) and ('季度' not in title):
                dataFlag = getDataFromUrl(link, title)
                if dataFlag:
                    break


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
    doc = pq(link, encoding="utf-8")
    content = textHandel(doc('.TRS_Editor').text(),1)
    content_02 = textHandel(doc('.TRS_Editor').text(), 2)
    if content == None:
        content = textHandel(doc('.xl-nr').text(), 1)
        content_02 = textHandel(doc('.xl-nr').text(), 2)

    content_obj = doc('.TRS_Editor p')
    imgs_length = content_obj('img').length

    Name = ''
    LinkUrl = link
    AdministrativeNumber = ''
    UnifiedSocialCode = ''
    Legal = ''
    CreateDate = ''
    Category = ''
    According = ''
    Measure = ''
    Area = '茂名市'

    pattern = re.compile(r'茂环罚字.\d{4}.\d{0,2}号{0,1}')
    match = pattern.search(content)
    if match:
        AdministrativeNumber = match.group(0)
        if '统一社会信用' in content:
            Name = re.search(AdministrativeNumber + '(.*?).统一社会信用', content).group(1)
        elif '营业执照' in content:
            Name = re.search(AdministrativeNumber + '(.*?).营业执照', content).group(1)
    else:
        if imgs_length < 1:
            if '营业执照' in content:
                Name = re.search('(.*?).营业执照', content).group(1)
            elif '统一社会信用' in content:
                Name = re.search('(.*?).统一社会信用', content).group(1)

    if '信用代码' in content_02 :
        UnifiedSocialCode = re.search('信用代码.(.*?)\n', content_02).group(1)

    if '法定代表人' in content_02:
        Legal = re.search('法定代表人.(.*?)\n', content_02).group(1)

    if '环境违法行为' in content and '以上事实' in content:
        Category = re.search('环境违法行为.(.*?)以上事实', content).group(1)


    if '二、责令改正和行政处罚的依据、种类及其履行方式、期限' in content and '根据上述规定' in content:
        According = re.search('二、责令改正和行政处罚的依据、种类及其履行方式、期限.(.*?)根据上述规定', content).group(1)
    elif '依据' in content and '规定' in content:
        According = re.search('依据(.*?)规定.', content).group(0)
    elif '依据' in content and '的规定' in content:
        According = re.search('依据(.*?)的规定', content).group(0)


    if '下行政处罚' in content and '收款银行' in content:
        Measure = re.search('下行政处罚.(.*?)收款银行', content).group(1)
    elif '我局决定' in content and '收款银行' in content:
        Measure = re.search('我局决定.(.*?)收款银行', content).group(1)

    pattern3 = re.compile(r'\d{4}年\d{0,2}月\d{0,2}日')
    if '茂名市环境保护局' in content:
        jieshu = content.split('茂名市环境保护局')[-1]
        if '年' in jieshu and '月' in jieshu and '日' in jieshu:
            match3 = pattern3.search(jieshu)
            if match3:
                CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted('茂名市')  # 获得最新的本地域的 已经存在的 数据
    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        if Name.strip() != '':
            sendDataToDb(dataToDb)
            return False



getLinks()






