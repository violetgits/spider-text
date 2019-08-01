import requests
from scrapy import Selector
import re
import datetime
import json
import pymysql.cursors
import fake_useragent

# goods_category_list = {'https://list.jd.com/list.html?cat=6994,6995', 'https://list.jd.com/list.html?cat=6994,6996'
#     , 'https://list.jd.com/list.html?cat=6994,6997', 'https://list.jd.com/list.html?cat=6994,6998'
#     , 'https://list.jd.com/list.html?cat=6994,6999', 'https://list.jd.com/list.html?cat=6994,7000'
#     , 'https://list.jd.com/list.html?cat=6994,7001'}
goods_category_list = {'https://list.jd.com/list.html?cat=6994,6995'}

ua = fake_useragent.UserAgent(path='/Users/wangchao/PycharmProjects/resources/spider/my_test/useragent.json')
now_time = datetime.date.today()
ip_list = []


# 循环商品分类获取页面
def get_goods_list():
    for url in goods_category_list:
        count = 1
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "User-Agent": str(ua.random)
        }
        goods_list_html = requests.get(url, headers=headers).text
        get_goods_page_list(count, goods_list_html)


# 递归实现分页
def get_goods_page_list(count, goods_list_html):
    goods_list_sel = Selector(text=goods_list_html)
    # 获取共多少页
    goods_list_page_num = goods_list_sel.xpath('//*[@id="J_bottomPage"]/span[2]/em[contains(text(),"共")]/b/text()').get()
    if count > int(goods_list_page_num):
        return
    print(count)
    print("第" + str(count) + "页,本分类共：" + str(goods_list_page_num) + "页")
    # 获取当前页的商品列表
    page_goods_list_url = goods_list_sel.xpath('//*[@id="plist"]/ul/li/div/div[4]/a/@href').extract()
    for url_goods in page_goods_list_url:
        try:
            get_goods_item(url_goods)
        except Exception as err:
            print("error:该url:{0}出现错误！{1}".format(url_goods, err))
            continue
    # 获取下一页的链接
    next_page_url_xpath = goods_list_sel.xpath('//*[@id="J_bottomPage"]/span[1]/a[@class="pn-next"]/@href').get()
    next_page_url = "https://list.jd.com" + next_page_url_xpath
    print("下一页：{}".format(next_page_url))
    count += 1
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "User-Agent": str(ua.random)
    }
    get_goods_page_list(count, requests.get(next_page_url, headers=headers).text)


# 进入商品详情页
def get_goods_item(url):
    item_url = "https:" + url
    print("进入当前页：{}".format(item_url))
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "User-Agent": str(ua.random)
    }
    goods_detail_html = requests.get(item_url, headers=headers).text
    goods_detail_sel = Selector(text=goods_detail_html)
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
    # 商品价格https://p.3.cn/prices/mgets?callback=jQuery&type=1&area=12_988_40034_48088&pdtk=&pduid=37449089&pdpin=jd_75040464d9dea&pin=jd_75040464d9dea&pdbp=0&skuIds=J_4492766&ext=11100000&source=item-pc
    goods_price_html = requests.get('https://c0.3.cn/stock?skuId=' + sku + '&area=12_988_40034_48088&cat=6994,6995,7003', headers=headers).text
    goods_price_json = json.loads(goods_price_html)
    goods_price = goods_price_json['stock']['jdPrice']['p']
    # 评分 和 销量
    headers1 = {
        "Referer": "https://item.jd.com/" + sku + ".html",
        "user-agent": str(ua.random)
    }
    shop_sales_num_html = requests.get('https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment&productId=' + sku + '&score=0&sortType=5&page=0&pageSize=10', headers=headers1).text
    shop_sales_num_html_re = re.search("fetchJSON_comment\((.*)\);", shop_sales_num_html).group(1)
    shop_sales_num_json = json.loads(shop_sales_num_html_re)
    shop_sales_num = shop_sales_num_json['productCommentSummary']['commentCount']
    goods_point = shop_sales_num_json['productCommentSummary']['goodRateShow']
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
    with connection.cursor() as cursor:
        sql = "INSERT INTO `jd_goods` (`busi_date`, `data_source`, `sku`, `name`, `brand`, `price`, `point`, `ggbz`, `category`, `sales_num`, `weight`) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, date_list)
        connection.commit()


if __name__ == "__main__":
    connection = pymysql.connect(host='192.168.1.142',
                                 user='root',
                                 password='erp-888888',
                                 db='petgoodsdb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    # with connection.cursor() as cursor:
    #     pass
    #     sql = "select ip from xici"
    #     cursor.execute(sql)
    #     for ip_str in cursor.fetchall():
    #         ip_list.append(ip_str['ip'])
    try:
        get_goods_list()
    finally:
        connection.close()
