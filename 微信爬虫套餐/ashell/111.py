from libs.print_error_info import *

qiu_gou_re = r'有货私聊|有货私|求购|有货请私聊|有的私聊|有的联系|有货的联系|有货联系|有现货联系|急求|有现货请私聊|采购|秒付|急求|有货的请联系|有货联系|有货的私信|有货请联系|找|需求|急需|急求|求购|求'
chu_sou_re = r'出售|需要的联系我|工厂现货|出|热卖|卖|优势出|需要的联系|销|价格美丽|需要|出现货|出货|售|销售|需要的|推荐|主推|优势|到货|一手货源|必出|供应|询价|特价|offer'

# 接插件
# model_li_re = r'[A-Za-z0-9][A-Za-z0-9-\.\(\)\/]{3,30}[A-Za-z0-9\)](?<!PCS|.PK)'

# IC
model_li_re = r'^[a-zA-Z][\w\/,-\.\(\)\_\*\+&#]*\d+[\w\/,-\.\(\)\*\+&#]*[a-zA-Z\d\)\*#]'


def get_model_li(message):
    resp = set()
    for line in [i.strip() for i in model_li_re.split('\n') if i.strip()]:
        # print('line', line)

        line = '([^a-zA-Z0-9]|^)(' + line + ')([^a-zA-Z0-9]|$)'
        message = message.replace('（', '(')
        message = message.replace('）', ')')
        message = message.strip()
        for block in message.split():
            find_all = re.findall(line, block, re.IGNORECASE)
            # print('find_all', find_all)
            if find_all:
                find_all = {i[1] for i in find_all}
                resp |= find_all

    return list(resp)


def handle_message(json_data):
    msg = json_data.get('message', '')
    is_qiu_gou = 0
    if re.search(qiu_gou_re, msg):
        is_qiu_gou = 1
    if re.search(chu_sou_re, msg):
        is_qiu_gou = 2

    for model_name in get_model_li(message=msg):
        send_data = {
            'action': is_qiu_gou,  # 1：求购 2：出售
            'type': 1,  # 1：微信 2：QQ
            'partnum': model_name,
            'code': json_data.get('wxid', ''),
            'nick': json_data.get('nickname', ''),
            'group': json_data.get('sender', ''),
            'desc': json_data.get('message', ''),
        }

        send_message(send_data)


def send_message(json_data):
    show_log('发送:', json_data)
    url = 'http://api.mrchip.cn/WechatCrawl/writeChipPart?tok=05F76977D146F9C8'
    res = retry_post(url=url, json=json_data, retry_times=9)
    show_log('res:', res.text)


if __name__ == '__main__':
    json_data = {
        "msgid": 495967493958363243,
        "wxid": "wxid_qk4h0a9xn8eu21",
        "nickname": "BIGTOM",
        "message": """90121-0784	2416	
RT425730/9-1393243-3	2000	
503480-2600	36K	
90130-1116	15K	求购现货，有货私聊""",
        "time": "2023-06-19 11:40:21",
        "sender": "38974356001@chatroom"
    }

    handle_message(json_data)
