# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import pymysql
import warnings
warnings.filterwarnings("ignore")

# 获取html页面
def GetPage(url1):
    headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    data = requests.get(url1, headers=headers).content.decode('utf-8')
    return data


# 解析ListPage，返回新闻列表的链接
def TakenList(page,kind):
    urls=[]
    soup_all=[]
    soup = BeautifulSoup(page,'lxml')
    if kind== '国际要闻':
        soup_a = soup.find('ul',class_='newList01')  #头条列表
        soup_a = soup_a.find_all('a')
        soup_b = soup.find('ul',id='gd_content',class_='newestList')  #最新播报
        soup_b = soup_b.find_all('a')
        soup_c = soup.find('div',class_='partL')   #乱七八糟的新闻列表
        soup_c = soup_c.find_all('a')
        soup_all.extend(soup_a)
        soup_all.extend(soup_b)
        soup_all.extend(soup_c)  # 把所有新闻标签放在一起  然后取url
    elif  kind=='国内新闻':
        soup_a = soup.find('ul',id='gd_content',class_='newestList')  #头条列表
        soup_a = soup_a.find_all('a')
        soup_all.extend(soup_a)
    for x in soup_all:
        url2=x.get('href')
        url2=re.match('http.*htm',url2)
        if url2:
            urls.append(url2.group())

    return urls


# 将新闻url添加到数据库中
def Url_Sql(urls, category1):
    conn = pymysql.connect(host="localhost", user="root", passwd="aiyunfei19990719", db="news_xinhua", port=3306, charset="utf8")
    cur = conn.cursor()  # 利用连接对象得到游标对象
    for url2 in urls:
        cur.execute("insert ignore into titles (url,category) values (%s,%s)",
                    (url2, category1))  # 此句行过程中，若数据库中已经存在目标utl，则不进行存储，并抛出一条警告
    conn.commit()
    cur.close()
    conn.close()


# 获取数据库中flag为0的url，返回urls[]
def GetSql():
    conn = pymysql.connect(host="localhost", user="root", passwd="aiyunfei19990719", db="news_xinhua", port=3306, charset="utf8")
    cur = conn.cursor()  # 利用连接对象得到游标对象
    cur.execute("select url,category from titles where flag=0")
    lines = cur.fetchall()
    cur.close()
    conn.close()
    return lines

#TODO
#解析出来的网页的中文变乱码了  在得到requests后对content进行译码
# 解析NewsPage
def TakenNews(data):
    analysis = {}
    soup = BeautifulSoup(data, 'lxml')
    div1 = soup.find('div', class_='h-news')    #新闻
    div2 = soup.find('div', class_='p-right left')  # 新闻正文
    if repr(div1) != "None":
        title = div1.find('div',class_='h-title').text  # 【标题】
        post_time = div1.find('span', class_='h-time').text # 【发布时间】
        post_source = div1.find('span', class_=None)  # 【发布来源】
        if repr(post_source)!='None':
            try:
                post_source = post_source.text
            except:
                post_source = post_source.find('em',id='source').text
        if repr(div2) != 'None':
            body=div2.find_all('p')
            body=re.sub(r'\n','',repr(body))                   #解析出正文内容
            analysis['state'] = "成功解析"   #解析状态
            analysis['title'] = title
            analysis['time'] = post_time
            analysis['source'] = post_source
            analysis['body'] = body
    else:
        analysis['state'] = "无法解析"
    return analysis

def Notsql(purl):  #无法解析 flag改为2
    conn = pymysql.connect(host="localhost", user="root", passwd="aiyunfei19990719", db="news_xinhua", port=3306, charset="utf8")
    cur = conn.cursor()
    try:
        cur.execute("update titles set flag=2 where url=%s",purl)
        conn.commit()
    except:
        print('error')
    finally:
        cur.close()
        conn.close()

def Putsql(analysis, category1, purl):  # 将新闻具体信息存入news表中  标题  日期   来源   第一张图片地址 文本内容  类别
    conn = pymysql.connect(host="localhost", user="root", passwd="aiyunfei19990719", db="news_xinhua", port=3306,
                           charset="utf8")
    cur = conn.cursor()
    try:
        cur.execute("insert into news(title,date,source,content,category) values (%s,%s,%s,%s,%s)",
                    (analysis['title'], analysis['time'], analysis['source'], analysis['body'],
                     category1))
        cur.execute("update titles set flag=1 where url=%s", purl)
        conn.commit()
    except:
        cur.execute("update titles set flag=2 where url=%s", purl)
        conn.commit()
    finally:
        cur.close()
        conn.close()
        print("成功添加新闻", analysis['title'], "\n")


# main
count = 0
NewsCategory = {
                '国际要闻': 'http://www.xinhuanet.com/world/index.htm',
                 '国内新闻': 'http://www.news.cn/local/index.htm'
                }    #新闻主页面词典
for category in NewsCategory:
    print("正在获取" + category + "新闻列表")
    category_url = NewsCategory[category]
    list_page = GetPage(category_url)  # 获取主页面
    list_urls = TakenList(list_page,category)  # 解析出单个新闻标题列表数据
    Url_Sql(list_urls, category)  # 将列表放入数据库
    print(category + "列表更新完成，开始获取新闻")
    page_urls = GetSql()  # 从数据库获取未访问过的列表
    # 依次访问这些列表
    for page_url in page_urls:
        url = ''.join(list(page_url[0]))  # 取出新闻地址
        Category = ''.join(list(page_url[1]))  # 取出新闻类型
        news_text = GetPage(url)  # 获取新闻内容页面
        analysis_result = TakenNews(news_text)  # 解析出标题、内容等信息
        if analysis_result['state'] == "成功解析":
            Putsql(analysis_result, Category, url, )
            count = count + 1
        elif analysis_result['state'] == "无法解析":
            Notsql(url)
            print("无法解析页面：" + url + "，已跳过")
print('本次新闻获取已完成，共更新"' + repr(count) + '"条新闻。')