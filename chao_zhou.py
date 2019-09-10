#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql



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



def getLinks():
    for i in range(1,4):
        url = 'http://www.chaozhou.gov.cn/yjbh/index_'+str(i)+'.jhtml'
        headers = {
            'Cookie':'__jsluid=34e2ee2164207a3b53498c4c5a43f233; yunsuo_session_verify=f8f7767bbb89ec98f506a9a82c079ef1; clientlanguage=zh_CN; JSESSIONID=6582547A6256EDBC54CAA865351CF1D5',
                     'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7'
        }
        r = requests.get(url , headers = headers)
        doc = pq(r.text)
        table_2 = doc('#xndt-list01').children('table').children('tr').children('td').children('table:nth-child(2)')
        trs = table_2.children('tr:nth-child(2)').children('td').children('table').children('tr')
        for tr in trs.items():
            td = tr.children('td')
            link = td.children('a').attr('href')
            title = td.children('a').text()
            dataFlag = getDataFromUrl(link,title)
            if dataFlag:
                break


def getDataFromUrl(link,title):
    if link != None:
        headers = {
            'Cookie':'__jsluid=34e2ee2164207a3b53498c4c5a43f233; yunsuo_session_verify=f8f7767bbb89ec98f506a9a82c079ef1; clientlanguage=zh_CN; JSESSIONID=6582547A6256EDBC54CAA865351CF1D5',
                     'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7'
        }
        r = requests.get(link , headers = headers)
        doc = pq(r.text)
        content = doc('#zoom')
        table = content.children('table')

        LinkUrl = link
        Name = ''
        AdministrativeNumber = ''
        UnifiedSocialCode = ''
        Legal = ''
        CreateDate = ''

        Category = ''
        According = ''
        Measure = ''

        Area = '潮州市'



        if table.length >0:
            trs = table.children('tbody').children('tr')
            if trs.length > 1:
                tr_selected = table.children('tbody').children('tr:nth-child(2)')
            else:
                tr_selected = table.children('tbody').children('tr:nth-child(1)')

            if tr_selected.children('td').length == 5:
                LinkUrl = link
                Name = textHandel(tr_selected.children('td:nth-child(2)').text(),1)
                Category = textHandel(tr_selected.children('td:nth-child(3)').text() ,1)
                AdministrativeNumber = textHandel(tr_selected.children('td:nth-child(4)').text() , 1)
                Measure = textHandel(tr_selected.children('td:nth-child(5)').text() ,1)

            elif tr_selected.children('td').length == 7:
                LinkUrl = link
                Name = textHandel(tr_selected.children('td:nth-child(1)').text(), 1)
                Legal= textHandel(tr_selected.children('td:nth-child(2)').text() ,1)
                According = textHandel(tr_selected.children('td:nth-child(4)').text() ,1)
                AdministrativeNumber = textHandel(tr_selected.children('td:nth-child(5)').text(),1)
                CreateDate = textHandel(tr_selected.children('td:nth-child(6)').text().replace( '.', '-'),1)
                Measure = textHandel(tr_selected.children('td:nth-child(7)').text() ,1)

            elif tr_selected.children('td').length == 8:
                LinkUrl = link
                Name = textHandel(tr_selected.children('td:nth-child(2)').text() ,1)
                Legal= textHandel(tr_selected.children('td:nth-child(3)').text() ,1)
                Category = textHandel(tr_selected.children('td:nth-child(5)').text() ,1)
                AdministrativeNumber = textHandel(tr_selected.children('td:nth-child(6)').text() ,1)
                CreateDate = textHandel(tr_selected.children('td:nth-child(7)').text().replace( '.', '-') ,1)
                Measure = textHandel(tr_selected.children('td:nth-child(8)').text() ,1)

        elif '行政处罚决定书' in textHandel(content.text() ,1):
            text_content = textHandel(content.text() ,1)
            text_content_2=textHandel(content.text() ,2)

            pattern = re.compile(r'潮环罚字.\d{4}.\d{0,3}号')
            match = pattern.search(text_content)
            if match:
                AdministrativeNumber = match.group()

            if '法定代表人' in text_content:
                Name = re.search(AdministrativeNumber + '(.*?)法定代表人', text_content).group(1)
            elif '工商' in text_content:
                Name = re.search(AdministrativeNumber + '(.*?)工商', text_content).group(1)
            elif '营业' in text_content:
                Name = re.search(AdministrativeNumber + '(.*?)营业', text_content).group(1)
            elif '居民身份证' in text_content:
                Name = re.search(AdministrativeNumber + '(.*?)居民身份证', text_content).group(1)

            Name = Name.replace(':','').replace('：','')

            if  '环境违法行为' in text_content and  '以上违法事实' in text_content:
                Category = re.search( '环境违法行为.(.*?)以上违法事实', text_content).group(1)

            if '行政处罚的依据、种类及其履行方式和期限' in text_content and '我局' in text_content:
                According = re.search( '行政处罚的依据、种类及其履行方式和期限(.*?).我局', text_content).group(1)

            if '下行政处罚' in text_content and '你' in text_content:
                Measure = re.search('下行政处罚.(.*?)你', text_content).group(1)

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted('潮州市')  # 获得最新的本地域的 已经存在的 数据
        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
            if Name.strip() != '':
                sendDataToDb(dataToDb)
                return False


getLinks()





