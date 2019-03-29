import re
from bs4 import BeautifulSoup
import requests

urls=[]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}
page = requests.get('http://china.huanqiu.com/article/2019-03/14582510.html?agt=15422')
soup = BeautifulSoup(page.text,'lxml')
div1 = soup.find('div',class_='l_a')  # 新闻头
div2 = soup.find('div',class_='la_con')  # 新闻正文
if repr(div1) != "None":
    title = div1.find('h1').text  # 【标题】
    post_time = div1.find('span', class_='la_t_a').text  # 【发布时间】
    post_source = div1.find('span', class_='la_t_b').text  # 【发布来源】
    if repr(div2) != 'None':
        body = div2.find_all('p')
        body = re.sub(r'\n', '', repr(body))
        body = re.sub(r'<!-- Ad.*</script>','',body)
        print('1')