import re
test = '							2019-03-26 15:51 来源：澎湃新闻'
a=re.search('.*\d{4}\-\d{2}\-\d{2}', test)
if a:
    print('ok')
    a = re.sub(r'<span>.*</span>','', a.group())
    a = re.sub('\t*','',a)
    print(a)
else:
    print('failed')