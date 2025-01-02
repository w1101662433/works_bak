from urllib.parse import urlparse, parse_qs, parse_qsl
url = 'http://sys.hibor.com.cn:9999/baogao/home/index?abc=aUqRmPpQvNoPqRsRoPvNwOxO&def=mOoOmNvMiNqQpMjMmOxO8OuNMYmMqRvPnNpN&vidd=5&keyy=TYUGUIYUI&xyz=rQmQnOrRsQxPtQ&op=0'

# 1. 获取各主要参数
path = urlparse(url).path
params = urlparse(url).params
query = urlparse(url).query
# 2. 获取详细查询信息
a= parse_qs(urlparse(url).query)  # {'key':['value']}
b = parse_qsl(urlparse(url).query)  # [('key','value')]


from urllib.parse import urlsplit


domain = urlsplit(url).hostname
print(domain)  # baidu.com
