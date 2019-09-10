#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://zwgk.jieyang.gov.cn'




def textHandel(text,flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')
        elif flag ==2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')
    else:
        return ''

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
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306, db='greentest', charset='utf8')
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
            dataToDb[0], dataToDb[1], dataToDb[2], dataToDb[3], dataToDb[4], dataToDb[5], dataToDb[6], dataToDb[7],dataToDb[8], dataToDb[9]))
            conn.commit()
            print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None




def getDataFromUrl(link, AdministrativeNumber):
    doc = pq(link, encoding='utf-8')
    a_word = doc('.cont div a').attr('href')

    a_pdf = doc('.add a')
    a_href = a_pdf.attr('href')

    a_img = doc('.cont').find('img')

    if a_word == None and a_href == None :  # 详情 页面上内容 即不是 下载文档 也不是 在线pdf 文件。
        Name = ''
        AdministrNumber = ''
        UnifiedSocialCode = ''
        Legal = ''
        LinkUrl = link

        Category = ''
        According = ''
        Measure = ''

        CreateDate = ''
        Area = '揭阳市'

        content = textHandel(doc('.cont').text(),1)
        title =   textHandel(doc('.tit').text(),1)

        pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        if '揭阳市环境保护局（印章）' in content:
            jieshu = content.split('揭阳市环境保护局（印章）')[-1]
            if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                match = pattern.search(jieshu)
                CreateDate = match.group().replace('年', '-').replace('月', '-').replace('日', '')
        if CreateDate.strip() == '':
            if '揭阳市环境保护局' in content:
                jieshu = content.split('揭阳市环境保护局')[-1]
                if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                    match = pattern.search(jieshu)
                    CreateDate = match.group().replace('年', '-').replace('月', '-').replace('日', '')

        pattern2 = re.compile(r'揭环罚.\d{4}.第\d{0,3}号{0,1}')
        match2 = pattern2.search(content)
        if match2:
            AdministrNumber = match2.group()
        else:
            match2 = pattern2.search(title)
            if match2:
                AdministrNumber = match2.group()

        content_02 = textHandel(doc('.cont').text(),2)
        if re.search('(.*?)\n',content_02):
            Name = re.search('(.*?)\n',content_02).group(1)
        if '环境保护局' in Name:
            Name = doc('.cont').children('p:nth-child(5)').text()
        Name = Name.replace('：', '').replace(':', '')

        if '法定代表人' in content_02:
            Legal = re.search('法定代表人.(.*?)\n',content_02).group(1)

        if '信用代码' in content_02:
            UnifiedSocialCode = re.search('信用代码.(.*?)\n',content_02).group(1)

        if '环境违法行为：' in content and '以上事实' in content:
            Category = re.search('环境违法行为：(.*?)以上事实', content).group(1)
        elif '调查发现：' in content and '上述事实' in content:
            Category = re.search('调查发现：(.*?)上述事实', content).group(1)

        if '三、行政处罚的依据、种类及其履行方式、期限' in content and '，对你' in content:
            According = re.search('三、行政处罚的依据、种类及其履行方式、期限(.*?).对你', content).group(1)
        elif '二、行政处罚的依据、种类及其履行方式、期限' in content and '，对你' in content:
            According = re.search('二、行政处罚的依据、种类及其履行方式、期限(.*?).对你', content).group(1)
        elif '依据《' in content and '我局决定' in content:
            According = re.search('依据《(.*?).我局决定', content).group(1)
            According = '依据《' + According
        elif '根据《' in content and '我局决定' in content:
            According = re.search('根据《(.*?).我局决定', content).group(1)
            According = '根据《' + According

        if '如下处罚决定' in content and '限你' in content:
            Measure = re.search('如下处罚决定.(.*?)限你', content).group(1)
        elif '如下行政处罚' in content and '限于接到' in content:
            Measure = re.search('如下行政处罚.(.*?)限于接到', content).group(1)

        # Name ,AdministrativeNumber,UnifiedSocialCode ,Legal,CreateDate Category  According Measure
        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据
        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
            if Name.strip() != '':
                sendDataToDb(dataToDb)
                return False





def getLinks():
    for i in range(201,301): # 1 - 332
        url = 'http://zwgk.jieyang.gov.cn/OpenInfoRight.action?pageNum='+str(i)+'&pageSize=10&depCode=007026553'
        doc = pq(url,encoding="utf-8")
        trs = doc('.csstable tr')
        for tr in trs.items():
            href = tr.children('td:nth-child(2)').children('a').attr('href')
            title= tr.children('td:nth-child(2)').children('a').text()
            AdministrativeNumber =  tr.children('td:nth-child(4)').text()
            if '行政处罚决定书' in title:
                link = prefix+href
                AdministrativeNumber = AdministrativeNumber
                dataFlag = getDataFromUrl(link, AdministrativeNumber)
                if dataFlag:
                    break


getLinks()




















