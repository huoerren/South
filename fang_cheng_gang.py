#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix_1
prefix_1 = 'http://fcg.gxepb.gov.cn/'  # ../../

global prefix_2
prefix_2 = 'http://fcg.gxepb.gov.cn/hjzf/xzcf/'  #./

global unfit_urls
unfit_urls = ['http://fcg.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/zjcfjd/201807/t20180716_43918.html',
              'http://fcg.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/zjcfjd/201607/t20160712_26880.html',
              'http://fcg.gxepb.gov.cn/wryhjjgxxgk/xxgkxzcf/zjcfjd/201807/t20180720_44062.html']


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
    for i in range(0,11):
        if i == 0:
            url = 'http://fcg.gxepb.gov.cn/hjzf/xzcf/'
        else:
            url = 'http://fcg.gxepb.gov.cn/hjzf/xzcf/index_'+str(i)+'.html'

        doc = pq(url,encoding='utf-8')
        ul = doc('.list-ctn ul')
        lis = ul.children('li')
        for i in lis.items():
            title = i.children('a').text()
            if '行政处罚决定书' in title:
                AdministrativeNumber = ''
                title_sub = ''
                href = i.children('a').attr('href')
                if '../../' in href:
                    link = prefix_1 + href.replace('../../','').replace('./','')
                else:
                    link = prefix_2 + href.replace('../../', '').replace('./', '')

                dataFlag = getDataFromUrl(link, title)
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
    if link not in unfit_urls:
        doc = pq(link, encoding='utf-8')
        content = textHandel(doc('.tb-inner').text() , 1)
        pattern = re.compile(r'防环罚字.\d{4}.\d{1,3}号')
        match2 = pattern.search(content)

        LinkUrl = link
        Name = ''
        Legal = ''

        Category = ''
        According = ''
        Measure = ''

        UnifiedSocialCode = ''
        CreateDate = ''
        AdministrativeNumber = ''
        Area = '防城港市'

        if match2:
            AdministrativeNumber = match2.group()

        if '营业执照' in content:
            Name = re.search(AdministrativeNumber+'(.*?)营业执照',content).group(1)
        if '统一社会信用代码' in Name:
            Name = Name.split('统一社会信用代码')[0]
        Name = Name.replace('：','').replace('被处罚单位','')

        if '一、环境违法事实和证据' in content and '以上事实' in content:
            Category = re.search('一、环境违法事实和证据(.*?)以上事实', content).group(1)
        elif '违法行为' in content and '以上违法事实'  in content:
            Category = re.search('违法行为.(.*?)以上违法事实',content).group(1)
        elif '违法行为' in content and '以上事实'  in content:
            Category = re.search('违法行为.(.*?)以上事实',content).group(1)


        if '二、行政处罚的依据、种类' in content and '的规定' in content:
            According = re.search('二、行政处罚的依据、种类.(.*?)的规定.',content).group(1)
        elif '二、责令停止违法行为和行政处罚的依据、种类' in content and '的规定' in content:
            According = re.search('二、责令停止违法行为和行政处罚的依据、种类(.*?)的规定.', content).group(1)

        elif '依据《' in content and '相关精神' in content:
            According = re.search('依据《(.*?)相关精神', content).group(0)
        elif '根据《' in content and '相关精神' in content:
            According = re.search('根据《(.*?)相关精神', content).group(0)

        elif '依据《' in content and '我局决定对' in content:
            According = re.search('依据《(.*?).我局决定对', content).group(0)
            According = According.replace('我局决定对', '')

        elif '根据《' in content and '我局决定对' in content:
            According = re.search('根据《(.*?).我局决定对', content).group(0)
            According = According.replace('我局决定对','')

        elif '依据《' in content and '我局对' in content:
            According = re.search('依据《(.*?).我局对', content).group(0)
            According = According.replace('我局对','')

        elif '根据《' in content and '我局对' in content:
            According = re.search('根据《(.*?).我局对', content).group(0)
            According = According.replace('我局对','')

        if '我局决定对' in content and '三、处罚决定的履行方式和期限' in content:
            Measure = re.search( '我局决定对(.*?)三、处罚决定的履行方式和期限', content).group(1)
        elif '我局决定对' in content and '。' in content:
            Measure = re.search( '我局决定对(.*?)。', content).group(1)
        elif '如下行政处罚' in content and '履行方式' in content:
            Measure = re.search( '如下行政处罚.(.*?)履行方式', content).group(1)

        elif '如下决定' in content and '（一）自接到' in content:
            Measure = re.search( '如下决定.(.*?)（一）自接到', content).group(1)
        elif '如下行政处罚' in content and '（一）自接到' in content:
            Measure = re.search( '如下行政处罚.(.*?)（一）自接到', content).group(1)

        elif '如下行政处罚' in content and '根据《' in content:
            Measure = re.search( '如下行政处罚.(.*?)根据《', content).group(1)
        elif '如下决定' in content and '根据《' in content:
            Measure = re.search( '如下决定.(.*?)根据《', content).group(1)
        elif '如下处理' in content and '根据《' in content:
            Measure = re.search( '如下处理.(.*?)根据《', content).group(1)





        if '防城港市环境保护局' in content:
            pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
            jieshu = content.split('防城港市环境保护局')[-1]
            if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                match3 = pattern3.search(jieshu)
                CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')


        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted('防城港市')  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
            if Name.strip() != '':
                sendDataToDb(dataToDb)
                return False




getLinks()













































