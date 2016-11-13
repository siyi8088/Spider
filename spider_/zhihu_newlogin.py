#知乎登陆    报错：405

import urllib.request
from urllib.error import HTTPError,URLError
import urllib.parse
import re

def xsrftoken(url):
    response=urllib.request.urlopen(url)
    content=response.read().decode('utf-8')
    pattern=re.compile(r'_xsrf" value="(.*?)"\/>',re.S)
    xsrftoken=re.search(pattern,content)
    return xsrftoken.group(1)


def login(sxlftoken,url):
    try:
        data={'_xsrf':xsrftoken,'password':'1040101325','rememberme':'y','email':'313560020@qq.com'}
        data=urllib.parse.urlencode(data)
        data=data.encode()   #data should be bytes
        print(data)
        headers={'Connection': 'Keep-Alive','Accept': 'text/html, application/xhtml+xml, */*','Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3','User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)     Chrome/53.0.2785.116 Safari/537.36','Accept-Encoding': 'gzip, deflate','Host': 'www.zhihu.com','DNT': '1'}
        request=urllib.request.Request(url,data=data,headers=headers)
        response=urllib.request.urlopen(request)
        content=response.read()
        print(content)
    except HTTPError as e:
        print('Error code:',e.code)
    except URLError as e:
        print('Error reason:',e.reason)
    else:
        print('something wrong!')

def start():
    url='https://www.zhihu.com/'
    xsrf=xsrftoken(url)
    url+='login/email'
    login(xsrf,url)

start()
