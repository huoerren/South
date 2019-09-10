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

global data_For_Compare
data_For_Compare = []

global dataForDb
dataForDb = []


def selectData():
    sql = 'select AdministrativeNumber , Name,Category,According,Measure, CreateDate, Area from xingzhengchufa_huanan where  Area = "韶关市" '

    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306, db='greentest',charset='utf8')
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for i in result:
            data_For_Compare.append(list(i))
    except:
        print('Error')


selectData()


def sendDataToDb():
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306,db='greentest',charset='utf8')
    cur = conn.cursor()

    if len(dataForDb) >0:
        try:
            for g in dataForDb:
                print(g[0])
                sqla = '''
                        insert into  xingzhengchufa_huanan(
                                LinkUrl,Name,Legal,CreateDate,Category,According,Measure,AdministrativeNumber,UnifiedSocialCode,Area
                             ) 
                        values
                            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                    '''

                B = cur.execute(sqla,(g[0],g[1],g[2],g[3],g[4],g[5],g[6],g[7],g[8],g[9]))
                conn.commit()
                print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None


def getLinks():
    for i in range(0,1):
        if i == 0 :
            url = 'http://epb.sg.gov.cn/hjgl/hjzf/index.html'
        else:
            url = 'http://epb.sg.gov.cn/hjgl/hjzf/index_'+str(i)+'.html'

        # randdom_header = random.choice(my_headers)
        # request_doc = requests.get(url,header =randdom_header)
        doc = pq(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0'},encoding="utf-8")
        ul = doc('.comlist1.mt10.hx')
        lis = ul.children('li')
        if lis.length>0:
            for item in lis.items():
                title = item('a').attr('title')
                link  = item('a').attr('href')[1:]
                if '行政处罚决定书' in title:
                    text_urls.append([prefix+link , title])
                elif '环境行政处罚情况' in title:
                    excel_urls.append([prefix+link , title])


def getDatas():
    for i in text_urls:
        if i[0] not in unfit_urls:
            doc = pq(i[0], headers={'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)'},encoding="utf-8")
            content = doc('.TRS_Editor').text().replace('\n','').replace(' ','').replace('\xa0','')

            Name = ''
            Legal =''
            Category = ''
            According =''
            Measure = ''
            AdministrativeNumber = ''
            Area='韶关市'
            CreateDate =''
            UnifiedSocialCode = ''


            AdministrativeNumber = i[1]

            CreateDate = content.split('。')[-1].replace('韶关市环境保护局','').replace('年','-').replace('月','-').replace('日','')


            if '统一社会信用代码' in content and '地址' in content:
                UnifiedSocialCode = re.search('统一社会信用代码：(.*?)地址',content).group(1)

            if '法定代表人' in content and '一、调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况' in content:
                Legal = re.search('法定代表人：(.*?)一、调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况',content).group(1)
            elif '法定代表人' in content and '一、调查情况及发现的环境违法事实、证据' in content:
                Legal = re.search('法定代表人：(.*?)一、调查情况及发现的环境违法事实、证据', content).group(1)


            if '统一社会信用代码' in content and '韶环罚字' in content :
                Name = re.search('韶环罚字〔\d+〕第\d+号(.*?)统一社会信用代码',content).group(1)
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
                Name = re.search('(.*?)营业执照注册号', content).group(1).replace('行政处罚决定书','')
            Name = Name.replace('经营者','').replace('：','').replace('：','').replace('字号：','')


            if '一、调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况' in content and '以上事实' in content:
                Category = re.search('一、调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况(.*?)以上事实',content).group(1)
            elif '一、调查情况及发现的环境违法事实、证据' in content and '以上事实' in content:
                Category = re.search('一、调查情况及发现的环境违法事实、证据(.*?)以上事实', content).group(1)


            if '二、行政处罚的依据、种类及其履行方式、期限' in content and '依据上述规定' in content :
                According = re.search('二、行政处罚的依据、种类及其履行方式、期限(.*?)依据上述规定',content).group(1)
            elif '二、行政处罚的依据、种类及其履行方式、期限' in content and '根据上述规定' in content:
                According = re.search('二、行政处罚的依据、种类及其履行方式、期限(.*?)根据上述规定', content).group(1)


            if '根据上述规定' in content and '三、申请行政复议或者提起行政诉讼的途径和期限' in content:
                Measure = re.search('根据上述规定，(.*?)三、申请行政复议或者提起行政诉讼的途径和期限',content).group(1)
            elif '依据上述规定' in content and '' in content:
                Measure = re.search('依据上述规定，(.*?)三、申请行政复议或者提起行政诉讼的途径和期限',content).group(1)



            data_becompared = [AdministrativeNumber,Name,Category,According,Measure,CreateDate,Area]
            if data_becompared in data_For_Compare:
                print('yes ,data has been in database ! ')
            else:
                print(data_becompared)

            # data =[i[0],Name,Legal,CreateDate,Category,According,Measure,AdministrativeNumber,UnifiedSocialCode,Area]
            # dataForDb.append(data)

    for j in excel_urls:
        print(j)


getLinks()

getDatas()


# LinkUrl , Name,Legal,Category,According,Measure,UnifiedSocialCode ,CreateDate,AdministrativeNumber,Area









