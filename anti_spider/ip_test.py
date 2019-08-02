# 通过ip代理绕过ip反爬
"""
A -----> B
A <----- B
A ---告诉C->C ----> B ---->C ---->A
"""

import requests
from scrapy import Selector
import pymysql.cursors
import random
import time


def get_html(url, ips):
    # 代理服务器
    print("开始下载url : {}".format(url))
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "HJK05V4Q9610L73D"
    proxyPass = "48DAAA8CD577EF3E"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }


    # proxies = {
    #     # str(ips['type']).lower(): str(ips['ip_str']).lower(),
    #     "http": str(ips['ip_str']).lower(),
    #     "https": str(ips['ip_str']).lower(),
    #
    # }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    from fake_useragent import UserAgent
    ua = UserAgent(path='/Users/wangchao/PycharmProjects/resources/spider/my_test/useragent.json')
    headers = {
        "User-Agent": ua.random
    }
    print(proxies)
    resp = requests.get(url, headers=headers, proxies=proxies, timeout=2)
    return resp


# 1. 随机去ip可能会重复
# 2. 用的人太多
# 1. 为什么代理可行，在什么情况下ip代理可行()
def get_ip_list():
    connection = pymysql.connect(host='192.168.1.142',
                                 user='root',
                                 password='erp-888888',
                                 db='petgoodsdb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        sql = 'select `ip`,`ip_str`,`port`,`type` from xici limit 16'
        cursor.execute(sql)
        connection.commit()
        return cursor.fetchall()


def method_name():
    for i in range(1, 30):
        job_list_url = "https://www.lagou.com/zhaopin/Python/{}/?filterOption={}".format(i, i)
        job_list_res = get_html(job_list_url, ip_list[random.choice(range(0, len(ip_list)))])
        job_list_html = job_list_res.content.decode("utf8")
        sel = Selector(text=job_list_html)
        all_lis = sel.xpath(
            "//div[@id='s_position_list']//ul[@class='item_con_list']/li//div[@class='position']//a[1]/@href").extract()
        print(all_lis)
        for url in all_lis:
            while 1:
                try:
                    count = random.choice(range(0, len(ip_list)))
                    print(count)
                    job_res = get_html(url, ip_list[count])
                    job_html = job_res.content.decode("utf8")
                    job_sel = Selector(text=job_html)
                    print("下载成功-----------:{}".format(job_sel.xpath("/html/body/div[4]/div/div[1]/div/h2").extract()[0]))
                    break
                except Exception as e:
                    print("下载失败:{}".format(e))
                    continue


def ip_daili():
    pass
    url = 'http://200019.ip138.com/'
    html_str = get_html(url, ip_list[random.choice(range(0, len(ip_list)))]).text
    job_sel = Selector(text=html_str)
    ip_syr = job_sel.xpath("//title/text()").get()
    print(ip_syr)


if __name__ == "__main__":
    ip_list = get_ip_list()
    print(len(ip_list))
    # print(ip_list)
    while 1:
        try:
            ip_daili()
            time.sleep(1)
        except Exception as e:
            print(e)
            pass
    # method_name()
