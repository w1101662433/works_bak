from libs.print_error_info import *

proxy_error_times = 0
proxy_server = '192.168.1.38:10086'
proxy_server2 = '192.168.1.38:10087'

# frequent_proxy_server = '16JPKSJI:316608@u6544.5.tn.16yun.cn:6441'
frequent_proxy_server = '16IAZLFP:860952@u6544.5.tn.16yun.cn:6441'
frequent_proxy_server = '16EOBZOI:860952@u6544.10.tp.16yun.cn:6446'

default_proxies = {'http': proxy_server, 'https': proxy_server}
default_proxies2 = {'http': proxy_server2, 'https': proxy_server2}
frequent_proxies = {'http': frequent_proxy_server, 'https': frequent_proxy_server}


def __get_new_proxy(private=False):
    global proxy_error_times
    # url = 'http://http.tiqu.letecs.com/getip3?num=1&type=2&pro=&city=0&yys=0&port=11&pack=243764&ts=1&ys=1&cs=1&lb=1&sb=0&pb=4&mr=1&regions=&gm=4'
    url = 'http://http.tiqu.letecs.com/getip_3h?num=1&type=2&pro=320000&city=0&yys=100017&port=1&pack=248517&ts=1&ys=1&cs=1&lb=1&sb=0&pb=5&mr=1&regions='
    res = requests.get(url=url)
    show_log('get_new_proxy')
    show_log(res.text)
    data = res.json().get('data', [])

    if '秒后再试' in res.text:
        time.sleep(2)
        res = requests.get(url=url)
        show_log(res.text)
        data = res.json().get('data', [])

    if not data or '今日套餐已用完' in res.text:
        show_log(Exception('【ERROR】获取代理失败'))
        return '127.0.0.1:10809', int(time.time()) + 1200

    proxy, expire_time = data[0].get('ip') + ':' + str(data[0].get('port')), data[0].get('expire_time')
    tmp_dir = get_tmp_dir(root=not private)
    tmp_file = os.path.join(tmp_dir, 'proxy.tmp')
    with open(tmp_file, 'w') as f:
        f.write(proxy + ' ' + str(make_time(expire_time)))

    proxy_error_times = 0
    return proxy, expire_time


def get_proxy(force_fresh=False, private=False):
    global proxy_error_times
    now = int(time.time())
    tmp_dir = get_tmp_dir(root=not private)
    show_log('tmp_dir', tmp_dir)
    tmp_file = os.path.join(tmp_dir, 'proxy.tmp')
    if not os.path.exists(tmp_file):
        data = None
    else:
        with open(tmp_file, 'r') as f:
            data = f.readline()
            show_log('data', data)

    if not data:
        proxy, expire_time = __get_new_proxy(private=private)

    else:
        proxy, expire_time = data.split()
        if force_fresh:
            proxy_error_times += 1
            show_log('proxy_error_times', proxy_error_times)
            with open(tmp_file, 'w') as f:
                f.write(proxy + ' ' + str(expire_time))
        if int(expire_time) < now + 150 or proxy_error_times >= 10:
            proxy, expire_time = __get_new_proxy(private=private)
    return proxy


if __name__ == '__main__':
    get_proxy()
