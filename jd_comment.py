# -*- coding = utf-8 -*-
'''
 @Author : RuiJia Li 
 @Time   : 2021/1/27 22:08
 @File   : jd_comment.py
 @Desc   :
'''
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pyquery import PyQuery as pq
import time
import pymongo
from requests.exceptions import RequestException
import requests
import random
import json


client = pymongo.MongoClient(host='localhost',port=27017)
db = client.condomdb
collection = db.condom1
collection_comment = db.condom_comment1

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0"}

# headers = {
#     "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）"
# }
#打开不同的浏览器实例
def openBrower(brower_type):
    if brower_type == 'chrome':
        return webdriver.Chrome()
    elif brower_type == 'firefox':
        return webdriver.Firefox()
    elif brower_type == 'safari':
        return webdriver.Safari()
    elif brower_type == 'PhantomJS':
        return webdriver.PhantomJS()
    else :
        return webdriver.Ie()

def parse_website():
    # 通过Chrome()方法打开chrome浏览器
    browser = openBrower('chrome')
    # 访问京东网站
    browser.get("https://search.jd.com/Search?keyword=oppo%20reno&enc=utf-8&wq=oppo%20reno&pvid=72ee783866c44bb4922a218eb1791c97")
    # 等待50秒
    wait = WebDriverWait(browser, 50)

    # 商品列表的总页数
    total = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b')
        )
    )
    print('total page===>' + total[0].text)
    html = browser.page_source.replace('xmlns', 'another_attr')
    parse_product(0,html)

    for page_num in range(1,int(total[0].text) + 1):
        time.sleep(get_random_time())
        print('休眠')
        parse_next_page(page_num,browser,wait)

##解析下一页
def parse_next_page(page_num,browser,wait):

    next_page_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next'))
    )
    next_page_button.click()

    #一页显示60个商品，"#J_goodsList > ul > li:nth-child(60)确保60个商品都正常加载出来。
    wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#plist > ul > li:nth-child(60)"))
    )
    # 判断翻页成功，当底部的分页界面上显示第几页时，就显示翻页成功。
    wait.until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"), str(page_num))
    )

    html = browser.page_source.replace('xmlns', 'another_attr')
    parse_product(page_num, html)

def parse_product(page,html):
    doc = pq(html)
    li_list = doc('.gl-item').items()
    for li in li_list:
        product_id = li('.gl-i-wrap').attr('data-sku')
        brand_id = li('.gl-i-wrap').attr('brand_id')
        time.sleep(get_random_time())
        title = li('.p-name').find('em').text()
        price_items = li('.p-price').find('.J_price').find('i').items()
        price = 0
        for price_item in price_items:
            price = price_item.text()
            break
        total_comment_num = li('.p-commit').find('strong a').text()
        if total_comment_num.endswith("万+"):
            print('总评价数量：' + total_comment_num)
            total_comment_num = str(int(float(total_comment_num[0:len(total_comment_num) -2]) * 10000))
            print('转换后总评价数量：' + total_comment_num)
        elif total_comment_num.endswith("+"):
            total_comment_num = total_comment_num[0:len(total_comment_num) - 1]
        condom = {}
        condom["product_id"] = product_id
        condom["brand_id"] = brand_id
        condom["condom_name"] = title
        condom["total_comment_num"] = total_comment_num
        condom["price"] = price
        comment_url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv308&productId=%s&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
        comment_url = comment_url %(product_id)
        response = requests.get(comment_url,headers = headers)
        if response.text == '':
            for i in range(0,10):
                time.sleep(get_random_time())
                try:
                    response = requests.get(comment_url, headers=headers)
                except requests.exceptions.ProxyError:
                    time.sleep(get_random_time())
                    response = requests.get(comment_url, headers=headers)
                if response.text:
                    break
                else:
                    continue
        text = response.text
        text = text[28:len(text) - 2]
        jsons = json.loads(text)
        productCommentSummary = jsons.get('productCommentSummary')
        # productCommentSummary = response.json().get('productCommentSummary')
        poor_count = productCommentSummary.get('poorCount')
        general_count = productCommentSummary.get('generalCount')
        good_count = productCommentSummary.get('goodCount')
        comment_count = productCommentSummary.get('commentCount')
        poor_rate = productCommentSummary.get('poorRate')
        good_rate = productCommentSummary.get('goodRate')
        general_rate = productCommentSummary.get('generalRate')
        default_good_count = productCommentSummary.get('defaultGoodCount')
        condom["poor_count"] = poor_count
        condom["general_count"] = general_count
        condom["good_count"] = good_count
        condom["comment_count"] = comment_count
        condom["poor_rate"] = poor_rate
        condom["good_rate"] = good_rate
        condom["general_rate"] = general_rate
        condom["default_good_count"] = default_good_count
        collection.insert(condom)

        comments = jsons.get('comments')
        if comments:
            for comment in comments:
                print('解析评论')
                condom_comment = {}
                reference_time = comment.get('referenceTime')
                content = comment.get('content')
                product_color = comment.get('productColor')
                user_client_show = comment.get('userClientShow')
                user_level_name = comment.get('userLevelName')
                is_mobile = comment.get('isMobile')
                creation_time = comment.get('creationTime')
                guid = comment.get("guid")
                condom_comment["reference_time"] = reference_time
                condom_comment["content"] = content
                condom_comment["product_color"] = product_color
                condom_comment["user_client_show"] = user_client_show
                condom_comment["user_level_name"] = user_level_name
                condom_comment["is_mobile"] = is_mobile
                condom_comment["creation_time"] = creation_time
                condom_comment["guid"] = guid
                collection_comment.insert(condom_comment)
        parse_comment(product_id)


def parse_comment(product_id):
    comment_url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98vv117396&productId=%s&score=0&sortType=5&page=%d&pageSize=10&isShadowSku=0&fold=1'
    for i in range(1,200):
        time.sleep(get_random_time())
        time.sleep(get_random_time())
        print('抓取第' + str(i) + '页评论')
        url = comment_url%(product_id,i)
        response = requests.get(url, headers=headers,timeout=10)
        print(response.status_code)
        if response.text == '':
            for i in range(0,10):
                print('抓取不到数据')
                response = requests.get(comment_url, headers=headers)
                if response.text:
                    break
                else:
                    continue
        text = response.text
        print(text)
        text = text[28:len(text) - 2]
        print(text)
        jsons = json.loads(text)
        comments = jsons.get('comments')
        if comments:
            for comment in comments:
                print('解析评论')
                condom_comment = {}
                reference_time = comment.get('referenceTime')
                content = comment.get('content')
                product_color = comment.get('productColor')
                user_client_show = comment.get('userClientShow')
                user_level_name = comment.get('userLevelName')
                is_mobile = comment.get('isMobile')
                creation_time = comment.get('creationTime')
                guid = comment.get("guid")
                id = comment.get("id")
                condom_comment["reference_time"] = reference_time
                condom_comment["content"] = content
                condom_comment["product_color"] = product_color
                condom_comment["user_client_show"] = user_client_show
                condom_comment["user_level_name"] = user_level_name
                condom_comment["is_mobile"] = is_mobile
                condom_comment["creation_time"] = creation_time
                condom_comment["guid"] = guid
                condom_comment["id"] = id
                collection_comment.insert(condom_comment)

        else:
            break

def get_random_time():
    sleep_time = random.randint(1, 10)
    return sleep_time

def main():
    parse_website()


if __name__ == "__main__":
    main()