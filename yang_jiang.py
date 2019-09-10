#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.yjepb.gov.cn/wryhjjgxx/xzcf/zjzcdcfjd'

global unfit_urls
unfit_urls = ['http://www.yjepb.gov.cn/wryhjjgxx/xzcf/zjzcdcfjd/201605/t20160511_3179.html']

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
    if link not in unfit_urls:
        LinkUrl = link
        Name = ''
        AdministrativeNumber = AdministrativeNumber
        UnifiedSocialCode = ''
        Legal = ''
        CreateDate = ''

        Category = ''
        According = ''
        Measure = ''

        Area = '阳江市'


        doc = pq(link,headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}, encoding="utf-8")

        content = ''
        content_02 = ''

        if doc('.TRS_Editor').length >1:
            doc('.TRS_Editor').find('style').remove()
            content = textHandel(doc('.TRS_Editor').text(), 1)
            content_02 = textHandel(doc('.TRS_Editor').text(), 2)
        else:
            content = textHandel(doc('.TRS_Editor').text(),1)
            content_02 =textHandel(doc('.TRS_Editor').text(),2)

        if '被处罚人' in content:
            Name = re.search('被处罚人.(\w+)',content).group(1)
        else:
            Name = re.search('(.*?)\n', content_02).group(1)
        Name = Name.replace( ':', '').replace( '：', '')

        if '信用代码' in content_02 :
            UnifiedSocialCode = re.search('信用代码.(.*?)\n',content_02).group(1)

        if '法定代表人' in content_02:
            Legal = re.search('法定代表人.(.*?)\n', content_02).group(1)
            if len(Legal) >6:
                Legal = re.search('法定代表人.(\w+)',content).group(1)

        match3 = re.search('环境违法行为.(.*?)事实' ,content)
        match4 = re.search('环境违法事实和证据.(.*?)事实', content)
        if match3:
            Category = match3.group(1).replace('以上','').replace('上述','')
        elif match4:
            Category = match4.group(1).replace('以上','').replace('上述','')


        if '二、行政处罚的依据、种类以及履行方式和期限' in content and '我局决定' in content:
            According = re.search('二、行政处罚的依据、种类以及履行方式和期限(.*?).我局决定', content).group(1)
        elif '二、行政处罚的依据、种类以及履行方式和期限' in content and '我局拟决定' in content:
            According = re.search('二、行政处罚的依据、种类以及履行方式和期限(.*?).我局拟决定', content).group(1)
        elif '责令改正和行政处罚的依据、种类'  in content and '我局决定'in content:
            According = re.search('责令改正和行政处罚的依据(.*?).我局决定', content).group(1)
        elif '行政处罚的依据、种类以及履行方式和期限'  in content and '我局'in content:
            According = re.search('行政处罚的依据、种类以及履行方式和期限(.*?).我局', content).group(1)


        if '如下处罚' in content and '根据《' in content:
            Measure = re.search( '如下处罚.(.*?)根据《', content).group(1)
        elif '如下行政处罚' in content and '根据《' in content:
            Measure = re.search( '如下行政处罚.(.*?)根据《', content).group(1)
        elif '我局决定' in content and '根据《' in content:
            Measure = re.search( '我局决定(.*?)根据《', content).group(1)
        elif '如下行政处罚' in content and '三、责令改正和行政处罚决定的履行方式和期限' in content:
            Measure = re.search( '如下行政处罚.(.*?)三、责令改正和行政处罚决定的履行方式和期限', content).group(1)
        elif '如下决定' in content and '根据' in content:
            Measure = re.search( '如下决定.(.*?)根据', content).group(1)


        if '阳江市环境保护局' in content:
            pattern2 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
            jieshu = content.split('阳江市环境保护局')[-1]
            if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                match2 = pattern2.search(jieshu)
                if match2:
                    CreateDate = match2.group().replace('年','-').replace('月','-').replace('日', '')
        # link,CreateDate,Name , AdministrativeNumber , Legal,UnifiedSocialCode  Category  According Measure  Area
        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted('阳江市')  # 获得最新的本地域的 已经存在的 数据
        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
            if Name.strip() != '':
                sendDataToDb(dataToDb)
                return False




def getLinks():
    for i in range(0,13):
        if i == 0:
            url = 'http://www.yjepb.gov.cn/wryhjjgxx/xzcf/zjzcdcfjd/index.html'
        else:
            url = 'http://www.yjepb.gov.cn/wryhjjgxx/xzcf/zjzcdcfjd/index_'+str(i)+'.html'

        doc = pq(url,encoding="utf-8")
        ul = doc('.clist dd ul')
        lls = ul.children('li')
        for li in lls.items():
            link = prefix + li('a').attr('href')[1:]
            title = li('a').attr('title')
            AdministrativeNumber = ''
            if '行政处罚' in title:
                pattern = re.compile(r'(阳环罚字.\d{4}.\d{0,4}号)')
                match = pattern.search(title)
                if match:
                    AdministrativeNumber = match.group()
                    dataFlag = getDataFromUrl(link,AdministrativeNumber)
                    if dataFlag:
                        break


getLinks()
























