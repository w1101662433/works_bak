import re, time, random, json, ast, logging, requests, asyncio, base64, platform, os, traceback
from io import StringIO


# -/\.(js|css|jpg|png|gif|svg|woff2|ico|woff)(\?|$)/

class ddict(dict):
    def __init__(self, seq=None, **kwargs):
        # 多维字典：效率比setdefault略低，只有原生dict的1/4，海量数据时请不要使用
        if isinstance(seq, dict):
            for i in seq:
                new_seq = seq[i]
                if not isinstance(new_seq, dict): continue
                seq[i] = ddict(new_seq)
            dict.__init__(self, seq, **kwargs)
        elif seq:
            dict.__init__(self, seq, **kwargs)

    def __getitem__(self, item):
        if item in self:
            return dict.__getitem__(self, item)
        else:
            value = self[item] = type(self)()
            return value

    def __iadd__(self, other):
        if self:
            raise Exception('add forbidden, ddict is not None')
        return other


def sort_dict(dic):
    return dict(sorted(dic.items(), key=lambda x: x[0]))


def cut_dict(dic, keys: list):
    return {k: dic.get(k) for k in keys}


def split_list_to_n_part(old_li, n):
    length = len(old_li)
    cnt = len(old_li) // n if length % n == 0 else len(old_li) // n + 1
    return [old_li[i * cnt:(i + 1) * cnt] for i in range(0, n)]


def judge_time_out(interval=10):
    # 超时装饰器
    def decorator(func):
        def wrapper(*args, **kwargs):
            from func_timeout import func_set_timeout
            fun = func_set_timeout(interval)(func)
            return fun(*args, **kwargs)

        return wrapper

    return decorator


def cut_text(text, length=159):
    t_li = re.findall('.{' + str(length) + '}', text)
    last_text = text[(len(t_li) * length):]
    if last_text: t_li.append(last_text)
    return t_li


def print_error_info(width=159, log=False):
    """用于打印报错信息"""
    fp = StringIO()
    traceback.print_exc(file=fp)
    message = fp.getvalue()
    message_list = sum([[i] if len(i) <= width else cut_text(i, width) for i in message.split('\n')], [])
    max_len = max([len(i) for i in message_list])
    message_list = map(lambda x: '|' + x.ljust(max_len) + '|', message_list)
    message = '+--TRY_EXCEPT:' + '-' * (max_len - 13) + '+\n' + '\n'.join(message_list) + '\n+' + '-' * max_len + '+'
    show_log(message) if log else print(message)
    return message


def get_random_str(length, special_chars=False):
    seed = r"1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if special_chars: seed += r"~!@#$%^&*()_+}{|:?><,./\;=-"
    return "".join([random.choice(seed) for i in range(length)])


def get_random_ip():
    return '.'.join([str(random.randint(0, 255)) for i in range(4)])


def get_host_ip():
    # 获取本机ip
    import socket
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    if '127.0.0.1' in ip:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
    return ip


def print_object_info(obj):
    try:
        print('__dict__.keys: ', obj.__dict__.keys())
        print('__dict__: ', obj.__dict__)
    except:
        print('obj has no __dict__')
    print('dir(): ', dir(obj))


def show_time(*args, **kwargs):
    t_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(t_str, *args, **kwargs)
    return t_str


def str_f_time(t=None, form="%Y-%m-%d %H:%M:%S"):
    t = t or time.time()
    t = str(t).strip()
    if not re.match(r'\d+\.?\d*$', t): return t
    t = float(t)
    if t > 10000000000: t = t // 1000
    return time.strftime(form, time.localtime(t))


def make_time(time_str):
    time_str = time_str.replace('T', ' ').strip()
    time_len = len(re.split(r'[:\- ]', time_str))
    element_dic = {6: [19, "%Y-%m-%d %H:%M:%S"], 3: [10, "%Y-%m-%d"], 5: [16, "%Y-%m-%d %H:%M"], 4: [13, "%Y-%m-%d %H"], 2: [13, "%Y-%m"]}
    for k, v in element_dic.items():
        if time_len == k: return int(time.mktime(time.strptime(time_str[:v[0]], v[1])))


def get_today_start(t=None):
    t = int(t) if t else int(time.time())
    return t - (t + 28800) % 86400


def second_to_time_long(time_long: int):
    day, time_long = divmod(time_long, 86400)
    hour, time_long = divmod(time_long, 3600)
    minute, second = divmod(time_long, 60)
    return "%d %d:%02d:%02d" % (day, hour, minute, second)


def get_delta_day(t=0):
    import datetime
    timedelta = datetime.timedelta
    now = datetime.datetime.fromtimestamp(t) if t else datetime.datetime.now()
    this_week_start = now - timedelta(days=now.weekday())
    this_week_end = now + timedelta(days=6 - now.weekday())
    last_week_start = now - timedelta(days=now.weekday() + 7)
    last_week_end = now - timedelta(days=now.weekday() + 1)
    this_month_start = datetime.datetime(now.year, now.month, 1)
    this_month_end = datetime.datetime(now.year, now.month + 1 if now.month < 12 else 1, 1) - timedelta(days=1)
    last_month_end = this_month_start - timedelta(days=1)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
    this_year_start = datetime.datetime(now.year, 1, 1)
    this_year_end = datetime.datetime(now.year + 1, 1, 1) - timedelta(days=1)
    last_year_end = this_year_start - timedelta(days=1)
    last_year_start = datetime.datetime(last_year_end.year, 1, 1)
    return {
        'this_week_start': get_today_start(this_week_start.timestamp()),
        'this_week_end': get_today_start(this_week_end.timestamp()),
        'last_week_start': get_today_start(last_week_start.timestamp()),
        'last_week_end': get_today_start(last_week_end.timestamp()),
        'this_month_start': get_today_start(this_month_start.timestamp()),
        'this_month_end': get_today_start(this_month_end.timestamp()),
        'last_month_start': get_today_start(last_month_start.timestamp()),
        'last_month_end': get_today_start(last_month_end.timestamp()),
        'this_year_start': get_today_start(this_year_start.timestamp()),
        'this_year_end': get_today_start(this_year_end.timestamp()),
        'last_year_start': get_today_start(last_year_start.timestamp()),
        'last_year_end': get_today_start(last_year_end.timestamp()),
    }


def get_logger():
    logger = logging.getLogger('tornado')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if platform.system() == 'Windows':
        project_name = os.path.abspath(__file__).split(os.sep)[-3]
        log_dir = r'C:/logs/' + str(project_name)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        fh = logging.FileHandler(os.path.join(log_dir, str_f_time(form="%Y%m%d") + '.log'), encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger


logger = get_logger()


def show_log(*args, **kwargs):
    logger.info(" ".join([str(i) for i in args]))


def show_error(*args, **kwargs):
    show_time("【ERROR】", *args, **kwargs)


def show_error_log(*args, **kwargs):
    show_log("【ERROR】", *args)


def get_field_choice_dic(model, field_name):
    choice_trans = {i.name: dict(i.flatchoices) for i in model._meta.fields if i.flatchoices}
    return choice_trans.get(field_name)


def print_json_info(json_data, colorful=True):
    try:
        if isinstance(json_data, str):
            try:
                json_data = ast.literal_eval(json_data)
            except:
                json_data = json.loads(json_data)
        res = json.dumps(json_data, indent=2, ensure_ascii=False)
        if colorful:
            res = re.sub(r'"(.*?)":', '"' + color_it(r'\1') + '":', res)
            res = re.sub(r': "(.*?)"', ': "' + color_it(r'\1', 'blue') + '"', res)
            res = re.sub(r': (\d+)', ': ' + color_it(r'\1', 'green'), res)
            print(res)
    except:
        print('非json:', json_data)


def color_it(string, color='red'):
    color_trans = {'white': 30, 'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'purple': 35, 'lightblue': 36, 'grey': 37}
    return "\033[0;{}m{}\033[0m".format(color_trans.get(color, 31), string)


def strip_html_tag(val):
    val = re.sub(r"<!--.*?-->", '', str(val))
    val = re.sub(r"&.{4};", ' ', val)
    return re.sub(r"<.*?>", '', val)


def url_replace_bracket(url):
    return url.replace('(', "%28").replace(')', "%29")


def match_jsonp(jsonp_str):
    return re.match(".*?({.*}).*", jsonp_str, re.S).group(1)


def retry_get(retry_times=3, session=None, interval=1, status_codes=None, **kwargs):
    return retry_request('GET', retry_times=retry_times, session=session, interval=interval, status_codes=status_codes, **kwargs)


def retry_post(retry_times=3, session=None, interval=1, status_codes=None, **kwargs):
    return retry_request('POST', retry_times=retry_times, session=session, interval=interval, status_codes=status_codes, **kwargs)


def retry_request(method='GET', retry_times=3, session=None, interval=1, status_codes=None, **kwargs):
    for n in range(retry_times):
        try:
            if not kwargs.get('timeout'): kwargs['timeout'] = 30
            res = session.request(method, **kwargs) if session else requests.request(method, **kwargs)
            if status_codes and res.status_code not in status_codes:
                show_log('重试', 'res.status_code', res.status_code)
                time.sleep(interval)
                continue
            return res
        except requests.exceptions.ProxyError as e:
            raise e
        except requests.exceptions.ReadTimeout as e:
            show_log('访问超时, retry', method.lower(), n, kwargs.get('url'))
            if n >= retry_times - 1:
                raise e
        except:
            print_error_info()
            show_log('retry', method.lower(), n, kwargs.get('url'))

        time.sleep(interval)
    raise Exception('获取页面失败:', str(kwargs.get("url")), 'kwargs', kwargs)


def md5(string):
    import hashlib
    h = hashlib.md5()
    h.update(string.encode(encoding='utf-8'))
    return h.hexdigest()


def sha256(data, key):
    from hashlib import sha256
    import hmac
    key = key.encode('utf-8')
    message = data.encode('utf-8')
    return base64.b64encode(hmac.new(key, message, digestmod=sha256).digest()).decode()


def base_64(data):
    return base64.b64encode(str(data).encode()).decode()


def until_success(func, interval=1, times=999999999):
    for i in range(times):
        try:
            return func()
        except:
            time.sleep(interval)


async def until_success_async(func, interval=1, times=999999999):
    for i in range(times):
        try:
            return await func()
        except:
            await asyncio.sleep(interval)


def wave_num(num):
    wave = random.randint(10, 30)
    operator = random.choice(['+', '-'])
    num = (num + wave / 100) if operator == '+' else (num - wave / 100)
    return num


def get_tmp_dir():
    pwd, _name = os.path.split(os.path.abspath(__file__))
    tmp_dir = os.path.join(pwd, '..', 'tmp')
    if not os.path.exists(tmp_dir): os.mkdir(tmp_dir)
    return tmp_dir


def get_cookies_list_from_session(session):
    cookies_list = []
    for i in session.cookies:
        tmp_dic = {'name': i.name, 'value': i.value, 'domain': i.domain, 'path': i.path, 'secure': i.secure}
        cookies_list.append(tmp_dic)
    return cookies_list


def set_cookies_list_for_session(session, cookies_list):
    for cookie in cookies_list:
        tmp_dic = cut_dict(cookie, ['domain', 'name', 'value', 'path', 'secure'])
        session.cookies.set(**tmp_dic)


def get_tmp_json(file_name='cookies.json'):
    tmp_file = os.path.join(get_tmp_dir(), file_name)
    if not os.path.exists(tmp_file): return {}
    with open(tmp_file, 'r', encoding='utf-8') as f:
        data = f.read()
    if not data.strip(): return {}
    return json.loads(data)


def set_tmp_json(file_name='cookies.json', data: [dict, list] = None):
    tmp_file = os.path.join(get_tmp_dir(), file_name)
    with open(tmp_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    a = second_to_time_long(1111)
    print(a)
