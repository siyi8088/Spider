__author__='siyi'

# -*- coding:utf-8 -*-

from lxml import etree
import requests
import pymysql
import random
import foodurl
import time
import re

class DZDP():

    def __init__(self):
        self.foodurl=foodurl.URL()
        requests.adapters.DEFAULT_RETRIES = 5
        self.url_pre='https://www.dianping.com'
        self.conn=pymysql.connect(user='root',password='siyi01',database='dzdp',charset='utf8')
        #self.user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        self.user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
        self.path='//*[@id="shop-all-list"]/ul/li'
        self.shop_path='div[2]/div[1]/a[1]/@title'
        self.area_path='div[2]/div[3]/a[2]/span'
        self.addr_path='div[2]/div[3]/span'
        self.category_path='div[2]/div[3]/a[1]/span'
        self.review_num_path='div[2]/div[2]/a[1]/b'
        self.mean_parice_path='div[2]/div[2]/a[2]/b'
        self.conment_path='div[2]/span/span/b'

    def createTable(self,region):
        flag=1
        cursor=self.conn.cursor()
        try:
            cursor.execute('create table food_%s (shop_id int not null auto_increment,url_id int,shop varchar(255) not null,area varchar(255),addr varchar(255),category varchar(255),review_num int,mean_price smallint,taste decimal(4,2),env decimal(4,2),serve decimal(4,2),primary key(shop_id),foreign key(url_id) references foodurl_%s(url_id))'%(region,region))
            cursor.close()
        except Exception as e:
            print(Exception,e)
            flag=0
        return flag

    def getResponse(self,url):
        response=requests.get(url,headers={'User-Agent':self.user_agent})
        content=response.text
        html=etree.HTML(content)
        time.sleep(random.uniform(0.3,1))
        return html

    def Tool(self,strings):#去掉人民币符号
        items=[]
        for string in strings:
            item=re.sub('[^\d+]','',string.text)
            items.append(item)
        return items

    def getTotalPageNum(self,url):
        pagenum=[]
        html=self.getResponse(url)
        items=html.xpath('//*[@id="top"]/div[6]/div[3]/div[1]/div[2]/a')
        for item in items:
            try:
                pagenum.append(int(item.text))
            except:
                pass
        try:
            totalpagenum=max(pagenum)
        except:
            totalpagenum=1   #there is not exists the page number button if the content just have only one page.
        return totalpagenum

    def saveContent(self,url_id,url,region):
        cursor=self.conn.cursor()
        html=self.getResponse(url)
        items=html.xpath(self.path)
        for item in items:
            if item:
                shop=item.xpath(self.shop_path)[0]
                area=item.xpath(self.area_path)[0].text  #some area is missed..fuck..
                if not area:
                    area='null'
                addr=item.xpath(self.addr_path)[0].text
                if not addr:
                    addr='null'
                category=item.xpath(self.category_path)[0].text
                if not category:
                    category='null'
                try:
                    review_num=item.xpath(self.review_num_path)[0].text
                except:
                    review_num=0
                try:
                    mean_price=item.xpath(self.mean_parice_path)[0].text
                    mean_price=re.sub('[^\d+]','',mean_price)
                except:
                    mean_price=0
                try:
                    conment=item.xpath(self.conment_path)
                    taste=conment[0].text
                    env=conment[1].text
                    serve=conment[2].text
                except:
                    taste=0
                    env=0
                    serve=0
                data=(url_id,shop,area,addr,category,int(review_num),int(mean_price),float(taste),float(env),float(serve))
                #print(data)
                cursor.execute('insert into food_%s(url_id,shop,area,addr,category,review_num,mean_price,taste,env,serve) values%s'%(region,data))
        self.conn.commit()
        cursor.close()

    def getData(self,region,url_num):
        cursor=self.conn.cursor()
        try:
            f=open('/home/siyi/study/python/dzdp/urlid_%s.txt'%region,'r')
            url_id=int(f.read())
            f.close()
        except:
            url_id=1
        while url_id<url_num+url_id-1:
            cursor.execute('select * from foodurl_%s where URL_ID=%d'%(region,url_id))
            url_info=cursor.fetchone()
            #print(url_info)
            if url_info[3]:
                totalpagenum=self.getTotalPageNum(url_info[4])
                print('\n--------The total page number of URL %d is %d.--------'%(url_id,totalpagenum))
                try:
                    g=open('/home/siyi/study/python/dzdp/page_%s.txt'%region,'r')
                    start_page=int(g.read())
                except:
                    start_page=1
                for page in range(start_page,totalpagenum+1):
                    url=url_info[4]+'p'+str(page)
                    print(time.asctime(time.localtime()),'  The page %d is beginning to crawl.'%page)
                    self.saveContent(url_id,url,region)
                    print(time.asctime(time.localtime()),'  The contnet of page %d have been saved.'%page)
                    g=open('/home/siyi/study/python/dzdp/page_%s.txt'%region,'w')
                    g.write(str(page+1))
                    g.close()
                print(time.asctime(time.localtime()),'  The content of URL %d have benn saved.'%url_id)
            else:
                print('The shop number of this URL is 0, let go to next URL...')
            url_id+=1
            f=open('/home/siyi/study/python/dzdp/urlid_%s.txt'%region,'w')
            f.write(str(url_id))
            f.close()
            g=open('/home/siyi/study/python/dzdp/page_%s.txt'%region,'w')
            g.write('1')
            g.close()
        cursor.close()
        self.conn.close()

    def main(self):
        cursor=self.conn.cursor()
        region=self.foodurl.getRegion()
        try:
            url_num=cursor.execute('select * from foodurl_%s'%region)
            cursor.close()
        except Exception as e:
            print(Exception,e)
            return
        if True: # self.createTable(region):
            self.getData(region,url_num)


if __name__=='__main__':
    dianping=DZDP()
    dianping.main()
