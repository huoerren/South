#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix_1
prefix_1 = 'http://laibin.gxepb.gov.cn'  # ../../

global predix_2
predix_2 = 'http://laibin.gxepb.gov.cn/hjzf/xzcf'

global unfit_urls
unfit_urls = ['http://laibin.gxepb.gov.cn/hjzf/xzcf/201504/t20150430_10002786.html',
              'http://laibin.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/zjcfjd/201806/t20180626_43002.html',
              'http://laibin.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/zjcfjd/201707/t20170718_33998.html',
              'http://laibin.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/zjcfjd/201707/t20170704_33686.html',
              'http://laibin.gxepb.gov.cn/hjzf/xzcf/201705/t20170527_32989.html',
              'http://laibin.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/zjcfjd/201701/t20170116_31064.html',
              'http://laibin.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/zjcfjd/201702/t20170207_31369.html',
              'http://laibin.gxepb.gov.cn/hjzf/xzcf/201612/t20161202_29977.html'
              ]


global urls
urls = []


global dataForDb
dataForDb = []



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
    for i in range(0,4):
        if i == 0:
            url = 'http://laibin.gxepb.gov.cn/hjzf/xzcf/index.html'
        else:
            url = 'http://laibin.gxepb.gov.cn/hjzf/xzcf/index_'+str(i)+'.html'

        doc = pq(url,encoding='utf-8')
        ul = doc('.list-ctn ul')
        lis = ul.children('li')
        for li in lis.items():
            title = li.children('a').text().replace(' ','')
            link = ''
            if '行政处罚决定书' in title:
                href = li.children('a').attr('href')
                if '../..' in href:
                    link = prefix_1 + href.replace('../..','')
                else:
                    link = predix_2 + href[1:]

                dataFlag = getDataFromUrl(link, title)
                if dataFlag:
                    break


def getDataFromUrl(link, title):
    if link not in unfit_urls:
        doc = pq(link, encoding='utf-8')
        content = textHandel(doc('.tb-inner').text(),1)
        content_02 = textHandel(doc('.tb-inner').text(),2)
        LinkUrl = link
        Name = ''
        Legal = ''

        Category = ''
        According = ''
        Measure = ''

        UnifiedSocialCode = ''
        CreateDate = ''
        AdministrativeNumber = ''
        Area = '来宾市'

        pattern = re.compile(r'来环罚字.\d{4}.\d{1,3}号')
        match = pattern.search(content)
        if match:
            AdministrativeNumber = match.group()

        if AdministrativeNumber.strip() == '':
            pattern2 = re.compile(r'金环罚字.\d{4}.\d{1,3}号')
            match2 = pattern2.search(content)
            if match2:
                AdministrativeNumber = match2.group()

        if '统一社会' in content:
            Name = re.search(AdministrativeNumber + '(.*?)统一社会', content).group(1)
        elif '营业执照' in content:
            Name = re.search(AdministrativeNumber + '(.*?)营业执照', content).group(1)

        Name = Name.replace('行政处罚决定书', '').replace('：', '') \
            .replace('被处罚人', '').replace('，', '').replace(':', '').replace(' ', '')

        if '信用代码' in content_02:
            UnifiedSocialCode = re.search('信用代码.(.*?)\n', content_02).group(1)

        if '法定代表人' in content_02:
            Legal = re.search('法定代表人.(.*?)\n',content_02).group(1)


        if '一、环境违法事实和证据' in content and '以上事实' in content:
            Category = re.search('一、环境违法事实和证据(.*?)以上事实', content).group(1)
        elif '一、环境违法事实和证据' in content and '以上违法事实' in content:
            Category = re.search('一、环境违法事实和证据(.*?)以上违法事实', content).group(1)


        if '二、行政处罚的依据、种类' in content and '我局决定' in content:
            According = re.search('二、行政处罚的依据、种类(.*?).我局决定', content).group(1)
        elif '二、行政处罚的依据、种类' in content and '我局对你' in content:
            According = re.search('二、行政处罚的依据、种类(.*?).我局对你', content).group(1)
        elif '二、责令改正和行政处罚的依据和种类' in content and '我局决定' in content:
            According = re.search('二、责令改正和行政处罚的依据和种类(.*?).我局决定', content).group(1)
        elif '二、责令改正和行政处罚的依据、种类' in content and '我局决定' in content:
            According = re.search('二、责令改正和行政处罚的依据、种类(.*?).我局决定', content).group(1)
        elif '二、行政处罚的依据、种类' in content and '我局拟' in content:
            According = re.search('二、行政处罚的依据、种类(.*?).我局拟', content).group(1)


        if '我局决定' in content and '三、行政处罚履行的方式、期限' in content:
            Measure = re.search('我局决定(.*?)三、行政处罚履行的方式、期限', content).group(1)
        elif '我局决定' in content and '三、行政处罚的履行方式和期限' in content:
            Measure = re.search('我局决定(.*?)三、行政处罚的履行方式和期限', content).group(1)
        elif '我局决定' in content and '三、行政处罚的履行方式' in content:
            Measure = re.search('我局决定(.*?)三、行政处罚的履行方式', content).group(1)
        elif '我局决定' in content and '三、行政处罚的履行方式、期限' in content:
            Measure = re.search('我局决定(.*?)三、行政处罚的履行方式、期限', content).group(1)
        elif '我局决定' in content and '三、申请行政复议或者提起行政诉讼的途径和期限' in content:
            Measure = re.search('我局决定(.*?)三、申请行政复议或者提起行政诉讼的途径和期限', content).group(1)
        elif '处理决定' in content and '三、行政处罚的履行方式和期限' in content:
            Measure = re.search('处理决定.(.*?)三、行政处罚的履行方式和期限', content).group(1)
        elif '如下行政处罚' in content and '三、行政处罚的履行方式和期限' in content:
            Measure = re.search('如下行政处罚.(.*?)三、行政处罚的履行方式和期限', content).group(1)


        if '来宾市环境保护局' in content:
            pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
            jieshu = content.split('来宾市环境保护局')[-1]
            if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                match3 = pattern3.search(jieshu)
                CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')
        if CreateDate.strip() == '':
            if '金秀瑶族自治县环境保护局' in content:
                pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
                jieshu = content.split('金秀瑶族自治县环境保护局')[-1]
                if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                    match3 = pattern3.search(jieshu)
                    CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted('来宾市')  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
            if Name.strip() != '':
                sendDataToDb(dataToDb)
                return False

        # data = [LinkUrl, Name, Legal, Category, According, Measure, UnifiedSocialCode, CreateDate, AdministrativeNumber, Area]




def getDatas():
    for i in urls:
        # print(i[0])
        if i[0] not in unfit_urls:
            doc = pq(i[0] , encoding='utf-8')
            content = doc('.tb-inner').text().replace('\n', '').replace(' ', '').replace('\xa0', '')

            LinkUrl = i[0]
            Name = i[1]
            Legal = ''
            Category = ''
            According = ''
            Measure = ''
            UnifiedSocialCode = ''
            CreateDate = ''
            AdministrativeNumber = ''
            Area = '来宾市'

            pattern = re.compile(r'来环罚字.\d{4}.\d{1,3}号')
            match = pattern.search(content)
            if match:
                AdministrativeNumber = match.group()

            if AdministrativeNumber.strip() == '' :
                pattern2 = re.compile(r'金环罚字.\d{4}.\d{1,3}号')
                match2 = pattern2.search(content)
                if match2:
                    AdministrativeNumber = match2.group()

            if '统一社会' in content :
                Name = re.search(AdministrativeNumber+'(.*?)统一社会',content).group(1)
            elif '营业执照' in content:
                Name = re.search(AdministrativeNumber + '(.*?)营业执照', content).group(1)

            Name = Name.replace('行政处罚决定书','').replace('：','')\
                .replace('被处罚人','').replace('，','').replace(':','').replace(' ','')

            if '一、环境违法事实和证据' in content and '以上事实' in content:
                Category = re.search('一、环境违法事实和证据(.*?)以上事实',content).group(1)
            elif '一、环境违法事实和证据' in content and '以上违法事实' in content:
                Category = re.search('一、环境违法事实和证据(.*?)以上违法事实', content).group(1)


            if '二、行政处罚的依据、种类' in content and '我局决定' in content:
                According = re.search('二、行政处罚的依据、种类(.*?).我局决定',content).group(1)
            elif '二、行政处罚的依据、种类' in content and '我局对你' in content:
                According = re.search('二、行政处罚的依据、种类(.*?).我局对你', content).group(1)
            elif '二、责令改正和行政处罚的依据和种类' in content and '我局决定' in content:
                According = re.search('二、责令改正和行政处罚的依据和种类(.*?).我局决定', content).group(1)
            elif '二、责令改正和行政处罚的依据、种类' in content and '我局决定' in content:
                According = re.search('二、责令改正和行政处罚的依据、种类(.*?).我局决定', content).group(1)
            elif '二、行政处罚的依据、种类' in content and '我局拟' in content:
                According = re.search('二、行政处罚的依据、种类(.*?).我局拟', content).group(1)

            if '我局决定' in content and  '三、行政处罚履行的方式、期限' in content:
                Measure = re.search('我局决定(.*?)三、行政处罚履行的方式、期限',content).group(1)
            elif '我局决定' in content and  '三、行政处罚的履行方式和期限' in content:
                Measure = re.search('我局决定(.*?)三、行政处罚的履行方式和期限',content).group(1)
            elif '我局决定' in content and  '三、行政处罚的履行方式' in content:
                Measure = re.search('我局决定(.*?)三、行政处罚的履行方式',content).group(1)
            elif '我局决定' in content and  '三、行政处罚的履行方式、期限' in content:
                Measure = re.search('我局决定(.*?)三、行政处罚的履行方式、期限',content).group(1)
            elif '我局决定' in content and  '三、申请行政复议或者提起行政诉讼的途径和期限' in content:
                Measure = re.search('我局决定(.*?)三、申请行政复议或者提起行政诉讼的途径和期限',content).group(1)

            elif '处理决定' in content and  '三、行政处罚的履行方式和期限' in content:
                Measure = re.search('处理决定.(.*?)三、行政处罚的履行方式和期限',content).group(1)

            elif '如下行政处罚' in content and  '三、行政处罚的履行方式和期限' in content:
                Measure = re.search('如下行政处罚.(.*?)三、行政处罚的履行方式和期限',content).group(1)


            if '来宾市环境保护局' in content:
                pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
                jieshu = content.split('来宾市环境保护局')[-1]
                if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                    match3 = pattern3.search(jieshu)
                    CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')
            if CreateDate.strip() == '':
                if '金秀瑶族自治县环境保护局' in content:
                    pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
                    jieshu = content.split('金秀瑶族自治县环境保护局')[-1]
                    if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                        match3 = pattern3.search(jieshu)
                        CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')




            data = [LinkUrl,Name,Legal,Category,According,Measure,UnifiedSocialCode,CreateDate,AdministrativeNumber,Area]
            dataForDb.append(data)




getLinks()

# getDatas()

# sendDataToDb()












































