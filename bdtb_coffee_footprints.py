__author__='siyi'

# -*- coding='utf-8' -*-

import urllib
import urllib.request
import re

class BDTB():

    def __init__(self,page,see_lz=1):
        self.enable=False
        self.page=page
        self.floor_num=1
        self.base_url='http://tieba.baidu.com/p/4580170978'
        self.see_lz=see_lz
        self.format_contents=[]
        self.imgs=[]

    def getPage(self,page):
        page_url=self.base_url+'?see_lz='+str(self.see_lz)+'&pn='+str(self.page)
        req=urllib.request.Request(page_url)
        response=urllib.request.urlopen(req)
        page_content=response.read().decode()
        return page_content

    def getTitle(self):
        page=1
        raw_string=self.getPage(page)
        title_p=r'<h1 class=core_title_txt.*?>(.*?)</h1>'
        pattern=re.compile(title_p,re.S)
        title=re.findall(pattern,raw_string)
        return title

    def getContents(self,page):  #获取一页的内容
        print('正在获取第%d页内容'%page)
        raw_string=self.getPage(page)
        content_p=r'class="d_post_content j_d_post_content  clearfix">(.*?)</div>'
        pattern=re.compile(content_p,re.S)
        contents=re.findall(pattern,raw_string)
        return contents

    def getImg(self,floor_num,content):  #在单层楼的内容里找图片，并保存
        img_p=r'<img.*?src="(.*?)" >'
        pattern=re.compile(img_p,re.S)
        imgs=re.findall(pattern,content)
        self.imgs.append(imgs)
        for img in imgs:   #单层楼可能包含多张图片
            num=0
            key='a'+str(floor_num)+str(num)
            if img:
                urllib.request.urlretrieve(img,'/home/siyi/study/python/bdtb/%s.jpg'%key)  #下载图片
                print('下载了%d张图片'%num)
            num+=1

    def formatContent(self,content):
        replace_p1='<br>'
        replace_p2='<img.*?" >'
        content1=re.sub(replace_p1,'\n',content)   #替换为换行符
        content2=re.sub(replace_p2,'',content1)    #替换掉图片的内容
        return content2.strip()

    def printContent(self,floor_num,content):
        print('------------------------%d楼内容-------------------'%floor_num)
        print('    '+content)

    def start(self):
        self.enable=True
        contents=[]
        title=self.getTitle()   #获取标题
        while self.enable==True:
            if len(contents)<1:
                contents=self.getContents(self.page)
                self.page+=1
            if len(contents)>1: print('内容获取成功')
            content=str(contents[0])
            del contents[0]
            self.getImg(self.floor_num,content)  #下载图片
            format_content=self.formatContent(content)    #规范内容格式
            self.format_contents.append(format_content)     #存储内容
            print('按回车获取新内容，按q退出！')
            putin=input()
            if putin=='q':
                self.enable=False
                return
            else:
                self.printContent(self.floor_num,format_content)     #打印内容
            self.floor_num+=1

coffee_footprints=BDTB(page=2)
coffee_footprints.start()
