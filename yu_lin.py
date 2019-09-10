#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://gg.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf'  # ../../

global unfit_urls
unfit_urls = ['http://hbj.yulin.gov.cn/zjzcdcfjd/698.jhtml']


def textHandel(text, flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n', '').replace(' ', '').replace('\xa0', '')
        elif flag == 2:
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
            dataToDb[0], dataToDb[1], dataToDb[2], dataToDb[3], dataToDb[4], dataToDb[5], dataToDb[6], dataToDb[7],dataToDb[8], dataToDb[9]))
            conn.commit()
            print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None


def getDataFromUrl(link,AdministrativeNumber):
    doc = pq(link, encoding='utf-8')
    content = textHandel(doc('.content-txt').text(),1)
    content_02 = textHandel(doc('.content-txt').text(), 2)

    if content != None and len(content.strip())>0:
        if link not in unfit_urls:
            LinkUrl = link
            Name = ''
            Legal = ''

            Category = ''
            According = ''
            Measure = ''

            UnifiedSocialCode = ''
            CreateDate = ''
            AdministrativeNumber = ''
            Area = '玉林市'

            pattern = re.compile(r'玉环罚.\d{4}.\d{0,3}号')
            match = pattern.search(content)
            if match:
                AdministrativeNumber = match.group()
            if AdministrativeNumber.strip() == '':
                title = textHandel(doc('.content_xxgk1').children('h1').text(), 1)
                match2 = pattern.search(title)
                if match2:
                    AdministrativeNumber = match2.group()

            if '法定代表人' in content_02 :
                Legal = re.search( '法定代表人.(.*?)\n', content_02).group(1)


            if '当事人' in content_02:
                Name = re.search( '当事人.(.*?)\n', content_02).group(1)
            if Name.strip()== '':
                if AdministrativeNumber in content  :
                    Name = re.search(AdministrativeNumber+'(.*?)：', content).group(1)
            Name = Name.replace('：', '').replace(':', '')

            if '统一社会信用代码' in content_02:
                UnifiedSocialCode = re.search( '统一社会信用代码(.*?)\n', content_02).group(1)


            if '环境违法行为：' in content and '事实' in content:
                Category = re.search('环境违法行为：(.*?)事实', content).group(1)
            elif '环境违法事实和' in content and '事实' in content:
                Category = re.search('环境违法事实和(.*?)事实', content).group(1)


            if '二、责令改正和行政处罚的依据和种类' in content and '根据以上规定' in content:
                According = re.search('二、责令改正和行政处罚的依据和种类(.*?)根据以上规定', content).group(1)
            elif '二、责令改正行政处罚的依据和种类' in content and '我局' in content:
                According = re.search('二、责令改正行政处罚的依据和种类(.*?)，我局', content).group(1)
            elif '二、行政处罚的依据和种类' in content and '对你厂' in content:
                According = re.search('二、行政处罚的依据和种类(.*?).对你厂', content).group(1)
            elif '二、行政处罚的依据和种类' in content and '根据以上规定' in content:
                According = re.search('二、行政处罚的依据和种类(.*?)根据以上规定.', content).group(1)
            elif '二、行政处罚的依据和种类' in content and '根据上述规定' in content:
                According = re.search('二、行政处罚的依据和种类(.*?)根据上述规定.', content).group(1)
            elif '二、行政处罚的依据和种类' in content and '的规定' in content:
                According = re.search('二、行政处罚的依据和种类(.*?)的规定.', content).group(1)
            elif '实施按日连续处罚的依据和总额' in content and '我局决定' in content:
                According = re.search('实施按日连续处罚的依据和总额(.*?)我局决定',content).group(1)


            if '我局决定' in content and '。' in content:
                Measure = re.search('我局决定.(.*?)。', content).group(1)
            elif '下处罚' in content and '。' in content:
                Measure = re.search('下处罚.(.*?)。', content).group(1)
            elif '处以罚款' in content and '。' in content:
                Measure = re.search('处以罚款.(.*?)。', content).group(1)
                Measure = '罚款' + Measure
            elif '我局决定责令' in content and '。' in content:
                Measure = re.search('我局决定责令.(.*?)。', content).group(1)
            elif '我局责令' in content and '。' in content:
                Measure = re.search('我局责令.(.*?)。', content).group(1)


            if '玉林市环境保护局' in content:
                CreateDate_sub_text = content.split('玉林市环境保护局')[1]
                pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
                match3 = pattern3.search(CreateDate_sub_text)
                if match3:
                    CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')

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
    for i in range(1,7):
        url = 'http://hbj.yulin.gov.cn/zjzcdcfjd/index_'+str(i)+'.jhtml'
        doc = pq(url,encoding='utf-8')
        table = doc('.xxgk_list table tbody')
        trs = table.children('tr')
        for tr in trs.items():
            if '标题' not in tr.text():
                AdministrativeNumber = ''
                href = ''
                title = tr.children('td:nth-child(1) a').text()
                if '处罚决定书' in title:
                    AdministrativeNumber = tr.children('td:nth-child(2)').text()
                    href = tr.children('td:nth-child(1) a').attr('href')
                    link = href
                    dataFlag = getDataFromUrl(link,AdministrativeNumber)
                    if dataFlag:
                        break



getLinks()













































