import re
import execjs
import requests
import json
import hashlib
import time
from lxml import etree
from requests.utils import add_dict_to_cookiejar
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.common.by import By
# 关闭ssl验证提示
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
    'Host' : 'www.mafengwo.cn'
}
session = requests.session() #使用session会一直携带上一次的cookies
def get_html(url):
    session = requests.session()  # 使用session会一直携带上一次的cookies
    response = session.get(url, headers=header, verify=False)  # 直接访问得到JS代码
    js_clearance = re.findall('cookie=(.*?);location', response.text)[0]  # 用正则表达式匹配出需要的部分
    #
    result = execjs.eval(js_clearance).split(';')[0].split('=')[1]  # 反混淆、分割出cookie的部分
    add_dict_to_cookiejar(session.cookies, {'__jsl_clearance_s': result})  # 将第一次访问的cookie添加进入session会话中
    response = session.get(url, headers=header, verify=False)  # 带上更新后的cookie进行第二次访问
    go = json.loads(re.findall(r'};go\((.*?)\)</script>', response.text)[0])
    for i in range(len(go['chars'])):
        for j in range(len(go['chars'])):
            values = go['bts'][0] + go['chars'][i] + go['chars'][j] + go['bts'][1]
            if go['ha'] == 'md5':
                ha = hashlib.md5(values.encode()).hexdigest()
            elif go['ha'] == 'sha1':
                ha = hashlib.sha1(values.encode()).hexdigest()
            elif go['ha'] == 'sha256':
                ha = hashlib.sha256(values.encode()).hexdigest()
            if ha == go['ct']:
                __jsl_clearance_s = values
    add_dict_to_cookiejar(session.cookies, {'__jsl_clearance_s': __jsl_clearance_s})
    response = session.get(url, headers=header, verify=False)
    return response.text


category={9472:'快餐',16089:'连锁/加盟',7558:'酒吧',16088:'主题',35399:'下午茶',36817:'早午餐',39590:'特色',16070:'西北菜',16116:'港式',20340:'西餐',15968:'东南亚美食',7523:'海鲜',7535:'小吃',7665:'粥店面食',35177:'咖啡饮品'}
url='https://www.mafengwo.cn/poi/758.html'
def get_info(html,url):
    selector=etree.HTML(html)
    data={}
    #记录餐厅链接
    data['Link']=url
    #获取餐厅名字
    name=selector.xpath('/html/body/div[3]/div[2]/div[1]/div[1]/div/h1/text()')[0].strip()+selector.xpath('/html/body/div[3]/div[2]/div[1]/div[1]/div/text()')[1].strip()
    data['Name']=name
    #获取餐厅简介
    intro=selector.xpath('/html/body/div[3]/div[2]/div[1]/div[2]/dl/dd[1]/text()')[0]
    data['Intro']=intro
    #获取餐厅评分
    score=selector.xpath('/html/body/div[3]/div[2]/div[1]/div[2]/div/span[1]/em/text()')[0]
    data['Score']=score
    #获取餐厅地址
    address=selector.xpath('/html/body/div[3]/div[3]/div[3]/ul/li[1]/text()')[1].strip()[3:]
    data['Address']=address
    #获取联系电话
    tel=selector.xpath('/html/body/div[3]/div[3]/div[3]/ul/li[2]/text()')[1].strip()
    data['Tel']=tel
    #获取附近酒店
    nb_hotels={}
    hotel_list=selector.xpath('/html/body/div[3]/div[3]/div[5]/ul/li/h3/a')
    n=1
    for item in hotel_list:
        name=selector.xpath('/html/body/div[3]/div[3]/div[5]/ul/li['+str(n)+']/h3/a/@title')[0]
        dist=selector.xpath('/html/body/div[3]/div[3]/div[5]/ul/li['+str(n)+']/p/text()[2]')[0]
        nb_hotels[name]=dist
        n+=1
    data['Nb_Hotels']=nb_hotels
    #获取附近景点
    nb_sites={}
    sites_list=selector.xpath('/html/body/div[3]/div[3]/div[6]/ul/li/h3/a')
    n=1
    for item in sites_list:
        name=selector.xpath('/html/body/div[3]/div[3]/div[6]/ul/li['+str(n)+']/h3/a/@title')[0]
        dist=selector.xpath('/html/body/div[3]/div[3]/div[6]/ul/li['+str(n)+']/p/text()[2]')[0]
        nb_sites[name]=dist
        n+=1
    data['Nb_Sites']=nb_sites
    #获取附近美食
    nb_food={}
    food_list=selector.xpath('/html/body/div[3]/div[3]/div[7]/ul/li/h3/a')
    n=1
    for item in sites_list:
        name=selector.xpath('/html/body/div[3]/div[3]/div[7]/ul/li['+str(n)+']/h3/a/@title')[0]
        dist=selector.xpath('/html/body/div[3]/div[3]/div[7]/ul/li['+str(n)+']/p/text()[2]')[0]
        nb_food[name]=dist
        n+=1
    data['Nb_Food']=nb_food
    return data

url='https://m.mafengwo.cn/cy/10189/gonglve.html?sExt=gonglve'
opt = webdriver.ChromeOptions()
opt.add_argument('--headless')
opt.add_argument('--disable-gpu')
user_ag='MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; '+'CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
opt.add_argument('user-agent=%s'%user_ag)
driver = webdriver.Chrome(options=opt)
start=int(input('请输入要从第几组数据开始爬取：'))
n=int(input('请输入要爬取的数据组数：'))
driver.get(url)
for n in range(0,start+n):
    driver.find_element(By.XPATH,'//*[@id="btn_getmore"]/a').click()
    time.sleep(1)
datas=[]
for num in range(start,start+n):
    xpath='//*[@id="poi_list"]/section['+str(num)+']/div/a'
    list=driver.find_elements(By.XPATH,xpath)
    for each in list:
        link='https://www.mafengwo.cn/poi/'+each.get_attribute('href')[26:].split('?')[0]
        html=get_html(link)
        try:
            category=each.text.split('\n')[2].split()
            business_district=each.text.split('\n')[3]
            data=get_info(html, link)
            data['Category']=category
            data['Business_District']=business_district
            datas.append(data)
        except:
            pass
json_str = json.dumps(datas, ensure_ascii=False, indent=4)
with open('C:/Users/17426/Desktop/food_mafengwo.json', 'a+', encoding='utf-8') as json_file:
    json_file.write(json_str)


