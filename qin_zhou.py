#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import urllib.parse
from lxml import etree


global prefix
prefix = 'http://www.qzhb.gov.cn'  #



global unfit_urls
unfit_urls = []


global urls
urls = []


global dataForDb
dataForDb = []


def sendDataToDb():
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306,db='greentest',charset='utf8')
    cur = conn.cursor()

    if len(dataForDb) >0:
        try:
            for g in dataForDb:
                print(g[0])
                sqla = '''
                    insert into  xingzhengchufa_huanan(
                        LinkUrl,Name,Legal,Category,According,Measure,UnifiedSocialCode,CreateDate,AdministrativeNumber,Area
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

def textHandel(text,flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')
        elif flag ==2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')
    else:
        return ''


def getDataFromUrl(link, AdministrativeNumber):

    LinkUrl = link
    Name = ''
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = AdministrativeNumber
    Area = '钦州市'


    doc = pq(link , encoding='gb2312')
    title = doc('strong').text()
    td_1th = doc('#box').children('table').children('tbody').children('tr:nth-child(2)').children('td')
    td_1th_table_tr = td_1th.children('table').children('tr').children('td').children('table').children('tr:nth-child(3)')
    td_1th_table_tr_data  = td_1th_table_tr.children('td').children('table').children('tr:nth-child(3)')
    consent_02 = textHandel(td_1th_table_tr_data.text() ,2)
    consent    = textHandel(td_1th_table_tr_data.text() ,1)
    if consent_02 != None :
        match = re.search('(.*?)\n' , consent_02)
        if match:
            Name = match.group()
            if '钦州市环境保护局' == Name:
                if AdministrativeNumber in consent and '统一社会信用':
                    Name = re.search(AdministrativeNumber+ '(.*?)统一社会信用' , consent)
            print(Name)
        else:
            print('---------------')
            print(consent_02)



def get_links():
    url = 'http://www.qzhb.gov.cn/ChannelMess/PublicInfoList.aspx?ID=121'
    for k in range(1,6):  # 循环出　每一页　
        data = {
            "__EVENTTARGET": 'AspNetPager1',
            "__EVENTARGUMENT": k
        }

        content = requests.post(url, data=data)
        doc = pq(content.text)
        list_table_xxgk = doc('#list_table_xxgk')
        t_bodys = list_table_xxgk.children('tbody')

        if t_bodys.length>0:
            for tbody  in t_bodys.items():

                tr_1_th = tbody.children('tr:nth-child(1)')
                tr_1_td_4 = tr_1_th.children('td:nth-child(4)').text() # AdministrativeNumber
                AdministrativeNumber = tr_1_td_4

                tr_1_td_2_font_a = tr_1_th.children('td:nth-child(2)').children('font').children('a')
                href = tr_1_td_2_font_a.attr('href').replace('..','')
                link = prefix + urllib.parse.quote(href)
                title = textHandel(tr_1_td_2_font_a.text() ,1)

                if '行政处罚决定书' in title:
                    print([link, AdministrativeNumber])
                    # dataFlag = getDataFromUrl(link, AdministrativeNumber)
                    # if dataFlag:
                    #     break







get_links()























