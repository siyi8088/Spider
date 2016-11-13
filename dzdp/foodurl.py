__author__='siyi'

# -*- coding:utf-8 -*-

from urllib.error import HTTPError
from selenium import webdriver
from pandas import Series
from lxml import etree
import requests
import pymysql
import random
import time
import sys
import re

class URL():

    def __init__(self):
        requests.adapters.DEFAULT_RETRIES = 5
        self.url_pre='https://www.dianping.com'
        self.conn=pymysql.connect(user='root',password='siyi01',database='dzdp',charset='utf8')
        #self.user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        self.user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
        self.test_path='//*[@id="J_nc_business"]/div[2]/div/dl[1]/dd/ul/li[1]/a'
        self.list_path='//*[@id="J_nc_business"]/div[2]/div/dl'
        self.area_path='//*[@id="top"]/div[6]/div[1]/span[4]/a/span'
        self.sub_area_path='//*[@id="top"]/div[6]/div[1]/span[6]/a/span'
        self.shop_num_path='//*[@id="top"]/div[6]/div[1]/span'
        self.category_path='//*[@id="classfy"]/a/@href'
        self.subcategory_path='//*[@id="classfy-sub"]/a/@href'

    def createTable(self,region):
        flag=1
        cursor=self.conn.cursor()
        try:
            cursor.execute('create table if not exists foodurl_%s(url_id int not null auto_increment,area varchar(255),sub_area varchar(255),shop_num smallint,url varchar(255),primary key(url_id))'%region)
            cursor.close()
        except Exception as e:
            flag=0
            print(e)
        return flag

    def getResponse(self,url):
        try:
            response=requests.get(url,headers={'User-Agent':self.user_agent})
        except HTTPError as e:
            print('获取网页失败!')
            return None
        content=response.text
        html=etree.HTML(content)
        time.sleep(random.uniform(0.3,1))
        return html

    def getPageUrl(self,url):
        pageurls=[]
        driver=webdriver.Chrome()
        driver.get(url)
        key=driver.find_element_by_xpath(self.test_path)
        if key:
            content=driver.page_source
            html=etree.HTML(content)
            items=html.xpath(self.list_path)
            for item in items:
                if item.xpath('./dd/span'):
                    pageurls.extend(item.xpath('./dt/a/@href'))  #append会直接添加列表进去,而extend是添加元素进去
                else:
                    pageurls.extend(item.xpath('./dd/ul/li/a/@href'))
            return iter(pageurls)
        driver.close()

    def tool(self,string):
        string=str(string)
        return int(re.sub('[^\d]','',string))

    def getUrl(self,region,pageurls):
        cursor=self.conn.cursor()
        for item in pageurls:
            #print(item)
            url_item=self.url_pre+item
            html_item=self.getResponse(url_item)
            area=html_item.xpath(self.area_path)[0].text
            try:
                sub_area=html_item.xpath(self.sub_area_path)[0].text
                shop_num_path_flag=7    #shop_num的位置标志,7表示有二级分区,5表示无二级分区
            except:
                sub_area='null'
                shop_num_path_flag=5
            shop_num=html_item.xpath(self.shop_num_path+'[%d]'%shop_num_path_flag)[0].text
            shop_num=self.tool(shop_num)
            if shop_num>750:
                categories=html_item.xpath(self.category_path)
                for category in categories:  #遍历每一个大类
                    url_category=self.url_pre+category
                    html_category=self.getResponse(url_category)
                    shop_num=html_category.xpath(self.shop_num_path+'[%d]'%(shop_num_path_flag+2))[0].text
                    shop_num=self.tool(shop_num)
                    if shop_num>750:  #店铺数量超过750,则获取小类
                        subcategories=html_category.xpath(self.subcategory_path)[1:]
                        for subcategory in subcategories:  #遍历每一个小类
                            url_subcategory=self.url_pre+subcategory
                            html_subcategory=self.getResponse(url_subcategory)
                            shop_num=html_subcategory.xpath(self.shop_num_path+'[%d]'%(shop_num_path_flag+4))[0].text
                            shop_num=self.tool(shop_num)
                            data=(area,sub_area,shop_num,url_subcategory)
                            print(time.asctime(time.localtime()),data)
                            cursor.execute('insert into foodurl_%s(area,sub_area,shop_num,url) values %s'%(region,data))
                        self.conn.commit()
                    else:
                        data=(area,sub_area,shop_num,url_category)
                        print(time.asctime(time.localtime()),data)
                        cursor.execute('insert into foodurl_%s(area,sub_area,shop_num,url) values %s'%(region,data))
                self.conn.commit()
            else:
                data=(area,sub_area,shop_num,url_item)
                print(time.asctime(time.localtime()),data)
                cursor.execute('insert into foodurl_%s(area,sub_area,shop_num,url) values %s'%(region,data))
            self.conn.commit()
        print('You have done.')
        cursor.close()
        self.conn.close()

    def getRegion(self):
        regions=Series(['beijing','shanghai','shenzhen','chengdu','chongqing'])
        print('The avairable regions are:')
        print(regions)
        print('Please input the region number that you want to crawl. Or q for quit')
        key=input()
        if key=='q':
            print('You have made a bad choice..So Byebye..')
            return None
        else:
            print('OK, let beginning...')
            return regions[int(key)]

    def main(self):
        region=self.getRegion()
        if region:
            if self.createTable(region):
                #handler=open('/home/siyi/study/python/dzdp/foodurl_%s.log'%self.region,'w')
                #sys.stdout=handler
                url=self.url_pre+'/%s/food'%region
                pageurls=self.getPageUrl(url)
                self.getUrl(region,pageurls)


if __name__=='__main__':
    geturl=URL()
    geturl.main()
