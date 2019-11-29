import sys,time
import re           #正则匹配
from bs4 import BeautifulSoup
import requests
from selenium import webdriver    #模拟浏览器行为的库
import pandas as pd

class Downloader(object):
    def __init__(self):
        self.form1 = 'http://search.sina.com.cn/?q=%CC%A8%B7%E7+%C3%D7%C4%C8&range=title&c=news&sort=time&col=&source=&from=&country=&size=&time=&a=&page='
        self.form2 = '&pf=0&ps=0&dpc=1'
        self.target = 'https://news.sogou.com/news?query=site%3Asina.com.cn+%CC%A8%B7%E7%C3%E7%B0%D8&_ast=1575011200&_asf=news.sogou.com&time=0&w=01029901&sort=1&mode=2&manual=true&dp=1&sut=19016&sst0=1575011348844&lkt=1%2C1575011348741%2C1575011348741' #搜狗搜索
        self.article_urls = []
        self.article_num = 0

    """
    获取每一篇新闻的链接
    """
    def get_articleUrls(self):
        new_target = self.target
        for i in range(20):
            req = requests.get(new_target)    
            req.encoding = 'utf8'
            html = req.text
            soup = BeautifulSoup(html,'html.parser')
            h3 = soup.find_all('h3',class_ = 'vrTitle')
            for x in h3:
                a_sp = BeautifulSoup(str(x),'html.parser')
                a = a_sp.find_all('a')
                self.article_urls.append(a[0].get('href'))
            pagebox = soup.find_all('div',class_ = 'p',id = 'pagebar_container')
            pagea_soup = BeautifulSoup(str(pagebox[0]),'html.parser')
            page_a = pagea_soup.find_all('a',id = 'sogou_next')
            if len(page_a) == 0:
                break
            new_target = 'https://news.sogou.com/news'+page_a[0].get('href')
        self.article_num = len(self.article_urls)

    '''
    获取每一篇新闻的时间，标题，内容
    '''
    def get_articles(self,target):
        req = requests.get(url = target)
        req.encoding = 'utf8'
        html = req.text
        soup = BeautifulSoup(html,'html.parser')

        title_h1 = soup.find_all('h1', class_='main-title')
        if len(title_h1) == 0:
            header = soup.find_all('div',class_ = 'article-header clearfix')
            title_h1 = soup.find_all('h1')
            time_span = soup.find_all('span')
            content_div = soup.find_all('div',class_ = 'article-body main-body')
        else:
            time_span = soup.find_all('span', class_='date')
            content_div = soup.find_all('div', class_='article')

        if len(content_div) == 0 or len(title_h1) == 0 or len(time_span) == 0:
            return ['','','']

        content_tx = BeautifulSoup(str(content_div[0]), 'html.parser').find_all('p')
        content = ''
        for x in content_tx:
            content = content + x.text
        content.strip()
        title = title_h1[0].text
        time_ = time_span[0].text
        list = [time_,title,content]
        return list

    def writer(self,all_news,path,colname):
        file = pd.DataFrame(data=all_news,columns=colname)
        file.to_csv(path,encoding='utf_8_sig')  #只能用这个编码，用utf8会乱码，不知道为什么。。



if __name__ == "__main__":
    dl = Downloader()
    dl.get_articleUrls()
    typhonName = '台风苗柏.csv'
    path_pro = 'E:/TyphonData/2017/'
    colnames = ['newstime', 'newsTitle', 'newsContent']
    allNews = []
    print('开始下载:',typhonName)
    for i in range(dl.article_num):
        allNews.append(dl.get_articles(dl.article_urls[i]))
        print('已下载:',i+1,'/',(dl.article_num))
    path = path_pro + typhonName
    dl.writer(allNews,path,colnames)
    print(typhonName,"下载完成！")



