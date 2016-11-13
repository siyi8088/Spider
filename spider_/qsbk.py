__author__='siyi'

# -*-coding:utf-8 -*-

import pymysql
import requests
from bs4 import BeautifulSoup

class QSBK():

    def __init__(self):
        self.page=1
        self.basic_url='http://www.qiushibaike.com/hot/page/'
        self.enable=False

    def getPage(self,page):
        url=self.basic_url+str(page)
        response=requests.get(url)
        content=response.text
        soup=BeautifulSoup(content)
        return soup

    def getAuthor(self,soup):
        authors=[]
        items=soup.select('#conent-left > div > div > a:nth-of-type(2) > h2')
        for item in items:
            authors.append(item.get_text())

    def 

