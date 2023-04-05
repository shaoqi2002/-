import json
import time
import random
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By

#随机等待0~0.5s,反反爬（不知道有没有用）
def wait():
    wait=random.random()/2
    time.sleep(wait)
    return 0

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44'
}
opt = webdriver.ChromeOptions()
opt.add_argument('--headless')
opt.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opt)
url = "https://you.ctrip.com/restaurantlist/hongkong38.html"
count = 0
start=int(input("请输入从第几页开始爬取"))-1
for i in range(0,start):
    driver.get(url)
    url = driver.find_element(By.XPATH,
                              '//*[@id="content"]/div[4]/div/div[2]/div/div[3]/div[16]/div/a[7]').get_attribute('href')
n = int(input("请输入要爬取的页数"))
wait()
datas = []
while count < n:
    driver.get(url)
    # 用headers伪装浏览器
    list1 = driver.find_elements(By.XPATH, '//*[@id="content"]/div[4]/div/div[2]/div/div[3]/div/div[3]/dl/dt/a')
    list = []
    for p in list1:
        list.append(p.get_attribute('href'))
    for item in list:  # 当前页的所有酒店
        data = {}  # 以字典形式储存每个餐厅数据
        res = requests.get(item, headers=headers)
        res.encoding = 'utf-8'
        html = res.text
        selector = etree.HTML(html)
        # 获取餐厅名字
        name = selector.xpath('//*[@id="content"]/div[2]/div[2]/div/div[1]/h1/text()')[0]
        data["Name"] = name
        #餐厅链接
        data["Link"]=item
        # 获取餐厅评分
        try:
            score = selector.xpath('//*[@id="content"]/div[3]/div/div[1]/div[1]/ul/li[1]/span/b/text()')[0]
            data["Score"] = score
        except:
            data["Score"] = "Null"
        #获取餐厅菜系
        try:
            styles=[]
            s=selector.xpath('//*[@id="content"]/div[3]/div/div[2]/div[1]/ul/li[2]/span[2]/dd/a')
            pos=1
            for i in s:
                stuff=selector.xpath('//*[@id="content"]/div[3]/div/div[2]/div[1]/ul/li[2]/span[2]/dd/a['+str(pos)+']/text()')
                styles.append(stuff[0])
                pos+=1
            data["Style"]=styles
        except:
            data["Style"]="Null"
        wait()
        # 获取餐厅位置
        try:
            address = selector.xpath('//*[@id="content"]/div[3]/div/div[2]/div[1]/ul/li[4]/span[2]/text()')[0]
            data["Address"] = address
        except:
            data["Adress"] = "Null"
        # 获取餐厅介绍,并去除前部空格
        try:
            intro = selector.xpath('//*[@id="content"]/div[3]/div/div[1]/div[3]/div[1]/div[1]/text()')[0].strip()
            data["Intro"] = intro
        except:
            data["Intro"] = "Null"
        wait()
        #获取特色食物
        try:
            set=selector.xpath('//*[@id="content"]/div[3]/div/div[1]/div[3]/div[1]/div[2]/p/text()')[0].split(',')
            foods=[]
            for food in set:
                foods.append(food.strip())
            data["Food"]=foods
        except:
            data["Food"]=foods
        # 获取人均消费
        try:
            avg = selector.xpath('//*[@id="content"]/div[3]/div/div[2]/div[1]/ul/li[1]/span[2]/em/text()')[0]
            data["Avg_consumption"] = avg
        except:
            data["Avg_consumption"] = "Null"
        wait()
        # 获取联系电话
        try:
            tel = selector.xpath('//*[@id="content"]/div[3]/div/div[2]/div[1]/ul/li[3]/span[2]/text()')[0]
            data["tel"] = tel
        except:
            data["tel"] = "Null"
        # 获取附近酒店,这部分性能有问题
        driver.get(item)
        try:
            nb_hotel_list = driver.find_elements(By.XPATH, '//*[@id="dest_NearHotel"]/ul/li/dl/dt/a')
            hotels = []
            pos = 1
            for hotel in nb_hotel_list:
                # 酒店名字
                hotel_name = driver.find_element(By.XPATH,
                                                 '//*[@id="dest_NearHotel"]/ul/li[' + str(pos) + ']/dl/dt/a').text
                # 距离
                hotel_dist = driver.find_element(By.XPATH, '//*[@id="dest_NearHotel"]/ul/li[' + str(
                    pos) + ']/dl/dd[2]').text.split()[1]
                pos += 1
                hotels.append([hotel_name,hotel_dist])
            data["Nb_Hotels"] = hotels
        except:
            data["Nb_Hotels"] = "Null"
        wait()
        #获取附近餐厅和距离
        nb_restaurants_list = driver.find_elements(By.XPATH, '//*[@id="content"]/div[3]/div/div[2]/div[3]/ul/li/dl/dt/a')
        restaurants = []
        pos = 1
        for restaurant in nb_restaurants_list:
            # 酒店名字
            restaurant_name = driver.find_element(By.XPATH,
                                             '//*[@id="content"]/div[3]/div/div[2]/div[3]/ul/li['+str(pos)+']/dl/dt/a').text
            # 距离
            restaurant_dist = driver.find_element(By.XPATH, '//*[@id="content"]/div[3]/div/div[2]/div[3]/ul/li['+str(pos)+']/dl/dd[2]').text.split()[0]
            pos += 1
            restaurants.append([restaurant_name,restaurant_dist])
        data["Nb_Restaurants"] = restaurants
        # 把餐厅信息压入json文件
        print(data)
        datas.append(data)
    # 翻页
    count += 1
    driver.get(url)
    url = driver.find_element(By.XPATH,
                              '//*[@id="content"]/div[4]/div/div[2]/div/div[3]/div[16]/div/a[7]').get_attribute('href')
json_str = json.dumps(datas, ensure_ascii=False, indent=4)
with open('C:/Users/17426/Desktop/food_ctrip.json', 'a+', encoding='utf-8') as json_file:
    json_file.write(json_str)
