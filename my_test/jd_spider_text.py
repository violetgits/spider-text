import requests
from scrapy import Selector
import re
import datetime
import json
import pymysql.cursors
from fake_useragent import UserAgent
import random

# goods_category_list = {'https://list.jd.com/list.html?cat=6994,6995', 'https://list.jd.com/list.html?cat=6994,6996'
#     , 'https://list.jd.com/list.html?cat=6994,6997', 'https://list.jd.com/list.html?cat=6994,6998'
#     , 'https://list.jd.com/list.html?cat=6994,6999', 'https://list.jd.com/list.html?cat=6994,7000'
#     , 'https://list.jd.com/list.html?cat=6994,7001'}
goods_category_list = {'https://list.jd.com/list.html?cat=6994,6995'}
ua = UserAgent(path='/Users/wangchao/PycharmProjects/resources/spider/my_test/useragent.json')
now_time = datetime.date.today()


# 循环商品分类获取页面
def get_goods_list():
    # for url in goods_category_list:
    url = 'https://list.jd.com/list.html?cat=6994,6995&page=2'
    count = 1
    goods_list_html = get_html(url, url)
    get_goods_page_list(count, goods_list_html)


# 递归实现分页
def get_goods_page_list(count, goods_list_html):
    goods_list_sel = Selector(text=goods_list_html)
    # 获取共多少页
    goods_list_page_num = goods_list_sel.xpath('//*[@id="J_bottomPage"]/span[2]/em[contains(text(),"共")]/b/text()').get()
    if count > int(goods_list_page_num):
        return
    print("第" + str(count) + "页,本分类共：" + str(goods_list_page_num) + "页")
    # 获取当前页的商品列表
    page_goods_list_url = goods_list_sel.xpath('//*[@id="plist"]/ul/li/div/div[4]/a/@href').extract()
    goods_count = 1
    # for url_goods in page_goods_list_url:
    get_goods_item(page_goods_list_url[16], count, goods_count)
    goods_count += 1
    # 获取下一页的链接
    next_page_url_xpath = goods_list_sel.xpath('//*[@id="J_bottomPage"]/span[1]/a[@class="pn-next"]/@href').get()
    next_page_url = "https://list.jd.com" + next_page_url_xpath
    print("下一页：{}".format(next_page_url))
    count += 1
    # get_goods_page_list(count, get_html(next_page_url, next_page_url))


# 进入商品详情页
def get_goods_item(url, page_count, goods_count):
    item_url = "https:" + url
    item_url_count = 0
    while 1:
        print("当前第{}页第{}个，进入：{}".format(page_count, goods_count, item_url))
        item_url_count += 1
        try:
            goods_detail_html = get_html(item_url, item_url)
            save_database(goods_detail_html, item_url)
            break
        except Exception as e:
            print("进入当前页,正在重试,次数:{},error{}".format(item_url_count, e))
            if item_url_count > 50:
                break
            else:
                continue


# 存入数据库
def save_database(goods_detail_html, item_url):
    goods_detail_sel = Selector(text=goods_detail_html)
    try:
        date_list = get_goods_detail_info(goods_detail_sel, item_url)
        print("存入数据库：{}".format(date_list))
        with connection.cursor() as cursor:
            sql = "INSERT INTO `jd_goods` (`busi_date`, `data_source`, `sku`, `name`, `brand`, `price`, `point`, `ggbz`, `category`, `sales_num`, `weight`) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, date_list)
            connection.commit()
    except Exception as e:
        print("存入数据库error,出现错误！{0}".format(e))
        pass


# 获取商品数据
def get_goods_detail_info(goods_detail_sel, item_url):
    # 当前日期
    # 数据来源
    # sku
    sku_html = goods_detail_sel.xpath('//*/li[contains(text(),"商品编号")]/text()').get()
    sku = re.search('商品编号：(.*)', sku_html).group(1)
    # 商品名称
    goods_name_html = goods_detail_sel.xpath('//*/div[@class="sku-name"]/text()').extract()
    goods_name = re.sub('\s', "", goods_name_html[len(goods_name_html) - 1])
    # 品牌
    goods_brand = goods_detail_sel.xpath('//*[@id="parameter-brand"]/li/@title').get()
    # 商品价格
    goods_price_html_url = 'https://c0.3.cn/stock?skuId=' + sku + '&area=12_988_40034_48088&cat=6994,6995,7003'
    goods_price = 0
    goods_price_count = 0
    while 1:
        goods_price_count += 1
        try:
            goods_price_html = get_html(goods_price_html_url, item_url)
            goods_price_json = json.loads(goods_price_html)
            goods_price = goods_price_json['stock']['jdPrice']['p']
            break
        except Exception as e:
            print("商品价格,正在重试,次数:{},error{}".format(goods_price_count, e))
            if goods_price_count > 50:
                break
            else:
                continue
    # 评分 和 销量
    shop_sales_num_url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment&productId=' + sku + '&score=0&sortType=5&page=0&pageSize=10'
    shop_sales_num = 0
    goods_point = 0
    goods_point_count = 0
    while 1:
        goods_point_count += 1
        try:
            shop_sales_num_html = get_html(shop_sales_num_url, item_url)
            shop_sales_num_html_re = re.search("fetchJSON_comment\((.*)\);", shop_sales_num_html).group(1)
            shop_sales_num_json = json.loads(shop_sales_num_html_re)
            shop_sales_num = shop_sales_num_json['productCommentSummary']['commentCount']
            goods_point = shop_sales_num_json['productCommentSummary']['goodRateShow']
            break
        except Exception as e:
            print("评分 和 销量,正在重试,次数：{},error{}".format(goods_point_count, e))
            if goods_point_count > 50:
                break
            else:
                continue
    # 规格包装
    goods_ggbz_html = goods_detail_sel.xpath('//*[@id="choose-attr-2"]/div[2]/div[3]/a/text()').get()
    goods_ggbz = ""
    if goods_ggbz_html:
        goods_ggbz = re.sub('\s', '', goods_ggbz_html)
    # 重量
    goods_weight = goods_detail_sel.xpath('//*[@id="detail"]/div[2]/div[1]/div[1]/ul[2]/li[contains(text(),"商品毛重")]/@title').get()
    # 分类
    goods_category1 = goods_detail_sel.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[1]/a/text()').get()
    if goods_category1:
        goods_category2 = goods_detail_sel.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[3]/a/text()').get()
        goods_category3 = goods_detail_sel.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[5]/a/text()').get()
        goods_category = goods_category1 + ">" + goods_category2 + ">" + goods_category3
    else:
        if '进口' in goods_name:
            goods_category2 = goods_detail_sel.xpath('//*[@id="item-detail"]/div[1]/ul/li[contains(text(),"商品产地：")]/@title').get()
            goods_category = "海囤全球" + ">" + goods_category2
        else:
            goods_category = "无"
    date_list = (now_time, item_url, sku, goods_name, goods_brand, goods_price, goods_point, goods_ggbz, goods_category, shop_sales_num, goods_weight)
    print(date_list)
    print("------------------")
    return date_list


def get_html(url, referer):
    # 代理服务器
    print("开始下载url : {}".format(url))
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "H58G6G30137G865D"
    proxyPass = "043F1F63DA9899C8"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }
    #
    # proxies = {
    #     "http": proxyMeta,
    #     "https": proxyMeta,
    # }
    proxies_str = ip_list[random.choice(range(0, len(ip_list)))]
    proxies = {
        proxies_str['type']: proxies_str['ip'] + ":" + str(proxies_str['port']),
    }

    if referer:
        headers = {
            "User-Agent": ua.random,
            "Referer": referer
        }
    else:
        headers = {
            "User-Agent": ua.random,
        }
    print("代理IP：{}".format(proxies))
    resp = requests.get(url, headers=headers, proxies=proxies)
    return resp.text


def get_ip_list():
    with connection.cursor() as cursor:
        sql = 'select `ip`,`port`,`type` from xici'
        cursor.execute(sql)
        connection.commit()
        return cursor.fetchall()


if __name__ == "__main__":
    connection = pymysql.connect(host='192.168.1.142',
                                 user='root',
                                 password='erp-888888',
                                 db='petgoodsdb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        ip_list = get_ip_list()
        print(ip_list)
        print(len(ip_list))
        get_goods_list()
    finally:
        connection.close()
