__author__='siyi'

# -*- coding:utf-8 -*-

from urllib.error import URLError
import urllib.request
import pymysql
import time
import re

class Iask():

    def __init__(self):
        self.enable=True
        self.base_url='http://iask.sina.com.cn'
        self.q_num=1
        self.a_num=1
        self.page=1
        self.conn=pymysql.connect(user='root',password='siyi01',database='iask',charset='utf8')   #没有charset：'latin-1' codec can't encode characters in position 33-40: ordinal not in range(256)
        self.cursor=self.conn.cursor()

    #def creTable(self):
        #self.cursor.execute('create table question(ID_q smallint not null auto_increment,question blob,name_q varchar(255),time_q datetime,primary key (ID_q))')
        #self.cursor.execute('create table answer(ID_a smallint not null auto_increment,ID_q smallint not null,answer blob,name_a varchar(255),flag_g char(1),time_a datetime,primary key(ID_a),foreign key(ID_q) references question(ID_q))')
        #self.cursor.execute('create table urllist(ID_u smallint not null auto_increment,url varchar(255),primary key(ID_u))')

    def getUrl(self,start=1,end=5,content=None):
        #f=open('/home/siyi/study/python/iask.txt','w')   #改用数据库
        num=1
        for i in range(end):
            url=self.pageUrl(content)
            req=urllib.request.Request(url)
            try:
                response=urllib.request.urlopen(req)
                content=response.read().decode('utf-8')
                pattern=re.compile(r'<div class="question-title.*?<a href="(.*?)" target',re.S)
                items=re.findall(pattern,content)
                for item in items:
                    item=self.base_url+item
                    data_u=(num,item)
                    print(data_u)
                    self.insertData('urllist',data_u)
                    num+=1
                    #stop=input()   #控制过程
                self.conn.commit()
            except URLError as e:
                print('页面获取失败\n')
                if hasattr(e,'code'):
                    print('错误代码：',e.code)
                if hasattr(e,'reason'):
                    print('错误原因：',e.reason)
        #f.close()

    def pageUrl(self,content=None):
        if not content:
            url=self.base_url+'/c/187.html'
        else:
            pattern=re.compile('<a href="(.*?)" style="width: 65px">下一页</a>')
            npage=re.search(pattern,content)
            url=self.base_url+npage.group(1)
        return url

    def getContent(self,url):
        req=urllib.request.Request(url)
        response=urllib.request.urlopen(req)
        content=response.read().decode('utf-8')
        return content

    def getQuestion(self,q_num,content):
        pattern=re.compile(r'<div class="question_text">.*?">(.*?)</pre>.*?<div class="ask_autho clearfix">.*?">(.*?)</span>.*?<span class="ask-time mr10">(.*?)</span>',re.S)
        item=re.findall(pattern,content)
        try:
            item=item[0]
            text=self.getText(item[0])
            name_q=self.getQname(item[1])
            time=self.getTime(item[2])
            question=(q_num,text,name_q,time)
        except:
            question=(q_num,'此问题不是有效问题！','','1970-01-01 00:00:00')
        return question

    def getGanswer(self,q_num,content):
        pattern=re.compile(r'div class="good_answer.*?">.*?">.*?">(.*?)</a>.*?<span class="time mr10"> \| (.*?)</span>.*?answer_text">.*?">(.*?)</pre>',re.S)
        item=re.findall(pattern,content)
        if item:
            item=item[0]
            time=self.getTime(item[1])
            text=self.getText(item[2])
            ganswer=(self.a_num,q_num,text,item[0],'1',time)
        else:
            return
        return ganswer

    def getUanswer(self,q_num,content):
        uanswers=[]
        if 'recommend-info cf' in content:
            pattern=re.compile(r'<li class="clearfix">.*?answer_txt.*?">.*?">(.*?)</pre>.*?class="recommend-info cf">.*?">.*?">.*?>(.*?</span>.*?">.*?)</span>.*?class="time fl">(.*?)</span>',re.S)
        else:
            pattern=re.compile(r'<li class="clearfix">.*?answer_txt.*?">.*?">(.*?)</pre>.*?author_name">(.*?)</a>.*?answer_t">(.*?)</span>',re.S)
        items=re.findall(pattern,content)
        if items:
            for item in items:
                time=self.getTime(item[2])
                text=self.getText(item[0])
                expert=self.getExperit(item[1])
                ganswer=(self.a_num,q_num,text,expert,'0',time)
                uanswers.append(ganswer)
                self.a_num+=1
        else:
            return
        return uanswers

    def insertData(self,table,data):
        cursor=self.conn.cursor()
        cursor.execute('insert into %s values %s'%(table,data))

    def getTime(self,time0):
        if '分钟前'in time0:
            time1=re.sub('[^\d+]','',time0)
            time2=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-int(time1)*60))
        elif '小时前' in time0:
            time1=re.sub('[^\d+]','',time0)
            time2=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-int(time1)*3600))
        else:
            time2=time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(time0,'%y-%m-%d'))
        return time2

    def getText(self,text):
        text1=re.sub('[\t ]+','',text)
        text2=re.sub('[<br/>]+','\n',text1)
        text3=re.sub('[\r ]+','\n',text2)
        return text3.strip()

    def getQname(self,name):
        if '匿名' in name:
            name_q=name    #匿名提问者
        else:
            pattern=re.compile('>(.*?)</a>')
            item=re.search(pattern,name)
            name_q=item.group(1)
        return name_q

    def getExperit(self,expert):
        expert1=re.sub('[\r\t\n ]*','',expert)
        expert2=re.sub('<.*?>','-',expert1)
        return expert2

    def main(self):
        #self.getUrl()   #获取问题链接
        #self.creTable()   #创建表
        while self.enable==True:
            try:
                q=open('/home/siyi/study/python/q_num.txt','r')
                a=open('/home/siyi/study/python/a_num.txt','r')
                self.q_num=int(q.readline())
                self.a_num=int(a.readline())
                q.close()
                a.close()
            except:
                self.q_num=1
                self.a_num=1
            result=self.cursor.execute('select url from urllist where ID_u=%s'%self.q_num)    #查询问题链接
            if result==1:
                url=self.cursor.fetchone()[0]
            else:
                self.enable=False
                return
            content=self.getContent(url)    #获取问题页页面内容
            data_q=self.getQuestion(self.q_num,content)#匹配问题
            #print(data_q)
            self.insertData('question',data_q)       #插入问题至数据库
            data_ga=self.getGanswer(self.q_num,content)   #匹配好评回答
            if data_ga:
                #print(data_ga)
                self.insertData('answer',data_ga)    #插入好评回答至数据库
                self.a_num+=1
            data_ua=self.getUanswer(self.q_num,content)   #匹配普通回答
            if data_ua:
                for item in data_ua:
                    #print(item)
                    self.insertData('answer',item)   #插入普通回答至数据库
                    #self.a_num+=1   #这里无效，加在函数里
            self.q_num+=1
            self.conn.commit()
            q=open('/home/siyi/study/python/q_num.txt','w')
            a=open('/home/siyi/study/python/a_num.txt','w')
            q.write(str(self.q_num))
            a.write(str(self.a_num))
            q.close()
            a.close()
            #contrl=input()
            #if contrl=='q':
                #self.enable=False
                #return
        self.cursor.close()
        self.conn.close()

if __name__=='__main__':
    iask=Iask()
    iask.main()
