__author__='siyi'

# -*- coding:utf-8 -*-

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.error import HTTPError
from selenium import webdriver
from random import uniform
from lxml import etree
import lianjia_region
import requests
import pymysql
import time
import re

class CourtUrl():

    def __init__(self,region):
        self.region=region
        self.user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
        self.conn=pymysql.connect(user='root',password='siyi01',database='lianjia',charset='utf8')
        self.base_url='http://%s.lianjia.com'%self.region
        self.area_url_path='/html/body/div[3]/div[1]/dl[2]/dd/div/div/a/@href'
        self.area_name_path='/html/body/div[3]/div[1]/dl[2]/dd/div/div/a'
        self.sub_area_url_path='/html/body/div[3]/div[1]/dl[2]/dd/div/div[2]/a/@href'
        self.sub_area_name_path='/html/body/div[3]/div[1]/dl[2]/dd/div/div[2]/a'
        self.total_court_path='/html/body/div[4]/div[1]/div[2]/h2/span'
        self.court_name_path='/html/body/div[4]/div[1]/ul/li/div[1]/div[1]/a'
        self.court_url_path='/html/body/div[4]/div[1]/ul/li/div[1]/div[1]/a/@href'
        self.total_page_path='/html/body/div[4]/div[1]/div[3]/div[2]/div/a'
        self.createtable_areaurl='create table if not exists areaurl_%s (area_id smallint not null auto_increment,area varchar(30),sub_area varchar(50),url varchar(50),primary key (area_id))'%self.region
        self.createtable_courturl='create table if not exists courturl_%s (url_id int not null auto_increment,area_id smallint not null,court_id varchar(255) not null,court_name varchar(255),url varchar(255) not null,primary key(url_id),foreign key(area_id) references areaurl_%s(area_id))'%(self.region,self.region)

    def getResponse(self,url):
        try:
            response=requests.get(url,headers={'User-Agent':self.user_agent})
            content=response.text.encode('iso8859-1').decode('utf-8')
            html=etree.HTML(content)
            time.sleep(uniform(0.3,0.5))
            return html
        except HTTPError as e:
            print(e.reason)
            return None

    def createTable(self,query):
        cursor=self.conn.cursor()
        try:
            cursor.execute(query)
        except Exception as e:
            print(Exception,e)
        finally:
            cursor.close()

    def getCourtId(self,courturls):
        result=[]
        for courturl in courturls:
            result.append(re.search('\d+',courturl).group())
        return result

    def getItem(self,html,path):
        html=self.getResponse(url)
        if html:
            items=html.xpath(path)
            return items
        else:
            print('The content of page is None.')

    def getContent(self,url,area_id):
        cursor=self.conn.cursor()
        html=self.getResponse(url)
        if html:
            court_names=html.xpath(self.court_name_path)
            urls=html.xpath(self.court_url_path)
            court_id=self.getCourtId(urls)
            for court_id,court_name,url in zip(court_id,court_names,urls):
                data=(area_id,court_id,court_name.text,url)
                #print(data)
                cursor.execute('insert into courturl_%s(area_id,court_id,court_name,url) values %s'%(self.region,data))
            self.conn.commit()
            cursor.close()
        else:
            print('The content of page is None.')

    def getTotalPage(self,url):
        driver=webdriver.Chrome()
        driver.get(url)
        #driver.implicitly_wait(5)
        try:
            items=WebDriverWait(driver,5).until(EC.presence_of_all_elements_located((By.XPATH,self.total_page_path)))
            pages=[int(item.text) for item in items if item.text!='下一页']
            return max(pages)
        except:
            return 1
        finally:
            driver.close()

    def areaUrl(self):
        cursor=self.conn.cursor()
        url=self.base_url+'/xiaoqu'
        html=self.getResponse(url)
        area_urls=html.xpath(self.area_url_path)
        area_names=html.xpath(self.area_name_path)
        for area_url,area_name in zip(area_urls,area_names):
            html1=self.getResponse(self.base_url+area_url)
            total_court=int(html1.xpath(self.total_court_path)[0].text)   #get total court num
            if total_court>3000:
                sub_area_urls=html1.xpath(self.sub_area_url_path)
                sub_area_names=html1.xpath(self.sub_area_name_path)
                for sub_area_url,sub_area_name in zip(sub_area_urls,sub_area_names):
                    data=(area_name.text,sub_area_name.text,sub_area_url)
                    print(data)
                    cursor.execute('insert into areaurl_%s(area,sub_area,url) values %s'%(self.region,data))
                self.conn.commit()
            else:
                data=(area_name.text,'null',area_url)
                print(data)
                cursor.execute('insert into areaurl_%s(area,sub_area,url) values %s'%(self.region,data))
                self.conn.commit()
        print('Perfect,you have got all urls.')
        cursor.close()

    def main(self):
        cursor=self.conn.cursor()
        self.createTable(self.createtable_areaurl)
        self.createTable(self.createtable_courturl)
        #self.areaUrl()
        cursor.execute('select max(area_id) from courturl_%s limit 1'%self.region)
        try:
            area_id=int(cursor.fetchone()[0])
        except:
            area_id=0
        cursor.execute('select area_id,url from areaurl_%s where area_id>%d'%(self.region,area_id))
        items=cursor.fetchall()
        cursor.close()
        for item in items:
            area_id=item[0]
            url=item[1]
            total_page=self.getTotalPage(self.base_url+url)
            print(url,total_page)
            try:
                with open('/home/siyi/study/python/lianjia/page_%s'%self.region,'r') as f:
                    page=int(f.read())
            except:
                page=1
            while page<=total_page:
                self.getContent(self.base_url+url+'/pg'+str(page),area_id)
                print('page %d of %s have been saved.'%(page,url))
                page+=1
                with open('/home/siyi/study/python/lianjia/page_%s'%self.region,'w') as f:
                    f.write(str(page))
            print('all the page for %s have been saved.'%url)
            with open('/home/siyi/study/python/lianjia/page_%s'%self.region,'w') as f:
                f.write('1')
        self.conn.close()
        print('OK,the commit have done.')

if __name__=='__main__':
    region=lianjia_region.getRegion()
    if region is not None:
        court_url=CourtUrl(region)
        court_url.main()
