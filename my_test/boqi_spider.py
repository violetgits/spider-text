import requests
from scrapy import Selector
import re
import datetime
import pymysql.cursors

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Language": 'zh,zh-HK;q=0.9,zh-CN;q=0.8,en-US;q=0.7,en;q=0.6,zh-TW;q=0.5',
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "UM_distinctid=16c1c9e293c43d-06d8a1fa7815d2-37677e02-1aeaa0-16c1c9e293e1b0; __jsluid_h=39a47f818d74f736f8e2dfe8cce73565; cityId=32; NTKF_T2D_CLIENTID=guest56962D73-8ABE-3EE9-931A-1C9EA00C50B3; __utma=137717295.1473295911.1564131570.1564131570.1564131570.1; __utmz=137717295.1564131570.1.1.utmcsr=shop.boqii.com|utmccn=(referral)|utmcmd=referral|utmcct=/dog/list-621-0-0-0-0-0-p2.html; Hm_lvt_16256b8df60004da41bb33a24cce8ba7=1564131570; PHPSESSID=6dfd00b27350ed668086e265069af9c5; userSessId=6dfd00b27350ed668086e265069af9c5; cityName=%E6%B1%9F%E8%8B%8F; CNZZDATA1265019045=1277829269-1563843084-http%253A%252F%252Fwww.boqii.com%252F%7C1564362956; CNZZDATA1273010752=650034217-1563844131-http%253A%252F%252Fwww.boqii.com%252F%7C1564359735; CNZZDATA1264316807=1563378263-1563845068-http%253A%252F%252Fwww.boqii.com%252F%7C1564360552; Hm_lvt_9035bf9f2ce12de3e1cc74aa8d3deeac=1564021683,1564029580,1564125938,1564364135; Hm_lpvt_9035bf9f2ce12de3e1cc74aa8d3deeac=1564364135; nTalk_CACHE_DATA={uid:kf_9481_ISME9754_guest56962D73-8ABE-3E,tid:1564364135192680}",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}
now_time = datetime.datetime.now()
res = requests.get("http://shop.boqii.com/", headers=headers)
sel = Selector(text=res.text)

connection = pymysql.connect(host='192.168.1.142',
                             user='root',
                             password='erp-888888',
                             db='petgoodsdb',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    # 获取首页分类，目前只获取狗和猫
    for a in range(2,4):
        home_tags = sel.xpath('//*[@id="nav"]/div/div[2]/a[' + str(a) + ']').extract()
        for text in home_tags:
            a_href = re.search('href="(.*?)"', text)
            if a_href:
                a_href_str = a_href.group(1).replace("null", "None")
                # 获取单个分类的商品分类
                res_list = requests.get(a_href_str, headers=headers)
                sel_list = Selector(text=res_list.text)
                dog_tags = sel_list.xpath('//*[@id="channel"]/div[2]/a[1]').extract()
                for text1 in dog_tags:
                    b_href = re.search('href="(.*?)\.html"', text1)
                    if b_href:
                        b_href_str = b_href.group(1).replace("null", "None")
                        # 分页
                        for n in range(1, 100):
                            b_href_str_1 = b_href_str + "-p" + str(n) + ".html"
                            # 获取商品列表
                            shop_list = requests.get(b_href_str_1, headers=headers)
                            shop_sel_list = Selector(text=shop_list.text)
                            shop_tags = shop_sel_list.xpath('//*[@id="listcontent"]/div[2]/div[3]/div/ul/li/div[2]/a').extract()
                            if shop_tags:
                                for text2 in shop_tags:
                                    c_href = re.search('href="(.*?)"', text2)
                                    if c_href:
                                        c_href_str = c_href.group(1).replace("null", "None")
                                        # 获取商品信息
                                        shop_info_list = requests.get(c_href_str, headers=headers)
                                        shop_sel_info_list = Selector(text=shop_info_list.text)
                                        # 当前日期
                                        print(now_time)
                                        # 数据来源
                                        print(c_href_str)
                                        # sku
                                        shop_sku = shop_sel_info_list.xpath('//*[contains(text(),"商品编号")]/span/text()').get()
                                        print(shop_sku)
                                        # 商品名称
                                        shop_name = shop_sel_info_list.xpath('//*[@id="content"]/div[2]/div[1]/div[2]/div[1]/input[@id="goodname"]').get()
                                        shop_name_str = re.search('value="(.*?)"', shop_name).group(1)
                                        print(shop_name_str)
                                        # 厂商
                                        # 品牌
                                        shop_brand = shop_sel_info_list.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/div[2]/dl[1]/dd/a/text()').get()
                                        print(shop_brand)
                                        # 商品价格
                                        shop_price = shop_sel_info_list.xpath('//*[@id="bqPrice"]/text()').get()
                                        shop_price_str = re.search('¥(\S*)', shop_price).group(1)
                                        print(shop_price_str)
                                        # 评分
                                        shop_point = shop_sel_info_list.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/div[2]/dl[4]/dd/div[1]/em/text()').get()
                                        shop_point_str = re.search('(.*)分', shop_point).group(1)
                                        print(shop_point_str)
                                        # 规格包装
                                        shop_ggbz = shop_sel_info_list.xpath('//*[contains(text(),"商品规格")]/span/text()').get()
                                        print(shop_ggbz)
                                        # 销量
                                        shop_sales_num = shop_sel_info_list.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/div[2]/dl[3]/dd/text()').get()
                                        shop_sales_num_str = re.search('(.*)件', shop_sales_num).group(1)
                                        print(shop_sales_num_str)
                                        # 重量
                                        shop_weight = shop_sel_info_list.xpath('//*[contains(text(),"重量")]/span/text()').get()
                                        print(shop_weight)
                                        # 分类
                                        shop_category = shop_sel_info_list.xpath('string(//*[@id="content"]/div[1]/div)').get()
                                        shop_category_str = re.sub("\s","",shop_category)
                                        print(shop_category_str)
                                        print("------------------------")
                                        with connection.cursor() as cursor:
                                            # Create a new record
                                            sql = "INSERT INTO `boqi_goods` (`busi_date`, `data_source`, `sku`, `name`, `brand`, `price`, `point`, `ggbz`, `category`, `sales_num`, `weight`) " \
                                                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                            cursor.execute(sql, (now_time, c_href_str, shop_sku, shop_name_str, shop_brand, shop_price_str, shop_point_str, shop_ggbz,shop_category_str,shop_sales_num_str,shop_weight))
                                            connection.commit()
                            else:
                                break
finally:
    connection.close()