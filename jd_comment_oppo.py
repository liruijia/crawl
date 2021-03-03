# -*- coding = utf-8 -*-
'''
 @Author : RuiJia Li 
 @Time   : 2021/1/27 22:10
 @File   : jd_comment_oppo.py
 @Desc   :
'''
'''
来则要在https://item.jd.com/57521830334.html#comment该网进行爬取,而且此时我们爬取只需要直接获取productpagecomment这个JS的
内容即可
产品评论网站:
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
import random
import http.cookiejar
import json
import pandas as pd
import csv
import codecs

class jd_comment():
    def __init__(self):
        print('开始爬取')
    def getnet_info(self):
        '''利用搜索到的结果获取每个产品的productid以及获取其下的评论个数'''
        all_info=pd.DataFrame(columns=['shop_name','comment_num','productId','good_rate','url','product'])
        #headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        #         'cookie':'__jdu=15643226051851040841365; pinId=5rS7uzjk4iIY_10t6rX84A; pin=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unick=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; _tp=q04yhIMpErvWbIVgKgQmuAFh%2Bn9sH33%2BohCLpppALCs%3D; _pst=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unpl=V2_ZzNtbUQHF0YiWkYHLxwIUWILEVkRAEFHd19ABnwbXQI3AEZeclRCFX0URldnGVoUZwcZWEFcQhJFCEdkeB5fA2AFEFlBZxVLK14bADlNDEY1WnwHBAJfF3ILQFJ8HlQMZAEUbXJUQyV1CXZUfx5ZB2QAFVxGV0oRdQlDVXIcXAdgByJtRWdzJXEBRV1%2fEWwEVwIiHxYLRBVyCkZRNhlYAmIBEV5FVkcVfAxGVX4YVQBnARVZclZzFg%3d%3d; __jdv=76161171|google-search|t_262767352_googlesearch|cpc|kwd-362776698237_0_7aebfc1be4ee4925bf3c3f7c6306a2e2|1576568529253; areaId=28; ipLoc-djd=28-2487-21646-0; shshshfpa=a2bdab8c-c101-61b7-d32e-eb0b75ce8ec7-1576568591; shshshfpb=bnrFJM6cZ7L5fQ9VdFuUtWg%3D%3D; ceshi3.com=000; TrackID=18tYjxLpdylvIgEKVu1h0V-M_YM2jE1kvxiBAmSl0qH_y_YXjg2WirTAEJhqpibK-2oI8x6-Mj4XvDpvwWHhTq9sRPgesCwGL6lo3e60bgFY; PCSYCityID=CN_620000_620100_620103; __jdc=122270672; 3AB9D23F7A4B3C9B=UQ45CY3ZSEKZC65MCK6BCU5AGQII4HW3FKN5AOSS62FC3QBXULUVRC4WODL536WNZSHM7ORWQDOEGHXV7UPG2ADRLQ; shshshfp=06031fa83bf3e7fe66a12a448b44620e; thor=58D9324435DD0AC1EEE5C46D19697B5ADF444E668FC328C46CABA0485602B287C8579C7145114310AFF2EFBDF4E49F84E8657F4743EB33CA21D9B2D2C101AD5C59B4BE4ACA48A38C1E35AB21B52DFD6F0AEDE45C11060C6BBB34809353E9A252C69B87DD6FA2B55067F455A29E2D12B8B46310BBB0E4718D6131D6D9F518C7D3B220CE27DECEC78734F08E08ABE25B20; __jda=122270672.15643226051851040841365.1564322605.1576575475.1576583300.9; __jdb=122270672.1.15643226051851040841365|9.1576583300; shshshsID=74043da9250acf14f8dde40fed669c65_1_1576583301258'}
        #
        jj=0
        for i in range(1,6):
            try:
                url_1='https://search-x.jd.com/Search?callback=jQuery2707165&area=28&enc=utf-8&keyword=oppo+reno&adType=7&page='
                url_2=str(i)+'&ad_ids=291%3A33&xtest=new_search'
                url=url_1+url_2
                r=requests.get(url).text
                #print(r)
                response=r.lstrip('jQuery2707165(').rstrip(')')
                print('resopnse:',len(response))
                data=json.loads(response)
                for i in data['291']:
                    store_name=i['shop_link']['shop_name']
                    comment_num=i['comment_num']
                    productId=i['sku_id']
                    url=i['link_url']+'#comment'
                    product=i['ad_title']  #利用product进行后期的处理
                    good_rate=i['good_rate']
                    print(store_name,comment_num,good_rate,url)
                    all_info.loc[jj]=[store_name,comment_num,productId,good_rate,url,product]
                    jj+=1
            except Exception as result:
                print('error',result)
        all_info.to_csv('product_info_before.csv')
        print('所有产品的基本信息已经加载完成****************')
        return all_info

    def getinfo(self,all_info):
        info=all_info.copy()
        print('the origin of len :',len(info))
        index_drop=[]
        print(info)
        for row_id,data  in all_info.iterrows():
            product_info=data['product']
            comment_num=data['comment_num']
            if 'oppo' not in product_info and 'OPPO' not in product_info:
                index_drop.append(row_id)
                print('row_id',row_id)
            else:
                if int(comment_num)==0:
                    index_drop.append(row_id)
                    print('row_id',row_id)
        print('index:',index_drop)
        info.drop(info.index[index_drop],inplace=True)
        print('the len of info :',len(info))
        info.to_csv('product_info_after.csv')
        print('基本信息处理完成******************')
        return info


    def _getcomment(self,productId,comment_num):
        all_comment=pd.DataFrame(columns=['user_id','user_name','referenceTime','score','productid','product_color','comment'])

        URL='https://chat1.jd.com/api/checkChat?callback=jQuery1024117&pid='+str(productId)+'&returnCharset=UTF-8&_=1576665317646'

        headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
                 'referer':'https://item.jd.com/'+str(productId)+'.html',
                 'cookie':'__jdu=15643226051851040841365; pinId=5rS7uzjk4iIY_10t6rX84A; pin=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unick=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; _tp=q04yhIMpErvWbIVgKgQmuAFh%2Bn9sH33%2BohCLpppALCs%3D; _pst=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unpl=V2_ZzNtbUQHF0YiWkYHLxwIUWILEVkRAEFHd19ABnwbXQI3AEZeclRCFX0URldnGVoUZwcZWEFcQhJFCEdkeB5fA2AFEFlBZxVLK14bADlNDEY1WnwHBAJfF3ILQFJ8HlQMZAEUbXJUQyV1CXZUfx5ZB2QAFVxGV0oRdQlDVXIcXAdgByJtRWdzJXEBRV1%2fEWwEVwIiHxYLRBVyCkZRNhlYAmIBEV5FVkcVfAxGVX4YVQBnARVZclZzFg%3d%3d; __jdv=76161171|google-search|t_262767352_googlesearch|cpc|kwd-362776698237_0_7aebfc1be4ee4925bf3c3f7c6306a2e2|1576568529253; areaId=28; ipLoc-djd=28-2487-21646-0; shshshfpa=a2bdab8c-c101-61b7-d32e-eb0b75ce8ec7-1576568591; shshshfpb=bnrFJM6cZ7L5fQ9VdFuUtWg%3D%3D; ceshi3.com=000; TrackID=18tYjxLpdylvIgEKVu1h0V-M_YM2jE1kvxiBAmSl0qH_y_YXjg2WirTAEJhqpibK-2oI8x6-Mj4XvDpvwWHhTq9sRPgesCwGL6lo3e60bgFY; PCSYCityID=CN_620000_620100_620103; __jdc=122270672; mba_muid=15643226051851040841365; 3AB9D23F7A4B3C9B=UQ45CY3ZSEKZC65MCK6BCU5AGQII4HW3FKN5AOSS62FC3QBXULUVRC4WODL536WNZSHM7ORWQDOEGHXV7UPG2ADRLQ; _gcl_au=1.1.1366431867.1576661791; shshshfp=cee428329831c168d7622114e7ce16ab; __jda=122270672.15643226051851040841365.1564322605.1576665284.1576673751.12; JSESSIONID=60185F38B35FB8697B7C5CC932DB6B9E.s1; shshshsID=78aa37c999a13f1be43db8a9ae8ee99b_3_1576673820995; __jdb=122270672.3.15643226051851040841365|12.1576673751'}

        all_comment['productid']=productId
        jj=0
        comment_num=int(comment_num)
        if comment_num <=10:
            all_page=1
        elif comment_num>10000:
            all_page=1100
        else:
            all_page=int(comment_num/10)-1
        for ii in range(all_page):
            try:

                url_0='https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv308&productId='
                url_1=str(productId)+'&score=0&sortType=5&page='
                url_2=str(ii)
                url_3='&pageSize=10&isShadowSku=0&fold=1'
                final_url=url_0+url_1+url_2+url_3

                #print('i:%d'%i)
                response = requests.get(url=final_url, headers=headers)
                text=response.text
                print('response:',len(text))
                text_new=text.lstrip('fetchJSON_comment98vv308(').rstrip(';)')
                #print(text_new[:10])
                data=json.loads(text_new)
                #print('i:%d'%i)
                for i in data['comments']:
                    content = i['content']
                    user_id=i['id']
                    user_name=i['nickname']
                    referencetime=i['referenceTime']
                    score=i['score']
                    product_color=i['productColor']
                    #product_size=i['productSize']
                    #print("评论内容\n{0}".format(content))
                    all_comment.loc[jj]=[user_id,user_name,referencetime,score,None,product_color,content]
                    jj+=1
                print('product{0} 的 第{1}页评论加载完成'.format(productId,ii))
            except Exception as result:
                print('appear error:',result)
        return all_comment

    def get_all_comment(self,info):
        comment_total=pd.DataFrame(columns=['user_id','user_name','referenceTime','score','productid','product_color','comment'])
        for row_id,data in info.iterrows():
            product_id=data['productId']
            comment_num=data['comment_num']
            if product_id == '46165085511':
                continue
            comment=self._getcomment(product_id,comment_num)
            comment_total=pd.concat([comment_total,comment],axis=0)
            print('product:{0} 已经爬取完毕'.format(product_id))
        comment_total.to_csv('comment_info_final.csv')
        return comment_total


'''
得到中评、差评、好评信息
https://club.jd.com/comment/productCommentSummaries.action?
referenceIds=100007958792&callback=jQuery3629255&_=1579184931038
#好评
https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv3792
&productId=100007958792&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
---只有好评  按照好评数量只取其中一部分
中评
ttps://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv3792&
productId=100007958792&score=2&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
差评
https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv3792&
productId=100007958792&score=1&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
#获取商品信息
https://search-x.jd.com/Search?callback=jQuery3156516&area=28&enc=utf-8
&keyword=%E5%B0%8F%E7%B1%B3%E6%89%8B%E6%9C%BA
&adType=7&page=1&ad_ids=291%3A33&xtest=new_search&_=1579190663713
header={'cookie': '__jdu=15643226051851040841365; pinId=5rS7uzjk4iIY_10t6rX84A; shshshfpa=a2bdab8c-c101-61b7-d32e-eb0b75ce8ec7-1576568591; shshshfpb=bnrFJM6cZ7L5fQ9VdFuUtWg%3D%3D; __jdv=122270672|direct|-|none|-|1578490716613; areaId=28; ipLoc-djd=28-2487-21646-0; TrackID=1gVLCSCZJoEFbSGKRwcYjkAv3SsBgq9IHfMCQG7QwWudFirK6w3yPr7GjtWQgFNyQthQw8dHpOyacXoxJnD96w58CbGf1GATjaCVMNcNyWPM; pin=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unick=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; ceshi3.com=000; _tp=q04yhIMpErvWbIVgKgQmuAFh%2Bn9sH33%2BohCLpppALCs%3D; _pst=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; 3AB9D23F7A4B3C9B=UQ45CY3ZSEKZC65MCK6BCU5AGQII4HW3FKN5AOSS62FC3QBXULUVRC4WODL536WNZSHM7ORWQDOEGHXV7UPG2ADRLQ; mba_muid=15643226051851040841365; mba_sid=15791897235927960796973111488.1; __jda=122270672.15643226051851040841365.1564322605.1579184765.1579189368.18; __jdc=122270672; shshshfp=8f9a0cac13798c679273417d0f2cb187; thor=58D9324435DD0AC1EEE5C46D19697B5A496EA38DDFB2606F44B3A3C3B57622BBFFD2B7D55E03119612AA66ADAAA3EDE6B0A656EDF3142B795DEA7A01A6ADBEEFC363FB35F10DE3A044C42FFC57ED82772A0707E886879F6A57115BF62A6B87B2B57F136973EB086DCEBB585B8F7A52F91B8FEF64E2C19FC5B46D05A90018B5501E684DD7ADAA5DAF6F47FD808E87ADAD; __jdb=122270672.8.15643226051851040841365|18.1579189368; shshshsID=f472c7b4616a515a81f5be8340bdb29c_4_1579190663233',
'referer': 'https://search.jd.com/Search?keyword=%E5%B0%8F%E7%B1%B3%E6%89%8B%E6%9C%BA&enc=utf-8&wq=%E5%B0%8F%E7%B1%B3%E6%89%8B%E6%9C%BA&pvid=3eada851e4d844c78a0a741601b465d7',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}
###水杯
https://search-x.jd.com/Search?callback=jQuery243330&area=28&enc=utf-8
&keyword=%E6%B0%B4%E6%9D%AF&adType=7&
page=1&ad_ids=291%3A33&xtest=new_search&_=1579240625062
'''





class cup_comment():
    def __init__(self):
        print('开始爬取京东商城上关于cup手机的评论')
    def getnet_info(self):
        '''利用搜索到的结果获取每个产品的productid以及获取其下的评论个数'''


        all_info=pd.DataFrame(columns=['shop_id','shop_name','product_id',
                                       'comment_num','product_info','url'])
        jj=0
        header = {'referer': 'https://search.jd.com/Search?keyword=%E6%B0%B4%E6%9D%AF&enc=utf-8&wq=%E6%B0%B4%E6%9D%AF&pvid=45d62dd3c46b40eeaa3b0b0feb2079b9',
                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
            ,'cookie':'__jdu=15643226051851040841365; pinId=5rS7uzjk4iIY_10t6rX84A; shshshfpa=a2bdab8c-c101-61b7-d32e-eb0b75ce8ec7-1576568591; shshshfpb=bnrFJM6cZ7L5fQ9VdFuUtWg%3D%3D; __jdv=122270672|direct|-|none|-|1578490716613; areaId=28; ipLoc-djd=28-2487-21646-0; TrackID=1gVLCSCZJoEFbSGKRwcYjkAv3SsBgq9IHfMCQG7QwWudFirK6w3yPr7GjtWQgFNyQthQw8dHpOyacXoxJnD96w58CbGf1GATjaCVMNcNyWPM; pin=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unick=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; ceshi3.com=000; _tp=q04yhIMpErvWbIVgKgQmuAFh%2Bn9sH33%2BohCLpppALCs%3D; _pst=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; 3AB9D23F7A4B3C9B=UQ45CY3ZSEKZC65MCK6BCU5AGQII4HW3FKN5AOSS62FC3QBXULUVRC4WODL536WNZSHM7ORWQDOEGHXV7UPG2ADRLQ; mba_muid=15643226051851040841365; __jdc=122270672; __jda=122270672.15643226051851040841365.1564322605.1579197558.1579240611.21; shshshfp=8f9a0cac13798c679273417d0f2cb187; thor=58D9324435DD0AC1EEE5C46D19697B5A496EA38DDFB2606F44B3A3C3B57622BBE2728A9150DA04F2BECFCB5AA00C932B9F2C2CE171DEF3D4D1F5CB3C7F09095D91DB7BA016DD6C2EB7A9996E0A606CE1922D09C4A0847EEAE316D6BD4C0549E674617D7B6F2F11FE9CE945297E3EAAE1B2A2A6F622FDD60EB7082E25C8A07F2A582AD5D53B8BE11B4D7036998BE451EC; __jdb=122270672.2.15643226051851040841365|21.1579240611; shshshsID=7aea9543ec51b74f104a7aedeac80e25_2_1579240624605'}

        jj=0
        for num in range(10):
            print()
            try:
                url='https://search-x.jd.com/Search?callback=jQuery243330&area=28&enc=utf-8&keyword=%E6%B0%B4%E6%9D%AF&adType=7&page='+str(num)+'&ad_ids=291%3A33&xtest=new_search&_=1579240625062'
                #print(url)
                r=requests.get(url,headers=header).text
                response=r.lstrip('jQuery243330(').rstrip(')')
                print('resopnse:',len(response))
                data=json.loads(response)
                print(type(data))

                for i in data['291']:
                    #print(len(i))
                    product_id=i['sku_id']
                    product_info=i['ad_title']
                    shop_id=i['shop_id']
                    shop_name=i['shop_link']['shop_name']
                    url=i['link_url']
                    comment_num=i['comment_num']
                    all_info.loc[jj]=[shop_id,shop_name,product_id,comment_num,product_info,url]
                    jj+=1
                    print('第{0}个产品信息加载完毕'.format(jj))
            except Exception as result:
                print('error',result)
        all_info.to_csv('product_info_cup_before.csv')
        print('所有产品的基本信息已经加载完成****************')
        return all_info

    def getinfo(self, all_info):
        info = all_info.copy()
        print('the origin of len :', len(info))
        index_drop = []
        print(info)
        for row_id, data in all_info.iterrows():
            product_info = data['product_info']
            comment_num = data['comment_num']
            if '小米' not in product_info and 'Redmi' not in product_info:
                index_drop.append(row_id)
                print('row_id', row_id)
            else:
                if int(comment_num) == 0:
                    index_drop.append(row_id)
                    print('row_id', row_id)
        print('index:', index_drop)
        info.drop(info.index[index_drop], inplace=True)
        print('the len of info :', len(info))
        info.to_csv('product_info_cup_after.csv')
        print('基本信息处理完成******************')
        return info
    def _getcomment(self,product_id,type_id,comment_num):

        all_comment=pd.DataFrame(columns=['userid','nickname','creationTime','product_id','referenceId',
                                          'score','product_info','comment'])
        url1='https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv82&'
        url2='productId='+str(product_id)
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
                 'Cookie': '__jdu=15643226051851040841365; pinId=5rS7uzjk4iIY_10t6rX84A; shshshfpa=a2bdab8c-c101-61b7-d32e-eb0b75ce8ec7-1576568591; shshshfpb=bnrFJM6cZ7L5fQ9VdFuUtWg%3D%3D; __jdv=122270672|direct|-|none|-|1578490716613; areaId=28; ipLoc-djd=28-2487-21646-0; TrackID=1gVLCSCZJoEFbSGKRwcYjkAv3SsBgq9IHfMCQG7QwWudFirK6w3yPr7GjtWQgFNyQthQw8dHpOyacXoxJnD96w58CbGf1GATjaCVMNcNyWPM; pin=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unick=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; ceshi3.com=000; _tp=q04yhIMpErvWbIVgKgQmuAFh%2Bn9sH33%2BohCLpppALCs%3D; _pst=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; 3AB9D23F7A4B3C9B=UQ45CY3ZSEKZC65MCK6BCU5AGQII4HW3FKN5AOSS62FC3QBXULUVRC4WODL536WNZSHM7ORWQDOEGHXV7UPG2ADRLQ; jwotest_product=99; mba_muid=15643226051851040841365; __jdc=122270672; JSESSIONID=D1DF10308AA0B61BE44131B4197CC2F3.s1; __jda=122270672.15643226051851040841365.1564322605.1579197558.1579240611.21; shshshfp=1f769c4c00b617d9a2eb7d02e653c707; shshshsID=7aea9543ec51b74f104a7aedeac80e25_5_1579241090457; __jdb=122270672.5.15643226051851040841365|21.1579240611; thor=58D9324435DD0AC1EEE5C46D19697B5A496EA38DDFB2606F44B3A3C3B57622BB94612BB26ECC565DBA0F7E23C470575A4B1662E12F15384CE3861657B16A66BFCC1D933E360FD69AA739859FBDB08854E0FB08159C81DB6A7E02427F67AEEC50066F083B65821A30C8572B5B873B6E53D5E33A8E0164F1946D585369D99FE526CCE030CA2E1EE8377C15ECA3C28432BE',
                 'Referer':'https://item.jd.com/'+str(product_id)+'.html'
                 }
        all_page=int(int(comment_num)/10)+1
        jj=0
        if all_page>=100:
            all_page=100
        for page_num in range(0,all_page):
            try:
                #print('i:%d'%i)
                url3 = '&score=' + str(type_id) + '&sortType=5&page=' + str(page_num) + '&pageSize=10&isShadowSku=0&fold=1'
                url=url1+url2+url3
                print(url)
                re = requests.get(url=url, headers=headers)
                response=re.text
                #print('response:',len(text))
                text=response.lstrip('fetchJSON_comment98vv82(').rstrip(');')
                #print(text_new[:10])
                data=json.loads(text)
                #print('i:%d'%i)
                for comment in data['comments']:
                    content = comment['content']
                    user_id=comment['id']
                    user_name=comment['nickname']
                    referencetime=comment['creationTime']
                    score=comment['score']
                    if comment['productColor'] is None:
                        product_info=comment['productSize']
                    elif comment['productSize'] is None:
                        product_info = comment['productColor']
                    elif comment['productColor'] is not None and comment['productSize'] is not None:
                        product_info=comment['productColor']+comment['productSize']
                    elif comment['productColor'] is None and comment['productSize'] is None:
                        product_info=None
                    referenceid=comment['referenceId']
                    all_comment.loc[jj]=[user_id,user_name,referencetime,product_id,referenceid,score,
                                         product_info,content]
                    jj+=1
                print('prodcutid:{0} 的 第{1}页评论加载完成'.format(product_id,page_num))
            except Exception as result:
                print('appear error:',result)
        return all_comment
    def get_all_comment(self,info):
        comment_total=pd.DataFrame(columns=['userid','nickname','creationTime','product_id',
                                            'referenceId','score',
                                            'product_info','comment'])
        ui=[]
        for row_id,data in info.iterrows():
            try:
                product_id=data['product_id']
                print('开始爬取product:{0}的评论信息'.format(product_id))
                shopId = data['shop_id']
                if product_id not in ui:
                    ui.append(product_id)
                    headers = {
                        'Cookie': '__jdu=15643226051851040841365; pinId=5rS7uzjk4iIY_10t6rX84A; shshshfpa=a2bdab8c-c101-61b7-d32e-eb0b75ce8ec7-1576568591; shshshfpb=bnrFJM6cZ7L5fQ9VdFuUtWg%3D%3D; __jdv=122270672|direct|-|none|-|1578490716613; areaId=28; ipLoc-djd=28-2487-21646-0; TrackID=1gVLCSCZJoEFbSGKRwcYjkAv3SsBgq9IHfMCQG7QwWudFirK6w3yPr7GjtWQgFNyQthQw8dHpOyacXoxJnD96w58CbGf1GATjaCVMNcNyWPM; pin=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; unick=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; ceshi3.com=000; _tp=q04yhIMpErvWbIVgKgQmuAFh%2Bn9sH33%2BohCLpppALCs%3D; _pst=%E4%BD%B3%E4%BD%B3%E4%BD%B31016; __jdc=122270672; __jda=122270672.15643226051851040841365.1564322605.1579166273.1579184765.17; 3AB9D23F7A4B3C9B=UQ45CY3ZSEKZC65MCK6BCU5AGQII4HW3FKN5AOSS62FC3QBXULUVRC4WODL536WNZSHM7ORWQDOEGHXV7UPG2ADRLQ; shshshfp=1f769c4c00b617d9a2eb7d02e653c707; jwotest_product=99; JSESSIONID=070515F48B256E9C1BFB340586FCF642.s1; thor=58D9324435DD0AC1EEE5C46D19697B5A496EA38DDFB2606F44B3A3C3B57622BBACA61155E87B92EAE562A75E474C782B60493C873C382AA023066FA7FA4819B8901BA23891E9BBD3BC9898E5A4394792021A57F44757C2BF2B32757FA649132317785AB52EB55ED6E47344E31EB07BAA7B3815F52A5AEAB70428821BDD7186E61AFF87EA35C68C870DE5CB61D2DA1C71; shshshsID=ea054ac0610099ef8a848e8d7c17c469_8_1579187245720; __jdb=122270672.11.15643226051851040841365|17.1579184765',
                        'User - Agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 79.0.3945.117Safari / 537.36',
                        'Referer': 'https://item.jd.com/' + str(product_id) + '.html'

                    }
                    url='https://club.jd.com/comment/productCommentSummaries.action?referenceIds='+str(product_id)+'&callback=jQuery8184807&_=1579241091165'
                    re=requests.get(url,headers)
                    print(url)
                    response=re.text
                    print('response:',len(response))
                    data=response.lstrip('jQuery8184807(').rstrip(');')
                    print(len(data))
                    print(data[:20])
                    data=json.loads(data)
                    ui=data['CommentsCount']
                    print(type(ui))
                    print(data)
                    goodnum=ui[0]['GoodCount']
                    normalnum=ui[0]['GeneralCount']
                    poornum=ui[0]['PoorCount']
                    #comment_good=self._getcomment(product_id,0,goodnum)
                    comment_normal=self._getcomment(product_id,2,normalnum)
                    comment_poor = self._getcomment(product_id,1, poornum)
                    n=len(comment_normal)+len(comment_poor)

                    #comment_total=pd.concat([comment_total,comment_good],axis=0)
                    comment_total=pd.concat([comment_total,comment_normal],axis=0)
                    comment_total = pd.concat([comment_total, comment_poor], axis=0)
                    print('shop_id:{0} 已经爬取完毕'.format(shopId))
                    comment_total.to_csv('comment_info_cup1_final.csv')

                else:
                    continue
            except Exception as result:
                print(result)
        return comment_total



M=cup_comment()
all_info=M.getnet_info()
#info=M.getinfo(all_info)
info=all_info[56:-1]
print(info.iloc[0])
comment=M.get_all_comment(info)

