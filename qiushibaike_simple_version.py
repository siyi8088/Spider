import urllib.request
import re
user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36'
headers={'User-Agent':user_agent}
url='http://www.qiushibaike.com/hot/page/1/'
request=urllib.request.Request(url,headers)
response=urllib.urlopen(request)
content=response.read().decode('utf-8')
pattern=re.compile(r'class="author.*?<h2>(.*?)</h2>.*?class="articleGender.*?(women|man)Icon.*?class="content.*?<span>(.*?)</span>.*?</a>[\n]+?(.*?)[\n]+?<div class="stats".*?class="number">(.*?)</i>',re.S)
items=re.findall(pattern,content)

