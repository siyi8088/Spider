__author__='siyi'
# -*- coding:utf-8 -*-

import urllib
import urllib.request
import re

class Qsbk:
    
    def __init__(self):
        self.stories=[]
        self.enable=False
        self.page=1

    def getPage(self,page):
        url=r'http://www.qiushibaike.com/hot/page/'+str(page)
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36'
        headers={'User-Agent':user_agent}
        request=urllib.request.Request(url,headers=headers)
        response=urllib.request.urlopen(request)
        content=response.read().decode('utf-8')
        return content

    def getStories(self,page):
        content=self.getPage(page)
        pattern=re.compile(r'class="author.*?<h2>(.*?)</h2>.*?class="articleGender.*?(women|man)Icon.*?class="content.*?<span>(.*?)</span>.*?</a>[\n]+?(.*?)[\n]+?<div class="stats".*?class="number">(.*?)</i>',re.S)
        items=re.findall(pattern,content)
        replacebr=re.compile('<br/>')
        for item in items:
            if not item[3]:#只取没有图片的部分
                item=list(item)
                item[2]=re.sub(replacebr,'\n    ',item[2])
                self.stories.append([item[0],item[1],item[2],item[4]])

    def getOneStory(self,pagestories):
        for story in pagestories:
            key=input()
            if key=='Q':
                self.enable=False
                return
            print('    %s\n\nAuthor:%-15s Sex:%-15s 赞:%s\n'%(story[2],story[0],story[1],story[3]))
            del pagestories[0]

    def start(self):
        self.enable=True
        print('页面正在获取，请稍等……')
        self.getPage(self.page)
        self.getStories(self.page)
        if len(self.stories)>0:
            print('页面获取结束，请按回车获取段子，按Q退出！')
        while self.enable:
            pagestories=self.stories
            self.stories=[]
            self.getOneStory(pagestories)
            self.page+=1
            self.getStories(self.page)

qsbk=Qsbk()
qsbk.start()
