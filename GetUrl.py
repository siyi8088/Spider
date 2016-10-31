__author__='siyi'

# -*- coding:utf-8 -*-

from lxml import etree
import requests
import pymysql
import random
import time
import re

class DZDP():

    def __init__(self):
        requests.adapters.DEFAULT_RETRIES = 5
        self.url_pre='https://www.dianping.com'
        self.conn=pymysql.connect(user='root',password='siyi01',database='dzdp',charset='utf8')
        #self.user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        self.user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'

    def getResponse(self,url):
        response=requests.get(url,headers={'User-Agent':self.user_agent})
        content=response.text
        html=etree.HTML(content)
        time.sleep(random.uniform(0.3,1))
        return html

    def getUrl(self):
        cursor=self.conn.cursor()
        url=self.url_pre+'/chengdu/food'
        html=self.getResponse(url)
        list_path='//*[@id="J_nc_business"]/div[2]/div/dl/dd/ul/li/a'
        area_path='//*[@id="top"]/div[6]/div[1]/span[4]/a/span'
        sub_area_path='//*[@id="top"]/div[6]/div[1]/span[6]/a/span'
        shop_num_path='//*[@id="top"]/div[6]/div[1]/span[7]'
        category_path='//*[@id="classfy"]/a/@href'
        subcategory_path='//*[@id="classfy-sub"]/a/@href'
        items=html.xpath(list_path)
        for item in items:
            url_item=self.url_pre+item
            html_item=self.getResponse(url_item)
            area=html_item.xpath(area_path)
            sub_area=html_item.xpath(sub_area_path)
            shop_num=html_item.xpath(shop_num_path)
            if shop_num>750:
                categories=html_item.xpath(category_path)
                for category in categories:  #遍历每一个大类
                    url_category=self.url_pre+category
                    html_category=self.getResponse(url_category)
                    shop_num=html_category.xpath(shop_num_path)
                    if shop_num>750:  #店铺数量超过750,则获取小类
                        subcategories=html_category.xpath(subcategory_path)
                            for subcategory in subcategories:  #遍历每一个小类
                                url_subcategory=self.url_pre+subcategory
                                html_subcategory=self.getResponse(url_subcategory)
                                shop_num=html_subcategory.xpath(shop_num_path)
                                data=(area,sub_area,shop_num,url_subcategory)
                                cursor.execute('insert into foodurl_chengdu(area,sub_area,shop_num,url) values %s'%(data,))
                    else:
                        data=(area,sub_area,shop_num,url_category)
                        cursor.execute('insert into foodurl_chengdu(area,sub_area,shop_num,url) values %s'%(data,))
            else:
                data=(area,sub_area,shop_num,url_item)
                cursor.execute('insert into foodurl_chengdu(area,sub_area,shop_num,url) values %s'%(data,))







    def getSubregion(self):
        subregion_navs=[]
        url_region=self.url_pre+'/search/category/8/10/'
        html_region=self.getResponse(url_region)
        path_region='//*[@id="region-nav"]/a/@href'
        region_navs=html_region.xpath(path_region)
        for region_nav in region_navs:
            url_subregion=self.url_pre+region_nav
            html_subregion=self.getResponse(url_subregion)
            path_subregion='//*[@id="region-nav-sub"]/a/@href'
            results=html_subregion.xpath(path_subregion)    #获取每一个小行政区的链接
            subregion_navs+=results[1:]   #去掉第一项（不限）
        return subregion_navs

    def getSubcategory(self):
        subcategories=[]
        url_category=self.url_pre+'/search/category/8/10/'
        html_category=self.getResponse(url_category)
        path_category='//*[@id="classfy"]/a/@href'
        categories=html_category.xpath(path_category)
        for category in categories:
            url_subcategory=self.url_pre+category
            html_subcategory=self.getResponse(url_subcategory)#获取每一个小分类的链接
            path_subcategory='//*[@id="classfy-sub"]/a/@href'
            results=html_subcategory.xpath(path_subcategory)
            subcategories+=results[1:]  #去掉第一项（不限）
        return subcategories

    def getUrl(self):
        cursor=self.conn.cursor()
        subcategories=self.getSubcategory()
        subregion_navs=self.getSubregion()
        for subcategory in subcategories:
            for subregion_nav in subregion_navs:
                suffix=re.search('.*([a-z]\d+)$',subregion_nav)
                url=self.url_pre+subcategory+suffix.group(1)
                cursor.execute('insert into foodurl_chengdu(url) values ("%s")'%url)
                self.conn.commit()
        cursor.close()

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
            totalpagenum=max(pagenum)     #总共一页的没有显示页码项
        except:
            totalpagenum=1
        return totalpagenum

    def getContent(self,url):
        cursor=self.conn.cursor()
        html=self.getResponse(url)
        path='//*[@id="shop-all-list"]/ul/li'
        items=html.xpath(path)
        shop_path='div[2]/div[1]/a[1]/@title'
        area_path='div[2]/div[3]/a[2]/span'
        addr_path='div[2]/div[3]/span'
        category_path='div[2]/div[3]/a[1]/span'
        review_num_path='div[2]/div[2]/a[1]/b'
        mean_parice_path='div[2]/div[2]/a[2]/b'
        conment_path='div[2]/span/span/b'
        for item in items:
            if item:
                shop=item.xpath(shop_path)[0]
                area=item.xpath(area_path)[0].text
                addr=item.xpath(addr_path)[0].text
                category=item.xpath(category_path)[0].text
                try:
                    review_num=item.xpath(review_num_path)[0].text
                except:
                    review_num=0
                try:
                    mean_price=item.xpath(mean_parice_path)[0].text
                    mean_price=re.sub('[^\d+]','',mean_price)
                except:
                    mean_price=0
                try:
                    conment=item.xpath(conment_path)
                    taste=conment[0].text
                    env=conment[1].text
                    serve=conment[2].text
                except:
                    taste=0
                    env=0
                    serve=0
                data=(shop,area,addr,category,int(review_num),int(mean_price),float(taste),float(env),float(serve))
                #print(data)
                cursor.execute('insert into food_chengdu(shop,area,addr,category,review_num,mean_price,taste,env,serve) values%s'%(data,))
        self.conn.commit()
        cursor.close()

    def main(self):
        cursor=self.conn.cursor()
        #self.getUrl()
        try:
            f=open('/home/siyi/study/python/dzdp/ID_url_chengdu.txt','r')
            ID_url=int(f.read())
            f.close()
        except:
            ID_url=3
        url_num=cursor.execute('select * from foodurl_chengdu')
        while ID_url<=url_num:
            cursor.execute('select url from foodurl_chengdu where ID=%d'%ID_url)
            basic_url=cursor.fetchone()[0]
            totalpagenum=self.getTotalPageNum(basic_url)
            print('\n第%d个链接总共有%d页。'%(ID_url,totalpagenum))
            cursor.execute('update urllist_chengdu set total_page_num=%d where ID=%d'%(totalpagenum,ID_url))
            cursor.close
            try:
                g=open('/home/siyi/study/python/dzdp/page_chengdu.txt','r')
                start_page=int(g.read())
            except:
                start_page=1
            for page in range(start_page,totalpagenum+1):
                url=basic_url+'p'+str(page)
                print('开始抓取第%d页。'%page)
                self.getContent(url)
                print('第%d页内容已存入数据库。'%page)
                g=open('/home/siyi/study/python/dzdp/page_chengdu.txt','w')
                g.write(str(page+1))
                g.close()
            print('第%d个链接已抓取完毕。'%ID_url)
            ID_url+=1
            f=open('/home/siyi/study/python/dzdp/ID_url_chengdu.txt','w')
            f.write(str(ID_url))
            f.close()
            g=open('/home/siyi/study/python/dzdp/page_chengdu.txt','w')
            g.write('1')
            g.close()
            #key=input()
            #if key=='q':
            #    break

if __name__=='__main__':
    dianping=DZDP()
    dianping.main()
