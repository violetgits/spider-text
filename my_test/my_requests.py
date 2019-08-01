import requests
from scrapy import Selector
import re
import datetime
import json
import pymysql.cursors
import fake_useragent

ua = fake_useragent.UserAgent(path='/Users/wangchao/PycharmProjects/resources/spider/my_test/useragent.json')
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "User-Agent": str(ua.random)
}
item_url = 'https://item.jd.com/34563750244.html'
print("进入当前页：{}".format(item_url))
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
date_list = (item_url, sku, goods_name, goods_brand, goods_price, goods_point, goods_ggbz, goods_category, shop_sales_num, goods_weight)
print(date_list)
print("------------------")
