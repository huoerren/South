#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import random


global prefix
prefix = 'http://epb.sg.gov.cn/hjgl/hjzf'

global unfit_urls
unfit_urls = ['http://epb.sg.gov.cn/hjgl/hjzf/201806/t20180622_659888.html',
              'http://epb.sg.gov.cn/hjgl/hjzf/201802/t20180222_516925.html']

global text_urls
text_urls = []
global excel_urls
excel_urls = []


global dataForDb
dataForDb = []




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

def ifGt2015(title):   # 判断是否 是 2015之前的，如果是  2015年之后的，则数据用页面里面的内容，否则用表格中的内容
    pattern = re.compile(r'\d{4}')
    match = pattern.search(title)
    flag = False
    Year = 0
    if match:
        Year = match.group()
        if int(Year) > 2015:
            flag = True
    return flag


def getLinks():
    for i in range(0,9):
        if i == 0 :
            url = 'http://epb.sg.gov.cn/hjgl/hjzf/index.html'
        else:
            url = 'http://epb.sg.gov.cn/hjgl/hjzf/index_'+str(i)+'.html'

        doc = pq(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0'},encoding="utf-8")
        ul = doc('.comlist1.mt10.hx')
        lis = ul.children('li')
        if lis.length>0:
            for item in lis.items():
                title = item('a').attr('title')
                href  = item('a').attr('href')[1:]
                link = prefix + href

                if '行政处罚决定书' in title and ifGt2015(title):
                    dataFlag = getDataFromUrl(link , title) #如果本条数据已经存在则终止该循环，否则插入新的数据，并继续循环
                    if dataFlag:
                        break
                elif '环境行政处罚情况' in title:
                    dataFlag = getDataFromExcel(link)
                    if dataFlag:
                        break

def textHandel(text):
    if len(text) != 0:
        return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')


def getDataFromUrl(link , title):
    doc = pq(link, headers={'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)'}, encoding="utf-8")
    content = doc('.TRS_Editor').text().replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')

    Name = ''
    LinkUrl = link
    Legal = ''
    Category = ''
    According = ''
    Measure = ''
    AdministrativeNumber = ''
    Area = '韶关市'
    CreateDate = ''
    UnifiedSocialCode = ''

    pattern = re.compile(r'韶环罚字.\d{4}.第\d{0,3}号')
    match = pattern.search(title)
    if match:
        AdministrativeNumber = match.group()

    CreateDate = content.split('。')[-1].replace('韶关市环境保护局', '').replace('年', '-').replace('月', '-').replace('日', '')

    if '统一社会信用代码' in content and '地址' in content:
        UnifiedSocialCode = re.search('统一社会信用代码：(.*?)地址', content).group(1)

    if '法定代表人' in content and '一、调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况' in content:
        Legal = re.search('法定代表人：(.*?)一、调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况', content).group(1)
    elif '法定代表人' in content and '一、调查情况及发现的环境违法事实、证据' in content:
        Legal = re.search('法定代表人：(.*?)一、调查情况及发现的环境违法事实、证据', content).group(1)

    if '统一社会信用代码' in content and '韶环罚字' in content:
        Name = re.search('韶环罚字〔\d+〕第\d+号(.*?)统一社会信用代码', content).group(1)
    elif '身份证号码' in content and '韶环罚字' in content:
        Name = re.search('韶环罚字〔\d+〕第\d+号(.*?)身份证号码', content).group(1)
        if '（' in Name and '）' in Name:
            Name = re.search('（(.*?)）', Name).group(1)
    elif '统一社会信用代码' in content:
        Name = re.search('(.*?)统一社会信用代码', content).group(1)
    elif '身份证号码' in content:
        Name = re.search('(.*?)身份证号码', content).group(1)
        if '（' in Name and '）' in Name:
            Name = re.search('（(.*?)）', Name).group(1)
    elif '身份证号' in content:
        Name = re.search('(.*?)身份证号', content).group(1)
        if '（' in Name and '）' in Name:
            Name = re.search('（(.*?)）', Name).group(1)
    elif '营业执照注册号' in content:
        Name = re.search('(.*?)营业执照注册号', content).group(1).replace('行政处罚决定书', '')

    Name = Name.replace('经营者', '').replace('：', '').replace('：', '').replace('字号：', '')

    if '一、调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况' in content and '以上事实' in content:
        Category = re.search('一、调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况(.*?)以上事实', content).group(1)
    elif '一、调查情况及发现的环境违法事实、证据' in content and '以上事实' in content:
        Category = re.search('一、调查情况及发现的环境违法事实、证据(.*?)以上事实', content).group(1)

    if '二、行政处罚的依据、种类及其履行方式、期限' in content and '依据上述规定' in content:
        According = re.search('二、行政处罚的依据、种类及其履行方式、期限(.*?)依据上述规定', content).group(1)
    elif '二、行政处罚的依据、种类及其履行方式、期限' in content and '根据上述规定' in content:
        According = re.search('二、行政处罚的依据、种类及其履行方式、期限(.*?)根据上述规定', content).group(1)

    if '根据上述规定' in content and '三、申请行政复议或者提起行政诉讼的途径和期限' in content:
        Measure = re.search('根据上述规定，(.*?)三、申请行政复议或者提起行政诉讼的途径和期限', content).group(1)
    elif '依据上述规定' in content and '' in content:
        Measure = re.search('依据上述规定，(.*?)三、申请行政复议或者提起行政诉讼的途径和期限', content).group(1)

    dataFromPage = [Name,Category,According,Measure,CreateDate,Area]
    data_For_Compare = getDataExisted('韶关市')  # 获得最新的本地域的 已经存在的 数据
    if dataFromPage in data_For_Compare:
        return True  # 该条数据已经存在时， 返回 True
    else:
        dataToDb = [LinkUrl,Name,Legal,CreateDate,Category,According,Measure,AdministrativeNumber,UnifiedSocialCode,Area]
        sendDataToDb(dataToDb)
        return  False # 插入新数据后，返回 False

def getDataFromExcel(link):
    doc = pq(link,
             headers={'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)'},
             encoding="utf-8")
    tableData = doc('.TRS_Editor').children('table').children('tbody').children('tr').children('td').children('table')
    trs = tableData.children('tbody').children('tr')

    if trs.length == 0:
        trs = doc('.TRS_Editor').children('table').children('tbody').children('tr')
    if trs.length == 0:
        trs = doc('.FCK__ShowTableBorders').children('tbody').children('tr')
    if trs.length == 0:
        trs =doc('table').children('tbody').children('tr')

    if trs.length >0:
        for tr in trs.items():
            if '处罚文号' not in tr.text():
                flag = False  # “返回” 是以 每页 为单位，每页中一旦出现有重复的数据，立即返回True ，如果一直没有重复数据则在最后时 返回 False .

                Name = ''
                LinkUrl = link
                Legal = ''
                Category = ''
                According = ''
                Measure = ''
                AdministrativeNumber = ''
                Area = '韶关市'
                CreateDate = ''
                UnifiedSocialCode = ''

                AdministrativeNumber = textHandel(tr('td:nth-child(1)').text())
                Name = textHandel(tr('td:nth-child(2)').text())
                Category = textHandel(tr('td:nth-child(3)').text())

                Acc_Meas = textHandel(tr('td:nth-child(4)').text())
                if '作出如下行政处罚：' in Acc_Meas:
                    According = Acc_Meas.split('作出如下行政处罚：')[0].split('，')[-2]
                    Measure   = Acc_Meas.split('作出如下行政处罚：')[1]

                CreateDate = textHandel(tr('td:nth-child(6)').text()).replace('年','-').replace('月','-').replace('日','')

                getDataExisted('韶关市')

                dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
                data_For_Compare = getDataExisted('韶关市')  # 获得最新的本地域的 已经存在的 数据

                if dataFromPage in data_For_Compare:
                    flag = True
                    break
                else:
                    dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
                    sendDataToDb(dataToDb)
        return flag










#########################################################


getLinks()







