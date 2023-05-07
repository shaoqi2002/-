import json
import time
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By


web="https://www.tripadvisor.cn/Restaurants-g294217-Hong_Kong.html"
def get_info(link):
    data={}
    opt = webdriver.ChromeOptions()
    opt.add_argument('--headless')
    opt.add_argument('--disable-gpu')
    opt.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"')
    driver = webdriver.Chrome(options=opt)
    driver.get(link)
    time.sleep(10)
    html=driver.page_source
    selector=etree.HTML(html)
    # 餐厅名字
    name=selector.xpath('/html/body/div[2]/div/div[6]/div[1]/div[1]/div/div/div/div/div[1]/div[1]/h1/text()')[0]
    data["Name"]=name
    print(name)
    #餐厅链接
    data["Link"]=link
    #餐厅排名
    rank_i=selector.xpath('/html/body/div[2]/div/div[6]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/span/a/text()')[0]
    rank=rank_i[0:5]+rank_i[-18:-3]+"个）"
    data["Rank"]=rank
    print(rank)
    #餐厅tag
    tags=selector.xpath('/html/body/div[2]/div/div[6]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/div/a/text()')
    data["Tags"]=tags
    print(tags)
    #餐厅位置
    position=selector.xpath('/html/body/div[2]/div/div[6]/div[1]/div[1]/div/div/div/div/div[2]/div/div[2]/div/div[1]/div/span[2]/span/text()')[0]
    data["Position"]=position
    print(position)
    #餐厅评分
    score=selector.xpath('/html/body/div[2]/div/div[7]/div/div[1]/div/div/div/div[1]/div/div/div[1]/div[1]/span[1]/text()[1]')[0][-4:]
    data["Score"]=score
    print(score)
    #附近酒店
    try:
        nb_hotels={}
        hotel_names=selector.xpath('//*[@id="taplc_resp_hr_nearby_ar_responsive_0"]/div/div[3]/div/div/div/div/div[1]/div[2]/div[1]/text()')
        print(hotel_names)
        dists=selector.xpath('//*[@id="taplc_resp_hr_nearby_ar_responsive_0"]/div/div[3]/div/div/div/div/div/div[2]/div[4]/text()')
        for i in range(0,len(hotel_names)):
            nb_hotels[hotel_names[i]]=dists[i]
        data["Nb_Hotels"]=nb_hotels
        print(nb_hotels)
    except:
        data["Nb_Hotels"]="Null"
    #附近餐厅
    try:
        nb_food={}
        food_names=selector.xpath('//*[@id="taplc_resp_hr_nearby_ar_responsive_0"]/div/div[4]/div/div/div/div/div[1]/div[2]/div[1]/text()')
        dists=selector.xpath('//*[@id="taplc_resp_hr_nearby_ar_responsive_0"]/div/div[4]/div/div/div/div/div[1]/div[2]/div[4]/text()')
        for i in range(0,len(food_names)):
            nb_food[food_names[i]]=dists[i]
        data["Nb_Restaurants"]=nb_food
        print(nb_food)
    except:
        data["Nb_Restaurants"]="Null"
    #评论
    comments=[]
    for page in range(0,10):
        comment=selector.xpath('//*[@id="component_10"]/div/div[3]/div/div[3]/div[3]/div[1]/div[1]/q/span/text()')
        '//*[@id="component_10"]/div/div[3]/div[2]/div[3]/div[4]/div[1]/div[1]/q/span'
        for each in comment:
            comments.append(each)
        try:
            driver.find_element(By.XPATH,'//*[@id="component_10"]/div/div[3]/ul/li[10]').click()
            time.sleep(0.5)
            html=driver.page_source
            selector=etree.HTML(html)
        except:
            break
    data["Comments"]=comments
    print(comments)
    return data




opt = webdriver.ChromeOptions()
opt.add_argument('--headless')
opt.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opt)
driver.get(web)
datas=[]
start=int(input("请输入从第几页开始爬取"))
n = int(input("请输入要爬取的页数"))
for i in range(0,start-1):
    driver.find_element(By.XPATH,'//*[@id="BODYCON"]/div[5]/div/ul/li[10]').click()
    time.sleep(1)
for page in range(0,n):
    html=driver.page_source
    selector=etree.HTML(html)
    links=selector.xpath('//*[@id="taplc_hsx_hotel_list_lite_dusty_hotels_combined_sponsored_0"]/div/div/div[1]/div[2]/div[1]/div/span/a/@href')
    for q in range(0,len(links)):
        links[q]="https://www.tripadvisor.cn/"+links[q]
    for each in links:
        datas.append(get_info(each))
    driver.find_element(By.XPATH, '//*[@id="BODYCON"]/div[5]/div/ul/li[10]').click()
    time.sleep(1)


with open('tripadvisor.json', 'a+', encoding='utf-8') as json_file:
    json_str = json.dumps(datas, ensure_ascii=False, indent=4, )
    json_file.write(json_str)
