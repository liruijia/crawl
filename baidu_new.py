# -*- coding = utf-8 -*-
'''
 @Author : RuiJia Li 
 @Time   : 2021/1/27 22:07
 @File   : baidu_new.py
 @Desc   :
'''

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import os

class news_spider():
    def __init__(self,headers):
        print('开始进行对于网易新闻网站的娱乐、健康、公益、科技、旅游主题的新闻进行爬取')
        self.headers=headers
    def urls_public_benefit(self,url):
        urlsss = []
        r = requests.get(url,headers=self.headers).text
        soup = BeautifulSoup(r,'lxml')
        aa=soup.find_all('div','content')
        for i in aa:  #[:-3]
            ki=i.find_all('a')
            for ui in ki:
                urlsss.append(ui.get('href'))
        return urlsss

    def urls_travel(self,url,click_num):
        urlsss = []
        browser = webdriver.Chrome()
        browser.get(url)
        for i in range(click_num):
            if i < click_num-1:
                selected_div = browser.find_element_by_css_selector(".post_addmore")
                ActionChains(browser).click(selected_div).perform()
            if i==click_num-1:
                content=browser.page_source
                browser.close()
        soup = BeautifulSoup(content,'lxml')
        aa=soup.find_all('div','news_title')
        for i in aa:  #[:-3]
            ki=i.find_all('a')
            for ui in ki:
                urlsss.append(ui.get('href'))
        return urlsss

    def urls_health(self,url,click_num=10): #爬取所有url
        urlsss = []
        browser = webdriver.Chrome()
        browser.get(url)
        all_page=1
        try:
            for i in range(click_num):
                content=browser.page_source
                soup = BeautifulSoup(content,'lxml')
                aa=soup.find_all('div','news_main_info')
                for i in aa:  #[:-3]
                    ki=i.find_all('a')[0]
                    urlsss.append(ki.get('href'))
                ab=browser.find_element_by_css_selector(".next_page")
                if ab:
                    ActionChains(browser).click(ab).perform()
                    continue
                else:
                    browser.close()
                    break
                all_page+=1
            print(all_page)
        except Exception as result:
            print('没有下一页了。。。')
            print('%s',result)
            print('*'*50)
        return urlsss

    def urls_entertainment(self,url): #爬取所有url
        urlsss = []
        r = requests.get(url, headers=self.headers).text
        soup = BeautifulSoup(r,'lxml')
        aa=soup.find_all('div','tabContents active')
        for i in aa:  #[:-3]
            ki=i.find_all('tr')
            for ui in range(1,len(ki)):
                p=ki[ui].find('a')
                if p is not None:
                    urlsss.append(p.get('href'))
                else:
                    continue
        return urlsss

    def urls_technology(self,url): #爬取所有url
        urlsss = []
        r = requests.get(url, headers=self.headers).text
        soup = BeautifulSoup(r,'lxml')
        aa=soup.find_all('div','titleBar clearfix')
        for i in aa:  #[:-3]
            ki=i.find_all('a')
            for ui in ki:
                urlsss.append(ui.get('href'))
        return urlsss

    def url_neirong(self,urls,save_path):
        #先检查是否存在该文件夹
        if os.path.exists(save_path):
            pass
        else:
            os.mkdir(save_path)
        for q in urls:
            try:
                time.sleep(2)
                r = requests.get(q,headers=self.headers).text
                soup = BeautifulSoup(r,'lxml')
                for jj in soup.find_all('div', class_="post_content_main"): #每章的标题
                    oop=jj.find_all('h1')[0].text
                    if os.path.exists(save_path +oop+'.txt'): #检查是否已存在该文件
                        print('已存在：',oop.text)
                        continue
                    else:
                        for i in soup.find_all('div', class_="post_content_main"): #每章的标题
                            hi=i.find_all('h1')[0].text

                            print('标题：'+ hi)
                            f = open(save_path+hi+'.txt','w',encoding='utf-8')
                            f.write('标题：'+ hi+ '\n')
                        for i in soup.find_all('div', class_="post_time_source"): #发布日期
                            print('-'*30)
                            ui=i.text.lstrip().rstrip()[0:19]
                            print('时间：'+ ui, end=' ');
                            print('URL:',q)
                            aad =i.find('a',id='ne_article_source').text
                            print('来源：',aad)
                            aaf = 'URL:%s'%q
                            f.write(ui + '\t')
                            f.write(aad + '\t')
                            f.write(aaf + '\n')
                            print('-'*30)
                        for i in soup.find_all('div',class_='post_text'): #每章的内容
                            f.write(i.text)
                            f.close()
                            print('*'*100)
            except Exception as result:
                print('网页不存在了。。。')
                print('%s',result)
                print('*'*50)

if __name__ == '__main__':
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/78.0.3904.108 Safari/537.36'}
    P=news_spider(headers)


    urlist1=['http://gongyi.163.com/special/huodongsudi']
    urlist1.extend([f'http://gongyi.163.com/special/huodongsudi_0{k}/' for k in range(2,10)])
    urlist1.extend([f'http://gongyi.163.com/special/huodongsudi_{k}/' for k in range(10,21)])
    save_path1='../新闻/公益新闻/'
    for i in range(2,len(urlist1)):
        url_neirong(P.urls_public_benefit(urlist1[i]),save_path1)
    print('完成！！！')


    urlist2=['http://tech.163.com/internet/']
    urlist2.extend([f'http://tech.163.com/special/internet_2016_0{k}' for k in range(2,10)])
    urlist2.extend([f'http://tech.163.com/special/internet_2016_{k}' for k in range(10,21)])
    save_path2='../新闻/科技新闻/'
    for i in range(len(urlist2)):
        url_neirong(P.urls_technology(urlist2[i]),save_path2)
    print('全部完成')

    url='http://travel.163.com/'
    save_path3='../新闻/旅游新闻/'
    url_neirong(P.urls_travel(url,click_num=30),save_path3)
    print('全部完成')


    url='http://jiankang.163.com/special/health_health/'
    save_path4='../新闻/健康新闻/'
    url_neirong(urls_health(url),save_path4)
    print('全部完成')


    url='http://news.163.com/special/0001386F/rank_ent.html'
    save_path5='../新闻/娱乐新闻/'
    url_neirong(urls_entertainment(url),save_path5)
    print('全部完成')