#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
from urllib import request
from urllib import  error


global prefix
prefix = 'http://www.yfepb.gov.cn/xxgk/wryhjjgxx/xzcf/cfjd'


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
    for i in range(0,18):
        if i == 0:
            url = 'http://www.yfepb.gov.cn/xxgk/wryhjjgxx/xzcf/cfjd/index.html'
        else:
            url = 'http://www.yfepb.gov.cn/xxgk/wryhjjgxx/xzcf/cfjd/index_'+str(i)+'.html'

        doc = pq(url,encoding='utf-8')
        ul = doc('.fr_bd_ls ul')
        lis = ul.children('li')
        for li in lis.items():
            link = prefix + li('a').attr('href')[1:]
            title = li('a').text()
            if '行政处罚决定书' in title:
                Name = title.split('行政处罚决定书')[0]
                AdministrativeNumber = title.split('行政处罚决定书')[1].replace('（','').replace('）','')
            elif '按日连续处罚决定书' in title:
                Name = title.split('按日连续处罚决定书')[0]
                AdministrativeNumber = title.split('按日连续处罚决定书')[1].replace('（', '').replace('）', '')

            dataFlag = getDataFromUrl(link , Name , AdministrativeNumber)
            if dataFlag:
                break



def textHandel(text,flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')
        elif flag ==2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')


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



def getDataFromUrl(link , Name , AdministrativeNumber):
    LinkUrl = link
    Name = Name
    Legal = ''
    Category = ''
    According = ''
    Measure = ''
    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = AdministrativeNumber
    Area = '云浮市'

    doc = pq(link , encoding='utf-8')
    content =   textHandel(doc('.TRS_Editor').text() ,1)
    content_02= textHandel(doc('.TRS_Editor').text() ,2)

    if '信用代码' in content_02:
        UnifiedSocialCode = re.search('信用代码.(.*?)\n', content_02).group(1)

    if '法定代表人' in content_02:
        Legal = re.search('法定代表人.(.*?)\n', content_02).group(1)

    if '一、环境违法事实和证据' in content and '上述违法事实' in content:
        Category = re.search('一、环境违法事实和证据(.*?)上述违法事实', content).group(1)
    elif '一、环境违法事实和证据' in content and '以上事实' in content:
        Category = re.search('一、环境违法事实和证据(.*?)以上事实', content).group(1)


    if '二、责令改正和行政处罚的依据、种类' in content and '根据上述法律' in content:
        According = re.search('二、责令改正和行政处罚的依据、种类(.*?)根据上述法律', content).group(1)
    elif '二、责令改正和行政处罚的依据、种类' in content and '根据上述法规规定' in content:
        According = re.search('二、责令改正和行政处罚的依据、种类(.*?)根据上述法规规定', content).group(1)
    elif '二、责令改正和行政处罚的依据、种类' in content and '我局决定' in content:
        According = re.search('二、责令改正和行政处罚的依据、种类(.*?).我局决定', content).group(1)
    elif '二、责令改正和行政处罚的依据、种类' in content and '决定' in content:
        According = re.search('二、责令改正和行政处罚的依据、种类(.*?).决定', content).group(1)



    if '如下行政处罚' in content and '三、处罚决定的履行方式和期限' in content:
        Measure = re.search('如下行政处罚.(.*?)三、处罚决定的履行方式和期限', content).group(1)
    elif '作出' in content and '的行政处罚决定' in content:
        Measure = re.search('作出(.*?)的行政处罚决定', content).group(1)

    pattern2 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
    jieshu = content.split('云浮市环境保护局')[-1]
    if '年' in jieshu and '月' in jieshu and '日' in jieshu:
        match2 = pattern2.search(jieshu)
        if match2:
            CreateDate = match2.group().replace('年', '-').replace('月', '-').replace('日', '')

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted('云浮市')  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        print(dataToDb)
        # if Name.strip() != '':
        #     sendDataToDb(dataToDb)
        #     return False



getLinks()







