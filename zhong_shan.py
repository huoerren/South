#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.zsepb.gov.cn/sdgg'

global unfit_urls
unfit_urls = []


global urls
urls = []


global dataForDb
dataForDb = []



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
    for i in range(0,15):
        if i == 0:
            url = 'http://www.zsepb.gov.cn/sdgg/index.html'
        else:
            url = 'http://www.zsepb.gov.cn/sdgg/index_'+str(i)+'.html'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }

        doc = pq(url ,headers=headers ,encoding='utf-8')
        lis = doc('.clearfix').children('li')
        for li in lis.items() :
            if '行政处罚决定书' in  li('a').text():
                link = prefix + li('a').attr('href')[1:]
                title= li('a').text()
                dataFlag = getDataFromUrl(link, title)
                if dataFlag:
                    break


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

    title = title

    LinkUrl = link
    Name = ''
    UnifiedSocialCode = ''

    Category = ''
    According = ''
    Measure = ''

    CreateDate = ''
    Legal = ''
    AdministrativeNumber = ''
    Area = '中山市'

    if '送达公告' in title:
        AdministrativeNumber = re.search('中山市环境保护局行政处罚决定书》(.*?)送达公告',title).group(1).replace('{', '（').replace('}', '）')
        AdministrativeNumber = AdministrativeNumber[1:len(AdministrativeNumber) - 1]
    elif '公告送达' in title:
        AdministrativeNumber = re.search('中山市环境保护局行政处罚决定书》(.*?)公告送达', title).group(1).replace('{', '（').replace('}', '）')
        AdministrativeNumber = AdministrativeNumber[1:len(AdministrativeNumber) - 1]
    else:
        AdministrativeNumber = title.split('政处罚决定书》')[1]
        AdministrativeNumber = AdministrativeNumber[1:len(AdministrativeNumber) - 1]
    if '号' not in AdministrativeNumber:
        AdministrativeNumber = AdministrativeNumber + '号'
    if '中' not in AdministrativeNumber:
        AdministrativeNumber = '中'+AdministrativeNumber


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }

    doc = pq(link, headers=headers, encoding='utf-8')
    content = ''
    content = doc('.TRS_PreAppend').text().replace('\r\n', '').replace('\n', '').replace(' ', '').replace('\xa0', '')
    if content.strip() == '':
        content = doc('.TRS_Editor').text().replace('\r\n', '').replace('\n', '').replace(' ', '').replace('\xa0', '')


    if '环境保护局行政处罚决定书送达公告' in content:
        Name = re.search('环境保护局行政处罚决定书送达公告(\w+)',content).group(1)

    if '经我局调查核实，' in content and '我局' in content:
        Category = re.search('经我局调查核实，(.*?)我局', content).group(1)

    if '我局依据' in content and '对你' in content:
        According = re.search('我局依据(.*?).对你', content).group(1)
    elif '我局依据' in content and '经研究决定' in content:
        According = re.search('我局依据(.*?).经研究决定', content).group(1)

    if '如下行政处罚' in content and '因无法与你' in content:
        Measure = re.search('如下行政处罚.(.*?)因无法与你', content).group(1)
    elif '经研究决定' in content and '因无法与你' in content:
        Measure = re.search('经研究决定.(.*?)因无法与你', content).group(1)
    elif '如下行政处罚' and '因现场查看' in content:
        Measure = re.search('如下行政处罚.(.*?)因现场查看', content).group(1)

    pattern2 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
    match2 = pattern2.search(content, re.A)
    if match2:
        CreateDate = match2.group().replace('年', '-').replace('月', '-').replace('日', '')

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted('中山市')  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return True
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
        if Name.strip() != '':
            sendDataToDb(dataToDb)
            return False



getLinks()













































