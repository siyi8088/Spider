# -*- coding:utf-8 -*-

import requests
from lxml import etree
import time
import pymysql

class ExtraUrl():

    def __init__(self):
        self.conn=pymysql.connect(user='root',password='siyi01',database='dzdp',charset='utf8')
        self.user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
        self.url_path='//*[@id="region-nav"]/a/@href'
        self.area_path='//*[@id="region-nav"]/a/span'

    def getResponse(self,url):
        response=requests.get(url,headers={'User-Agent':self.user_agent})
        content=response.text
        html=etree.HTML(content)
        time.sleep(1) 
        return html

    def main(self):
        cursor=self.conn.cursor()
        base_url='http://www.dianping.com'
        extra=['http://www.dianping.com/search/category/1/10/g133','http://www.dianping.com/search/category/1/10/g134']
        for item in extra:
            html=self.getResponse(item)
            urls=html.xpath(self.url_path)
            items=html.xpath(self.area_path)
            areas=[]
            for item in items:
                areas.append(item.text)
            for area,url in zip(areas,urls):
                data=(area,'',0,base_url+url)
                #print(data)
                cursor.execute('insert into foodurl_shanghai(area,sub_area,shop_num,url) values %s'%(data,))
            self.conn.commit()
        cursor.close()
        self.conn.close()

if __name__=='__main__':
    extra=ExtraUrl()
    extra.main()
