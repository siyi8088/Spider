__author__='siyi'

# -*- coding:utf-8 -*-

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import pymysql
import foodurl
import time
import re

class GPS():

    def __init__(self,region_path):
        self.enable=True
        self.foodurl=foodurl.URL()
        self.driver=webdriver.Chrome()
        self.conn=pymysql.connect(user='root',password='siyi01',database='dzdp',charset='utf8')
        self.url='http://api.map.baidu.com/lbsapi/getpoint/index.html'
        self.region_path=region_path

    def createTable(self,region):
        cursor=self.conn.cursor()
        try:
            cursor.execute('create table if not exists gpsdata_%s (shop_id int not null primary key,longitude decimal(6,2),latitude decimal(6,2))'%region)
            print('Ok,table have been created.')
        except Exception as e:
            print(e)
        finally:
            cursor.close()

    def getGps(self,region,addrs,cursor):
        driver=self.driver
        driver.get(self.url)
        driver.find_element_by_id('curCityText').click()
        driver.find_element_by_xpath(self.region_path).click()
        #print(driver.find_element_by_xpath('//*[@id="txtPanel"]/span').text)
        while self.enable:
            try:
                addr=next(addrs)
                #print(addr)
                driver.find_element_by_id('localvalue').send_keys(addr[1])
                driver.find_element_by_id('localsearch').click()
                time.sleep(1)
                try:
                    item=WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="no_0"]/p'))).text
                    #print(item)
                    items=re.sub('^[\S\s]+：','',item).split(',')
                    data=(addr[0],items[0],items[1])
                except Exception as e:
                    data=(addr[0],0,0)
                    print(e)
                #print(data)
                cursor.execute('insert into gpsdata_%s values %s'%(region,data))
            except Exception as e:
                self.enable=False
                print(e)
            finally:
                driver.find_element_by_id('localvalue').clear()

    def getAddrs(self,region):
        cursor=self.conn.cursor()
        cursor.execute('select max(shop_id) from gpsdata_%s'%region)
        shop_id=cursor.fetchone()[0]
        if not shop_id:
            shop_id=0
        cursor.execute('select shop_id,addr from food_%s where shop_id>%d'%(region,shop_id))
        addrs=iter(cursor.fetchall())
        cursor.close()
        return addrs

    def main(self):
        cursor=self.conn.cursor()
        region=self.foodurl.getRegion()
        self.createTable(region)
        addrs=self.getAddrs(region)
        try:
            self.getGps(region,addrs,cursor)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            self.conn.close()
            self.driver.close()

if __name__=='__main__':
    region_path='//*[@id="selCity"]/tbody/tr[25]/td[2]/nobr[1]/a'
    getgps=GPS(region_path)
    getgps.main()
