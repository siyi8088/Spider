__author__='siyi'

# -*- coding:utf-8 -*-

import urllib
import urllib.request
import re

class Pyjobs:
    
    def __init__(self):
        self.enable=False
        self.jobinfo=[]
        self.jobs=[]
        self.page=1
        self.url=r'https://www.python.org/jobs/?page='
        self.python_url=r'https://www.python.org'

    def jobInfo(self,page):
        web_url=self.url+str(self.page)
        web_request=urllib.request.Request(web_url)
        web_response=urllib.request.urlopen(web_request)
        web_content=web_response.read().decode('utf-8')
        web_pattern=re.compile(r'listing-new.*?<a href="(?P<web>.*?)">(?P<title>.*?)<\/a>.*?<br\/>(?P<company>.*?)<\/span>.*?<a href.*?>(?P<location>.*?)<\/a>.*?Posted.*?>(?P<posted>.*?)<\/time>',re.S)
        web_items=re.findall(web_pattern,web_content)
        for item in web_items:
            self.jobinfo.append([item[1].strip(),self.python_url+item[0].strip(),item[2].strip(),item[3].strip(),item[4].strip()])

    def contactInfo(self,job):
        info_url=job[1]
        info_request=urllib.request.Request(info_url)
        info_response=urllib.request.urlopen(info_request)
        info_content=info_response.read().decode('utf-8')
        p1=re.compile(r'Contact Info.*?Contact</strong>.*?:(?P<contact>.*?)<\/li>',re.S)
        p2=re.compile(r'Contact Info.*?E-mail.*?">(?P<email>.*?)<\/a>',re.S)
        p3=re.compile(r'Contact Info.*?<strong>Web</strong>.*?href=.*?>(?P<web>.*?)<\/a>',re.S)
        contact=re.findall(p1,info_content)
        if contact:contact=contact[0];contact=str(contact).strip()
        email0=re.findall(p2,info_content)
        if email0:email0=email0[0];email0=str(email0).strip()
        web=re.findall(p3,info_content)
        if web:web=web[0];web=str(web).strip()
        email_p1='<span>'
        email_p2='</span>'
        email1=re.sub(email_p1,'',email0)
        email2=re.sub(email_p2,'',email1)
        contactinfo=(contact,email2,web)
        return contactinfo

    def addInfo(self,job):
        contactinfo=self.contactInfo(job)
        job.append(contactinfo[:])
        print('已加载好联系人信息，请按回车继续：')
        return job

    def printInfo(self,job):
        key=input()
        if key=='q':
            self.enable=False
            return
        print('Job title:%s\nCompany:%-15s Location:%-15s Posted:%-15s'%(job[0],job[2],job[3],job[4]))
        if job[5][0]:
            print('Contact: %s'%job[5][0])
        if job[5][1]:
            print('E-mail: %s'%job[5][1])
        if job[5][2]:
            print('Web: %s'%job[5][2])

    def loadPage(self,page):
        if len(self.jobinfo)<1:
            print('开始获取第%d页信息\n'%self.page)
            self.jobInfo(self.page)
            self.page+=1  #第一个页面获取完成后页数加1

    def start(self):
        self.enable=True
        print('按回车获取新信息，按q退出！\n\n')
        while self.enable:
            self.loadPage(self.page)
            job=self.jobinfo[0]
            one=self.addInfo(job)
            self.printInfo(one)
            self.jobs.append(one)
            del self.jobinfo[0]


pythonjobs=Pyjobs()
pythonjobs.start()
