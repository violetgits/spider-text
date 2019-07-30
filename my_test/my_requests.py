import requests
from lxml import etree
import time
import csv
#定义函数抓取每页前30条商品信息
def crow_first(n):
    #构造每一页的url变化
    url='https://list.jd.com/list.html?cat=6994,6995&page='+n
    head = {'authority': 'search.jd.com',
            'method': 'GET',
            'path': '/list.html?cat=6994,6995&page=1'+n,
            'scheme': 'https',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            }
    r = requests.get(url, headers=head)
    #指定编码方式，不然会出现乱码
    r.encoding='utf-8'
    html1 = etree.HTML(r.text)
    #定位到每一个商品标签li
    datas=html1.xpath('//li[contains(@class,"gl-item")]')
    #将抓取的结果保存到本地CSV文件中
    with open('JD_cw.csv','a',newline='',encoding='utf-8')as f:
        write=csv.writer(f)
        for data in datas:
            p_price = data.xpath('div/div[@class="p-price"]/strong/i/text()')
            p_comment = data.xpath('div/div[5]/strong/a/text()')
            p_name = data.xpath('div/div[@class="p-name p-name-type-2"]/a/em')
            #这个if判断用来处理那些价格可以动态切换的商品，比如上文提到的小米MIX2，他们的价格位置在属性中放了一个最低价
            if len(p_price) == 0:
                p_price = data.xpath('div/div[@class="p-price"]/strong/@data-price')
                #xpath('string(.)')用来解析混夹在几个标签中的文本
            write.writerow([p_name[0].xpath('string(.)'),p_price[0],p_comment[0]])
    f.close()

if __name__=='__main__':
    for i in range(1,101):
        #下面的print函数主要是为了方便查看当前抓到第几页了
        print('***************************************************')
        try:
            print('   First_Page:   ' + str(i))
            crow_first(i)
            print('   Finish')
        except Exception as e:
            print(e)
        print('------------------')
        try:
            print('   Last_Page:   ' + str(i))
            print('   Finish')
        except Exception as e:
            print(e)