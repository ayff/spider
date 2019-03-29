import  pymysql
conn=pymysql.connect(host="localhost", user="root", passwd="aiyunfei19990719",port=3306, charset="utf8")  #连接MySql
cursor=conn.cursor()           #获取当前光标位置
cursor.execute('create database news_huanqiu;')   #建立相应数据库  环球时报  读取国际和国内
cursor.execute('use news_huanqiu;')             #使用相应数据库
cursor.execute('create table titles(url varchar(100) primary key,'   
               'category varchar(10),flag tinyint not null default 0);')   #建立titles表  存url  存分类  标记是否获取内容
cursor.execute('create table news(newsId bigint primary key auto_increment,'   #建立news表   新闻id
               'title varchar(40),'                     #标题
               'content text,'                           #正文
               'date timestamp,'                        #日期
               'category varchar(10),'                  #分类
               'source varchar(50));')                   #来源
conn.commit()
cursor.close()
print('建立数据库 news_huanqiu 完成')
