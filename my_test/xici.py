# -*- coding=utf-8 -*-
import requests
from bs4 import BeautifulSoup
# from openpyxl import Workbook
import pymysql.cursors
import re

for a in range(1, 100):
    s = requests.session()
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    rs = s.get(url="http://www.xicidaili.com/nn/" + str(a), headers=header)
    soup = BeautifulSoup(rs.text, "lxml")
    print(rs.text)
    ip_list_all = []
    ip_list = soup.select_one("#ip_list").select("tr")
    ip_info_list_key = ["ip", "port", "address", "hidden", "type", "speed", "conn_time", "survival_time", "verify_time"]

    for item in ip_list[1:]:
        ip_info_list_value = []
        ip_info = item.select("td")
        for info in ip_info[1:]:
            if info.select_one(".bar"):
                ip_info_list_value.append(info.select_one(".bar")["title"])
            else:
                ip_info_list_value.append(info.get_text().strip())
        ip_list_all.append(dict(zip(ip_info_list_key, ip_info_list_value)))

    print(len(ip_list_all))
    # 写excel文件
    # w = Workbook()  # 创建一个工作簿
    # ws = w.create_sheet("西刺免费代理IP")  # 创建一个工作表
    # ws.append(['序号','IP地址','端口','服务器地址','是否匿名','类型','速度','连接时间','存活时间','验证时间'])  # 在1行1列写入
    # i = 0
    # for item in ip_list_all:
    #     i += 1
    #     ws.append([str(i),item["ip"],item["port"],item["address"],item["hidden"],item["type"],item["speed"],item["conn_time"],item["survival_time"],item["verify_time"]])
    # w.save(u"西刺免费代理IP.xlsx")  # 保存
    # print("写excel完成")
    # 存入数据库
    connection = pymysql.connect(host='192.168.1.142',
                                 user='root',
                                 password='erp-888888',
                                 db='petgoodsdb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        for item in ip_list_all:
            ip_sql = item["type"] + "://" + item["ip"] + ":" + item["port"]
            data_list = (item["ip"], ip_sql, item["port"], item["address"], item["hidden"], item["type"], item["speed"], item["conn_time"], item["survival_time"], item["verify_time"])
            survival = re.search("\d+", item["survival_time"]).group(0)
            if int(survival) > 100:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO `xici` (`ip`, `ip_str`,`port`, `address`, `hidden`, `type`, `speed`, `conn_time`, `survival_time`, `verify_time`) " \
                          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, data_list)
                    connection.commit()
    finally:
        connection.close()
