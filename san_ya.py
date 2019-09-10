#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import  requests
import json

global dataForDb
dataForDb = []


def getValue(val):
    if str(val)== 'None':
        val = ''
    else:
        val = val.strip()
    return val


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
    for i in range(1,9):
        param ={
            'sitecode':'sthjsite',
            'pageSize':15,
            'page':i
        }
        resp = requests.get('http://hbj.sanya.gov.cn/b/sgs/xzcflist',params=param)
        href ='http://hbj.sanya.gov.cn/sthjsite/cfgs/cfdetail.shtml?id='
        for j in resp.json()['list']:
            LinkUrl = href + str(j['id'])
            getValue(j['cf_fr'])
            Name = getValue(j['cf_xdr_mc'])
            Legal = getValue(j['cf_fr'])
            Category = getValue(j['cf_sy'])
            According = getValue(j['cf_yj'])
            Measure   = getValue(j['cf_jg'])
            UnifiedSocialCode =  getValue(j['cf_xdr_shxym'])
            CreateDate = getValue(j['cf_jdrq'])
            AdministrativeNumber = getValue(j['cf_wsh'])
            Area = '三亚市'

            dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
            data_For_Compare = getDataExisted('三亚市')  # 获得最新的本地域的 已经存在的 数据

            if dataFromPage in data_For_Compare:
                return True
            else:
                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area]
                if Name.strip() != '':
                    sendDataToDb(dataToDb)

getLinks()




















