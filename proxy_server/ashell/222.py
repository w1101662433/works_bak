import requests
from libs.proxy_tools import *


res = requests.get('http://ip.tool.lu/', proxies=frequent_proxies, headers={'a':'12312312'})
print(res.text)
