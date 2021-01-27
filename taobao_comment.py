# -*- coding = utf-8 -*-
'''
 @Author : RuiJia Li 
 @Time   : 2021/1/27 22:11
 @File   : taobao_comment.py
 @Desc   :
'''
'''
爬取微博/京东的某一个话题或者某一个产品的各种评论，同时爬取的时候最好保留一下内容：
如果是京东评论数据：
    第一个文件中保存：           ----------------   
    ---最好保存在excel中         ---------------- 
        id名                     ---------------- 
        发布时间                 ----------------
        评论所在的店铺           ----------------
        评论内容
    第二个文件中保存：
        id名
        评论所在的店铺
        所在店铺的星级/级别
        该店铺的总体评论的人数
        该店铺的粉丝数
    刷单性质的评论需要剔除！！！！！！！！这个也可以只进行简单处理，最后写在缺点里面
    获取了这些数据之后需要做的是：
        首先利用主题模型以及情感分析的模型判断评论者的情感态度（情感极性）
        其次希望找到该产品恶评最多的店铺，以及好评最多的店铺
        最后能够通过这种情感极性来对该店铺进行打分，得到所有店铺的排名
    模型：
        我们在进行上面的处理的时候肯定是想和传统的机器学习的方法进行一个比较
        1.我们可以利用这些评论以及所在店铺的打分，使用监督学习svm，进行预测
        2.使用情感主题模型
            依据句子进行情感分析-----对于同一句子中的词有相同的情感 ？？？？？？这一步怎么实现？？？？    有待考虑要不要进行写
            同时我们需要注意的是要加入表情包字典库，表情包也代表一定的感情色彩
            ---此时我们可以引入GLDA模型，然后将该模型与情感分析的模型进行融合
        3.需要了解到利用LDA模型进行情感分析的时候主要是做了哪些东西
'''
'''
我们至少要选择100多个店铺的某一个产品的评论信息，比如官方旗舰店以及各种手机专卖店
分析oppo reno 系列手机
首先利用find_all('div',class_='search-result-boxout')
然后继续定位到find_all('div',class_='title') ,最后查找第一个a标签的href属性
对于一个具体的网址：
需要获取评论人的昵称、店铺名、评论的总人数，该人的评论、发布的时间、该店铺的星级、该店铺的总的粉丝数量
比如我们爬取到的该商品的链接为https://item.jd.com/57521830334.html ，但是直接去爬取的话，是找不到相应的评论的，
要想爬取下来则要在https://item.jd.com/57521830334.html#comment该网进行爬取,而且此时我们爬取只需要直接获取productpagecomment这个JS的
内容即可
产品评论网站：https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv308
&productId=57521830334&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
https://item.jd.com/57521830334.html#comment
产品网站：https://item.jd.com/productId.html#comment
获取个产品的网址的网站：
https://search.jd.com/Search?keyword=oppo%20reno&enc=utf-8&suggest=1.rem.0.0&wq=oppo%20reno&pvid=e69b2a8e30a34f6984fc293b2192d23e
'''
import urllib
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import os
import http.cookiejar
import json
import pandas as pd


def getnet_info():
    '''利用搜索到的结果获取每个产品的productid以及获取其下的评论个数'''
    all_info=pd.DataFrame(columns=['shop_name','comment_num','productId','good_rate','url','product'])
    #headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    #         'cookie':'__jdu=15643226051851040841365; pinId=5rS7uzjk4iIY_10t6rX84A; pin=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unick=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; _tp=q04yhIMpErvWbIVgKgQmuAFh%2Bn9sH33%2BohCLpppALCs%3D; _pst=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unpl=V2_ZzNtbUQHF0YiWkYHLxwIUWILEVkRAEFHd19ABnwbXQI3AEZeclRCFX0URldnGVoUZwcZWEFcQhJFCEdkeB5fA2AFEFlBZxVLK14bADlNDEY1WnwHBAJfF3ILQFJ8HlQMZAEUbXJUQyV1CXZUfx5ZB2QAFVxGV0oRdQlDVXIcXAdgByJtRWdzJXEBRV1%2fEWwEVwIiHxYLRBVyCkZRNhlYAmIBEV5FVkcVfAxGVX4YVQBnARVZclZzFg%3d%3d; __jdv=76161171|google-search|t_262767352_googlesearch|cpc|kwd-362776698237_0_7aebfc1be4ee4925bf3c3f7c6306a2e2|1576568529253; areaId=28; ipLoc-djd=28-2487-21646-0; shshshfpa=a2bdab8c-c101-61b7-d32e-eb0b75ce8ec7-1576568591; shshshfpb=bnrFJM6cZ7L5fQ9VdFuUtWg%3D%3D; ceshi3.com=000; TrackID=18tYjxLpdylvIgEKVu1h0V-M_YM2jE1kvxiBAmSl0qH_y_YXjg2WirTAEJhqpibK-2oI8x6-Mj4XvDpvwWHhTq9sRPgesCwGL6lo3e60bgFY; PCSYCityID=CN_620000_620100_620103; __jdc=122270672; 3AB9D23F7A4B3C9B=UQ45CY3ZSEKZC65MCK6BCU5AGQII4HW3FKN5AOSS62FC3QBXULUVRC4WODL536WNZSHM7ORWQDOEGHXV7UPG2ADRLQ; shshshfp=06031fa83bf3e7fe66a12a448b44620e; thor=58D9324435DD0AC1EEE5C46D19697B5ADF444E668FC328C46CABA0485602B287C8579C7145114310AFF2EFBDF4E49F84E8657F4743EB33CA21D9B2D2C101AD5C59B4BE4ACA48A38C1E35AB21B52DFD6F0AEDE45C11060C6BBB34809353E9A252C69B87DD6FA2B55067F455A29E2D12B8B46310BBB0E4718D6131D6D9F518C7D3B220CE27DECEC78734F08E08ABE25B20; __jda=122270672.15643226051851040841365.1564322605.1576575475.1576583300.9; __jdb=122270672.1.15643226051851040841365|9.1576583300; shshshsID=74043da9250acf14f8dde40fed669c65_1_1576583301258'}
    #
    jj=0
    for i in range(1,6):
        try:
            url_1='https://search-x.jd.com/Search?callback=jQuery8374907&area=28&enc=utf-8&keyword=oppo+reno&adType=7&page='
            url_2=str(i)+'&ad_ids=291%3A33&xtest=new_search'
            url=url_1+url_2
            r=requests.get(url).text
            print(r)
            response=r.lstrip('jQuery8374907(').rstrip(')')
            print(response)
            data=json.loads(response)
            for i in data['291']:
                store_name=i['shop_link']['shop_name']
                comment_num=i['comment_num']
                productId=i['sku_id']
                url=i['link_url']+'#comment'
                product=i['ad_title']  #利用product进行后期的处理
                good_rate=i['good_rate']
                all_info.loc[jj]=[store_name,comment_num,productId,url]
            jj+=1
        except Exception as result:
            print('error',result)
    all_info.to_csv('C:/Users/Administrator/Desktop/data/评论/product_info_before')
    print('所有产品的基本信息已经加载完成****************')
    return all_info

def getinfo(all_info):
    info=all_info.copy()
    for row_id,data  in all_info.iterrows():
        product_info=data['product']
        comment_num=data['comment_num']
        if 'oppo' not in product_info or 'OPPO' not in product_info or comment_num==0:
            all_info.drop(index=row_id)

    all_info.to_csv('C:/Users/Administrator/Desktop/data/评论/product_info_after')
    print('基本信息处理完成******************')
    return info


def getcomment(all_page,productId):
    all_comment=pd.DataFrame(columns=['user_id','user_name','referenceTime','score','shop','product_color','product_size','comment'])

    URL='https://item.jd.com/'+str(productId)+'.html#comment'
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
             'referer': 'https://item.jd.com/57521830334.html',
             'cookie': '__jdu=15643226051851040841365; pinId=5rS7uzjk4iIY_10t6rX84A; pin=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unick=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; _tp=q04yhIMpErvWbIVgKgQmuAFh%2Bn9sH33%2BohCLpppALCs%3D; _pst=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unpl=V2_ZzNtbUQHF0YiWkYHLxwIUWILEVkRAEFHd19ABnwbXQI3AEZeclRCFX0URldnGVoUZwcZWEFcQhJFCEdkeB5fA2AFEFlBZxVLK14bADlNDEY1WnwHBAJfF3ILQFJ8HlQMZAEUbXJUQyV1CXZUfx5ZB2QAFVxGV0oRdQlDVXIcXAdgByJtRWdzJXEBRV1%2fEWwEVwIiHxYLRBVyCkZRNhlYAmIBEV5FVkcVfAxGVX4YVQBnARVZclZzFg%3d%3d; __jdv=76161171|google-search|t_262767352_googlesearch|cpc|kwd-362776698237_0_7aebfc1be4ee4925bf3c3f7c6306a2e2|1576568529253; areaId=28; ipLoc-djd=28-2487-21646-0; shshshfpa=a2bdab8c-c101-61b7-d32e-eb0b75ce8ec7-1576568591; shshshfpb=bnrFJM6cZ7L5fQ9VdFuUtWg%3D%3D; ceshi3.com=000; TrackID=18tYjxLpdylvIgEKVu1h0V-M_YM2jE1kvxiBAmSl0qH_y_YXjg2WirTAEJhqpibK-2oI8x6-Mj4XvDpvwWHhTq9sRPgesCwGL6lo3e60bgFY; thor=58D9324435DD0AC1EEE5C46D19697B5ADF444E668FC328C46CABA0485602B287768D913697F6C5966D3D9A7AB5BCEB8DAD60335804CFD45FB7572E7D33A7133DDE512FF8B5BF509C678E126C8ECE47EC6CD9C8B87900A71C61DBA640BA1DF5BADC4D8AD5FFD3D68C0F8609E64D03B124E54FE24C4DFAC7C35B774AA23E23C67EA28030C55A13D38D5B4740BA8D906D19; JSESSIONID=629345944CA8390B54606974E5FB7CEB.s1; PCSYCityID=CN_620000_620100_620103; shshshfp=cee428329831c168d7622114e7ce16ab; __jda=122270672.15643226051851040841365.1564322605.1575555555.1576568529.6; __jdc=122270672; 3AB9D23F7A4B3C9B=UQ45CY3ZSEKZC65MCK6BCU5AGQII4HW3FKN5AOSS62FC3QBXULUVRC4WODL536WNZSHM7ORWQDOEGHXV7UPG2ADRLQ; shshshsID=8e294f07bac1905d54c5c852d5265037_14_1576570680643; __jdb=122270672.20.15643226051851040841365|6.1576568529'
             }
    r=requests.get(url,headers).text
    soup=BeautifulSoup(r,'lxml')
    aa=soup.find('div',id='summary-service')
    all_comment['shop']=aa.find('a').text
    for i in range(all_page):
        try:
            url_0='https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv308&productId='
            url_1=str(productId)+'&score=0&sortType=5&page='
            url_2=str(0)
            url_3='&pageSize=10&isShadowSku=0&fold=1'
            final_url=url_0+url_1+url_2+url_3

            #print('i:%d'%i)
            response = requests.get(url=final_url, headers=headers, verify=False)

            text=response.text
            text_new=text.lstrip('fetchJSON_comment98vv308+++(').rstrip(';)')
            data=json.loads(text_new)
            #print('i:%d'%i)
            jj=0
            for i in data['comments']:
                content = i['content']
                user_id=i['id']
                user_name=i['nickname']
                referencetime=i['referenceTime']
                score=i['score']
                product_color=i['productColor']
                product_size=i['productSize']
                #print("评论内容\n{0}".format(content))
                all_comment.loc[jj]=[user_id,user_name,referencetime,score,None,product_color,product_size,content]
                jj+=1
            print('product{0} 的 第{1}页评论加载完成'.format(productId,i))
        except Exception as result:
            print('appear error',result)
    return all_comment

def get_all_comment(info):
    comment_total=pd.DataFrame()
    for row_id,data in info.iterrows():
        product_id=data['productId']
        comment=getcomment(5,productId)
        comment_total=pd.concat([comment_total,comment],axis=0,ignore_index=True)
    all_info.to_csv('C:/Users/Administrator/Desktop/data/评论/comment_info_final')
    return comment_total


all_info=getnet_info()
info=getinfo(all_info)
comment=get_all_comment(info)
