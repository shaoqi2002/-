import json
import time
import random
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
#随机等待0~0.2s,反反爬（不知道有没有用）
def wait():
    wait=random.random()/5
    time.sleep(wait)
    return 0

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'
}
opt = webdriver.ChromeOptions()
opt.add_argument('--headless')
opt.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opt)
count = 0
start=int(input("请输入从第几页开始爬取"))
n = int(input("请输入要爬取的页数"))
wait()
datas = []
while count < n:
    url='https://travel.qunar.com/p-cs300027-xianggang-meishi?page='+str(start+count)
    driver.get(url)
    # 用headers伪装浏览器
    l = driver.find_elements(By.XPATH, '/html/body/div[3]/div/div[7]/div[1]/div[1]/div[2]/ul/li/div/div[1]/a')
    list=[]
    for i in l:
        list.append(i.get_attribute('href'))
    for link in list:
        data = {}
        driver.get(link)
        time.sleep(random.randint(1,3))
        html=driver.page_source
        selector = etree.HTML(html)
        time.sleep(0.5)
        try:#餐厅名字
            name=driver.find_element(By.XPATH,'//*[@id="js_mainleft"]/div[3]/h1').text
            data["Name"]=name
            wait()
        except:
            data["Name"]="Null"
        #餐厅链接
        data["link"] = link
        id=link.split('-')[1][2:]
        try:#餐厅评分
            score=driver.find_element(By.XPATH,'//*[@id="js_mainleft"]/div[4]/div/div[2]/div[1]/div[1]/span[1]').text
            data["Score"]=score
            wait()
        except:
            data["Score"]="Null"
        try:#人均消费
            avg=driver.find_element(By.XPATH,'//*[@id="js_mainleft"]/div[4]/div/div[2]/div[1]/div[2]/div[2]').text[3:]
            data["Avg"]=avg
            wait()
        except:
            data["Avg"]="Null"
        try:#餐厅简介
            intro=driver.find_element(By.XPATH,'//*[@id="gs"]/div[1]').text
            data["Intro"]=intro
            wait()
        except:
            data["Intro"]="Null"
        wait()
        pack=driver.find_element(By.XPATH,'//*[@id="gs"]/div[2]/div').text
        if pack.find("营业时间:")!=-1:
            data["Open_Time"] = pack.split("营业时间:")[-1].strip()
            pack = pack.split("营业时间:")[0]
        else:
            data["Open_Time"] = "Null"
        if pack.find("电话:")!=-1:
            data["Tel"] = pack.split("电话:")[-1].strip()
            pack = pack.split("电话:")[0]
        else:
            data["Tel"] = "Null"
        if pack.find("地址:")!=-1:
            data["Address"] = pack.split("地址:")[-1].strip()
        else:
            data["Address"]="Null"
        wait()
        try:#特色食物
            special=driver.find_element(By.XPATH,'//*[@id="tjc"]/div[2]').text.split()
            data["Special"]=special
        except:
            data["Special"]="Null"
        try:#交通建议
            tra=driver.find_element(By.XPATH,'//*[@id="jtzn"]/div[2]').text.strip()
            data["Traffic_Advice"]=tra
        except:
            data["Traffic_Advice"]="Null"
        try:#附近景点
            nb_sites={}
            sites=selector.xpath('//*[@id="idContBox"]/ul[1]/li/div[1]/a/text()')
            dists=selector.xpath('//*[@id="idContBox"]/ul[1]/li/div[2]/span[2]/text()')
            for i in range(0,len(sites)):
                nb_sites[sites[i]]=dists[i]
            data["Nb_Sites"]=nb_sites
        except:
            data["Nb_Sites"]="Null"
        try:  # 附近美食
            nb_foods = {}
            foods = selector.xpath('//*[@id="idContBox"]/ul[2]/li/div[1]/a/text()')
            dists = selector.xpath('//*[@id="idContBox"]/ul[2]/li/div[2]/span[1]/text()')
            for i in range(0, len(foods)):
                nb_foods[foods[i]] = dists[i]
            data["Nb_Foods"] = nb_foods
        except:
            data["Nb_Foods"] = "Null"
        try:#附近酒店
            nb_hotels={}
            hotels=selector.xpath('//*[@id="idContBox"]/ul[3]/li/div[1]/a/text()')
            dists = selector.xpath('//*[@id="idContBox"]/ul[3]/li/div[2]/span[2]/text()')
            for i in range(0,len(sites)):
                nb_hotels[hotels[i]]=dists[i]
            data["Nb_Hotels"]=nb_hotels
            wait()
        except:
            data["Nb_Hotels"]="Null"
        try:#附近购物
            nb_shoppings={}
            shoppings=selector.xpath('//*[@id="idContBox"]/ul[4]/li/div[1]/a/text()')
            dists=selector.xpath('//*[@id="idContBox"]/ul[4]/li/div[2]/span[2]/text()')
            for i in range(0,len(sites)):
                nb_shoppings[shoppings[i]]=dists[i]
            data["Nb_Shopping"]=nb_shoppings
            wait()
        except:
            data["Nb_Shopping"]="Null"
        try:#爬取评论
            comments=[]
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
            }
            for i in range(1,11):
                url='https://travel.qunar.com/place/api/html/comments/poi/'+str(id)+'?poiList=true&sortField=1&rank=0&pageSize=10&page='+str(i)
                print(url)
                res = requests.get(url, headers=header)
                res.encoding = 'utf-8'
                source=res.text.split('"data":"')[-1][0:-2]
                selector=etree.HTML(source)
                c_list=selector.xpath('//*[contains(@id,"cmt_item_")]/div[1]/div/div[3]')
                star_list=source.split('cur_star')
                pos=1
                for each in c_list:
                    comments.append([star_list[pos][6],each.xpath('string(.)')])
                    pos+=1
            data["Comments"]=comments
        except:
            data["Comments"]=comments
        print(data)
        datas.append(data)
        wait()
    count+=1
json_str = json.dumps(datas, ensure_ascii=False, indent=4)
with open('food_qunar.json', 'a+', encoding='utf-8') as json_file:
    json_file.write(json_str)
