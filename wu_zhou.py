#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import  urllib

global prefix
prefix = 'http://www.gxwzepb.gov.cn/'

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



def textHandel(text,flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')
        elif flag ==2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')
    else:
        return ''



def getDataFromUrl(link):
    if '行政处罚' in link:
        doc = pq(link , encoding='gb2312')
        head_text = doc('font').text()
        if '查封' not in head_text:
            tab_trs = doc('#box').children('table').children('tbody').children('tr:nth-child(2)')
            tab_trs_tab_tr_td = tab_trs.children('td').children('table').children('tr').children('td')
            tab_trs_tab_tr_td_tab_tr = tab_trs_tab_tr_td.children('table').children('tr:nth-child(3)')
            tab_trs_tab_tr_td_tab_tr_td_table = tab_trs_tab_tr_td_tab_tr.children('td').children('table')
            tab_trs_tab_tr_td_tab_tr_td_table_tr_3 = tab_trs_tab_tr_td_tab_tr_td_table('tr:nth-child(3)')

            content = textHandel(tab_trs_tab_tr_td_tab_tr_td_table_tr_3.text() , 1)
            content_2 = textHandel(tab_trs_tab_tr_td_tab_tr_td_table_tr_3.text() , 2)

            LinkUrl = link

            Name = ''
            AdministrativeNumber = ''
            UnifiedSocialCode = ''
            Legal = ''
            CreateDate = ''

            Category = ''
            According = ''
            Measure = ''

            Area = '梧州市'

            if '当事人' in content_2:
                Name = re.search('当事人.(.*?)\n' , content_2).group(1)
            Name = Name.replace('称：' , '')

            if '信用代码' in content_2:
                UnifiedSocialCode = re.search('信用代码.(.*?)\n',content_2).group(1)

            if '法定代表人' in content_2:
                Legal = re.search( '法定代表人.(.*?)\n', content_2).group(1)
                Legal = Legal.replace( '负责人）：', '')

            pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
            if '梧州市环境保护局' in content:
                jieshu = content.split('梧州市环境保护局')[-1]
                if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                    match = pattern.search(jieshu)
                    if match:
                        CreateDate = match.group().replace('年', '-').replace('月', '-').replace('日', '')

            pattern2 = re.compile(r'梧环罚字.\d{4}.\d{0,3}号')
            match2 = pattern2.search(content)
            if match2:
                AdministrativeNumber = match2.group()

            if '环境违法事实和证据' in content and '以上事实' in content:
                Category = re.search('环境违法事实和证据(.*?)以上事实' ,content).group(1)
            elif '违法事实和证据' in content and '证据材料有' in content:
                Category = re.search('违法事实和证据(.*?)证据材料有', content).group(1)
            elif '违法事实和证据' in content and '上述行为' in content:
                Category = re.search('违法事实和证据(.*?)上述行为', content).group(1)

            if '行政处罚的依据、种类' in content and '的规定，' in content:
                According = re.search('行政处罚的依据、种类(.*?)的规定',content).group(1)
                According = According+"的规定"

            if '我局决定' in content and '行政处罚的履行方式' in content:
                Measure = re.search('我局决定(.*?)行政处罚的履行方式',content).group(1)


            #link,Name ,AdministrativeNumber , UnifiedSocialCode ,Legal,CreateDate  Category  According

            print([link, Measure])


def getLinks():
    filePath = 'http://www.gxwzepb.gov.cn/ChannelMess/List.aspx?Channel_ID=198'

    for k in range(1,7):  # 循环出　每一页　
        data = {
            "__EVENTARGUMENT": k,
            "__EVENTTARGET": "ctl00$ContentPlaceHolder_middle$AspNetPager1"
        }
        print('==============================')
        content = requests.post(filePath, data=data)
        doc = pq(content.text)
        ul = doc('.list02').children('ul')
        lis = ul.children('li')
        for li in lis.items():
            href = li.children('a').attr('href').replace( '../', '')
            # href  = urllib.parse.quote(href_mix).replace( '../', '')
            link = prefix + href
            # print([link])
            dataFlag = getDataFromUrl(link)
            # if dataFlag:
            #     break



getLinks()













































