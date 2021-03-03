# -*- coding = utf-8 -*-
'''
 @Author : RuiJia Li 
 @Time   : 2021/1/27 22:11
 @File   : taobao_comment.py
 @Desc   :
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
    all_info.to_csv('product_info_before')
    print('所有产品的基本信息已经加载完成****************')
    return all_info

def getinfo(all_info):
    info=all_info.copy()
    for row_id,data  in all_info.iterrows():
        product_info=data['product']
        comment_num=data['comment_num']
        if 'oppo' not in product_info or 'OPPO' not in product_info or comment_num==0:
            all_info.drop(index=row_id)

    all_info.to_csv('product_info_after')
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
    all_info.to_csv('comment_info_final')
    return comment_total


all_info=getnet_info()
info=getinfo(all_info)
comment=get_all_comment(info)
