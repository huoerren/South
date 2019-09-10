#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://hbj.jiangmen.gov.cn/thirdData/zdlhxxgk/xzcfxx'

global unfit_urls
unfit_urls = []

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
    for i in range(0,30):
        if i == 0 :
            url = 'http://hbj.jiangmen.gov.cn/thirdData/zdlhxxgk/xzcfxx/'
        else:
            url = 'http://hbj.jiangmen.gov.cn/thirdData/zdlhxxgk/xzcfxx/index_'+str(i)+'.html'

        doc = pq(url,headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'},encoding="utf-8")
        ul = doc('.comlist2.mt10.fh40')
        lis = ul.children('li')
        for item in lis.items():
            title = item('a').attr('title')
            if ('公告' not in  title) and ('限制' not in title) and ('限产' not in title) and ('催告书' not in title) and \
                    ('限制' not in title) and ('查处和整改' not in title) and ('名单' not in title) and \
                    ('查封' not in title) and ('扣押' not in title):
                if '处罚情况' not in title:
                    dataFlag =  getDataFromUrl(item('a').attr('title'), prefix+ item('a').attr('href')[1:])
                    if dataFlag:
                        break
                else:
                    dataFlag = getDataFromExcel(item('a').attr('title'), prefix+ item('a').attr('href')[1:])
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


def getDataFromUrl(title,link):
    if link not in unfit_urls:
        # print(link)
        doc = pq(link, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}, encoding="utf-8")
        pyObject = doc('.content_text')
        pyObject_text =  textHandel(doc('.content_text').text(),1)
        pyObject_text_02=textHandel(doc('.content_text').text(),2)

        Name = ''
        LinkUrl = link
        Legal = ''
        Category = ''
        According = ''
        Measure = ''
        AdministrativeNumber = ''
        CreateDate = ''
        UnifiedSocialCode = ''
        Area = '江门市'

        if '当事人' in pyObject_text_02:
            Name = re.search('当事人.(.*?)\n', pyObject_text_02).group(1)

        pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        if '江门市环境保护局' in pyObject_text:
            jieshu = pyObject_text.split('江门市环境保护局')[-1]
            if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                match = pattern.search(jieshu)
                if match:
                    CreateDate = match.group().replace('年', '-').replace('月', '-').replace('日', '')




        pattern2 = re.compile(r'江环罚字.\d{4}.\d{0,3}号{0,1}')
        match2 = pattern2.search(pyObject_text)
        if match2:
            AdministrativeNumber = match2.group()


        if '信用代码' in pyObject_text_02:
            UnifiedSocialCode = re.search('信用代码.(.*?)\n', pyObject_text_02).group(1)


        if '法定代表人' in pyObject_text_02 :
            Legal = re.search('法定代表人.(.*?)\n', pyObject_text_02).group(1)
        elif '法人代表' in pyObject_text_02 :
            Legal = re.search('法人代表.(.*?)\n', pyObject_text_02).group(1)
        elif '投资人' in pyObject_text_02 :
            Legal = re.search('投资人.(.*?)\n', pyObject_text_02).group(1)


        if '一、调查情况及发现的环境违法事实、证据' in pyObject_text and '上述事实有' in pyObject_text:
            Category = re.search('一、调查情况及发现的环境违法事实、证据(.*?)上述事实有', pyObject_text).group(1)

        if '二、行政处罚的依据、种类及其履行方式和期限' in pyObject_text  and '三、申请复议或者提起诉讼的途径和期限' in pyObject_text:
            According_Measure = re.search('二、行政处罚的依据、种类及其履行方式和期限(.*?)三、申请复议或者提起诉讼的途径和期限', pyObject_text).group(1)
            if '（一）' in According_Measure and '（二）' in According_Measure:

                if '（一）' in According_Measure and '我局决定责令' in According_Measure:
                    According_01 = re.search('（一）(.*?).我局决定责令', According_Measure).group(1)
                elif '（一）' in According_Measure and '我局决定' in According_Measure:
                    According_01 = re.search('（一）(.*?).我局决定', According_Measure).group(1)
                elif '（一）' in According_Measure and '我局责令' in According_Measure:
                    According_01 = re.search('（一）(.*?).我局责令', According_Measure).group(1)

                if '（二）' in According_Measure and '我局决定对' in According_Measure:
                    According_02 = re.search('（二）(.*?).我局决定对', According_Measure).group(1)

                According = According_01 + ' ; ' + According_02

                if '责成' in According_Measure:
                    Measure_01 = re.search('.我局责成(.*?).', According_Measure).group(1)
                elif '我局决定' in According_Measure:
                    Measure_01 = re.search('.我局决定(.*?).', According_Measure).group(1)
                else:
                    Measure_01 = re.search('.责令(.*?).', According_Measure).group(1)

                Measure_02 = re.search('.我局决定对(.*?)的行政处罚.', According_Measure).group(1)

                Measure = Measure_01 + " ; " + Measure_02
            else:
                According = re.search('依据(.*?).我局', According_Measure).group(1)
                if '拟' in According_Measure:
                    Measure = re.search('.我局拟(.*?)(根据|依据)', According_Measure).group(1)
                elif '我局责令' in According_Measure:
                    Measure = re.search('我局责令(\w+)', According_Measure).group(1)
                else  :
                    Measure = re.search('.我局决定(.*?)(根据|依据)', According_Measure).group(1)

        # print( [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area])

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted('江门市')  # 获得最新的本地域的 已经存在的 数据
        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
            if '限产' not in AdministrativeNumber:
                sendDataToDb(dataToDb)
                return False



def getDataFromExcel(title,link):
    doc = pq(link, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}, encoding="utf-8")
    table = doc('.ke-zeroborder')
    trs = table.children('tbody').children('tr')
    if trs.length >0:
        for tr in trs.items():
            if tr.children('td:nth-child(1)').text().isdigit():
                flag = False  # “返回” 是以 每页 为单位，每页中一旦出现有重复的数据，立即返回True ，如果一直没有重复数据则在最后时 返回 False .

                Name = ''
                LinkUrl = link
                Legal = ''
                Category = ''
                According = ''
                Measure = ''
                AdministrativeNumber = ''
                CreateDate = ''
                UnifiedSocialCode = ''
                Area = '江门市'

                Name = textHandel(tr.children('td:nth-child(2)').text(),1)
                Category = textHandel(tr.children('td:nth-child(3)').text(),1)

                Acc_Mea =  textHandel(tr.children('td:nth-child(4)').text(),1)

                According = Acc_Mea.split('的规定')[0]
                Measure   = Acc_Mea.split('的规定')[1]

                CreateDate = textHandel(tr.children('td:nth-child(5)').text(),1)
                if '-' not in CreateDate :
                    CreateDate = CreateDate[0:4]+'-'+CreateDate[4:6]+'-'+CreateDate[6:8]
                dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
                data_For_Compare = getDataExisted('江门市')  # 获得最新的本地域的 已经存在的 数据
                # print([LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area])
                if dataFromPage in data_For_Compare:
                    flag = True
                    break
                else:
                    dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
                    sendDataToDb(dataToDb)
        return flag


getLinks()





