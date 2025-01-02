import requests
from libs.print_error_info import *

# url = 'http://localhost:11001/item_info'
# # url = 'http://178.236.41.165:11001/item_info'
# data = {"url": "https://page.auctions.yahoo.co.jp/jp/auction/r74690384"}
# res = requests.post(url=url, json=data)
# print_json_info(res.text)

url = 'http://localhost:8888/echo'
# url = 'http://178.236.41.165:11001/item_info'
data = {"url": "https://page.auctions.yahoo.co.jp/jp/auction/m1059682411", "price": 1600}
res = requests.post(url=url, json=data)
print_json_info(res.text)
