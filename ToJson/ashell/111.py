import requests
import json

url = 'http://www.fivcan.cn:8888/echo'
data = {'hello':'world'}

res = requests.post(url, json=data)
print(res.text)
