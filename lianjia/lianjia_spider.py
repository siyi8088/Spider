__author__='siyi'

# -*- coding:utf-8 -*-

from requests.exceptions import MissingSchema
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pandas.io.sql as sql
from random import uniform
import lianjia_region
import requests
import pymysql
import time
import json
import re


class LianJia():

    def __init__(self,region):
        self.region=region
        self.conn=pymysql.connect(user='root',password='siyi01',database='lianjia',charset='utf8')
        #self.user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
        self.createtable_court_info='create table court_info_%s (court_id varchar(255) not null primary key,url_id int not null,building_age varchar(50),building_type varchar(50),property_fee varchar(255),property_company varchar(255),developer varchar(255),building_num smallint,hosehold_num int,longitude decimal(8,4),latitude decimal(8,4),sub_area varchar(50),court_addr varchar(255),foreign key(url_id) references courturl_%s(url_id))'%(self.region,self.region)
        self.createtable_court_price='create table court_price_%s (court_id varchar(255) not null primary key,url_id int not null,nov_2015 decimal(8,2),dec_2015 decimal(8,2),jan_2016 decimal(8,2),feb_2016 decimal(8,2),mar_2016 decimal(8,2),apr_2016 decimal(8,2),may_2016 decimal(8,2),jun_2016 decimal(8,2),jul_2016 decimal(8,2),aug_2016 decimal(8,2),sep_2016 decimal(8,2),oct_2016 decimal(8,2),foreign key(url_id) references courturl_%s(url_id))'%(self.region,self.region)
        self.court_addr_selector='body > div.xiaoquDetailHeader > div > div.detailHeader.fl > div'
        self.sub_area_selector='body > div.xiaoquDetailbreadCrumbs > div.fl.l-txt > a:nth-of-type(4)'
        self.court_info_selector='body > div.xiaoquOverview > div.xiaoquDescribe.fr > div.xiaoquInfo > div > span.xiaoquInfoContent'

    def getResponse(self,url):
        headers={
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'en-US,en;q=0.8',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Cookie':'lianjia_uuid=afaae707-89a7-4b5f-bdb0-fc80b6c9a027; gr_user_id=d961bca9-a8d9-4cb4-9968-91169f19b1e0; ubta=2299869246.2048440784.1478698085530.1478964249828.1478964251054.9; _jzqckmp=1; select_city=510100; all-lj=59dc31ee6d382c2bb143f566d268070e; gr_session_id_a1a50f141657a94e=e537b9ea-8cfb-4b70-ad9c-5c55b812f26b; _smt_uid=58232480.55700ff3; CNZZDATA1253492306=1462247063-1478694776-http%253A%252F%252Fsh.lianjia.com%252F%7C1478997788; _gat=1; _gat_past=1; _gat_global=1; _gat_new_global=1; _ga=GA1.2.1782554846.1478698085; _gat_dianpu_agent=1; CNZZDATA1254525948=1158831448-1478694866-http%253A%252F%252Fsh.lianjia.com%252F%7C1479002667; CNZZDATA1255633284=170911731-1478696014-http%253A%252F%252Fsh.lianjia.com%252F%7C1478998435; CNZZDATA1255604082=287803517-1478697642-http%253A%252F%252Fsh.lianjia.com%252F%7C1479000063; _jzqa=1.990290716351762300.1478698114.1478998562.1479002815.15; _jzqc=1; _jzqx=1.1478698114.1479002815.10.jzqsr=sh%2Elianjia%2Ecom|jzqct=/.jzqsr=captcha%2Elianjia%2Ecom|jzqct=/; _jzqb=1.1.10.1479002815.1; _qzja=1.1191601760.1478698114566.1478998561835.1479002814742.1478998561835.1479002814742.0.0.0.99.15; _qzjb=1.1479002814741.1.0.0.0; _qzjc=1; _qzjto=2.2.0; lianjia_ssid=ecd9ea2c-3173-4046-8e33-389c9cbcadfc',
                'Host':'cd.lianjia.com',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
                }
        try:
            response=requests.get(url,headers=headers)
            content=response.text.encode('iso8859-1').decode('utf-8')
            time.sleep(uniform(0.8,1.1))
            return content
        except MissingSchema:
            url=re.sub('/cd','http://cd.lianjia.com',url)
            content=self.getResponse(url)
            return content
        except HTTPError as e:
            print(e.reason)

    def getInfo(self,soup,court_id,url_id):
        cursor=self.conn.cursor()
        sub_area=soup.select(self.sub_area_selector)[0].string
        court_addr=soup.select(self.court_addr_selector)[0].string
        items=soup.select(self.court_info_selector)    #主要的基本信息
        court_info=[]
        for item in items:
            court_info.append(item.string)
        del court_info[-1]
        court_info[5]=re.sub('[^\d]+','',court_info[5])
        court_info[6]=re.sub('[^\d]+','',court_info[6])
        try:
            court_info.extend(re.search('mendian="(.*?)"',str(items[7].contents)).group(1).split(','))  #经纬度数据
        except:
            court_info.extend([0,0])
        data=(court_id,url_id)+tuple(court_info[:])+(sub_area,court_addr)
        #print(data)
        cursor.execute('insert into court_info_%s values %s'%(self.region,data))
        cursor.close()

    def getPrice(self,court_id,url_id):
        cursor=self.conn.cursor()
        url='http://cs.lianjia.com/fangjia/priceTrend/c'+court_id  #获取一年的价格数据链接
        content=self.getResponse(url)
        price=json.loads(content)
        elements=price['currentLevel']['dealPrice']['total']
        result=tuple([0 if ele is None else ele for ele in elements])
        data=(court_id,url_id)+result
        #print(data)
        cursor.execute('insert into court_price_%s values %s'%(self.region,data))
        cursor.close()

    def createTbale(self,query):
        cursor=self.conn.cursor()
        try:
            cursor.execute(query)
        except Exception as e:
            print(Exception,e)
        finally:
            cursor.close()

    def main(self):
        self.createTbale(self.createtable_court_info)
        self.createTbale(self.createtable_court_price)
        cursor=self.conn.cursor()
        try:
            cursor.execute('select max(url_id) from court_info_%s'%self.region)  #取出已经获取过的链接的最大编号
            url_id=cursor.fetchall()[0][0]
        except:
            url_id=0
        print(url_id)
        courturl_info=sql.read_sql('select url_id,court_id,url from courturl_%s where url_id>%d'%(self.region,url_id),self.conn)
        key=0
        while key<len(courturl_info):
            result=courturl_info.ix[key]
            content=self.getResponse(result[2])
            soup=BeautifulSoup(content,'lxml')
            self.getInfo(soup,result[1],result[0])
            self.getPrice(result[1],result[0])
            self.conn.commit()
            print('The infomation of court_id (%s) have been saved.'%result[2])
            key+=1
        print('You have got all the court infomation of %s'%self.region)


if __name__=='__main__':
    region=lianjia_region.getRegion()
    if region is not None:
        lianjia=LianJia(region)
        lianjia.main()
