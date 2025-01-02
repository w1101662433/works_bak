import asyncio
import inspect
from pyppeteer import launch
from typing import Optional
from pyppeteer.network_manager import statusTexts
from libs.print_error_info import *
from pyppeteer.element_handle import ElementHandle
from pyppeteer_stealth import stealth
from urllib.parse import quote
import numpy as np

# linux安装需要的依赖
# yum install pango.x86_64 libXcomposite.x86_64 libXcursor.x86_64 libXdamage.x86_64 libXext.x86_64 libXi.x86_64 libXtst.x86_64 cups-libs.x86_64 libXScrnSaver.x86_64 libXrandr.x86_64 GConf2.x86_64 alsa-lib.x86_64 atk.x86_64 gtk3.x86_64 -y
# yum install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm -y

# 日文乱码：
# yum -y groupinstall "X Window System"
# yum -y groupinstall chinese-support
# yum -y groupinstall Fonts

# windows日志位置：
# C:\Users\Administrator\AppData\Local\pyppeteer\pyppeteer

# 安装linux桌面
# yum -y localinstall http://www.rpmfind.net/linux/centos/7.9.2009/os/x86_64/Packages/xorg-x11-server-Xvfb-1.20.4-10.el7.x86_64.rpm
# /usr/bin/xvfb-run python3 spider.py

# 插件位置：
# C:\Users\Administrator\AppData\Local\google\Chrome\User Data\Default\Extensions

execute_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if platform.system() != "Windows":
    execute_path = r"/usr/bin/google-chrome"

# 常见崩溃关键字
destroy_key_words = ['Execution context was destroyed', 'Most likely the page has been closed',
                     'connection unexpectedly closed', 'Target closed', 'Session closed']


async def evaluate_with_timeout(page, timeout=10, *args, **kwargs):
    try:
        coro = page.evaluate(*args, **kwargs)
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        show_log('Evaluation timed out.')


async def judge_display(page, css_selector):
    js = "nodes => [...nodes].filter(n=> getComputedStyle(n).display != 'none' && getComputedStyle(n).visibility != 'hidden')"
    return await page.JJeval(css_selector, js)


async def wait_for_xpath(page, xpath_str, timeout=30):
    for i in range(timeout):
        ele = await page.xpath(xpath_str)
        if ele:
            return ele
        else:
            await asyncio.sleep(1)


async def wait_js_element_handle(page, js_path, timeout=30):
    # js_path = ''document.querySelector("#rXOa8 > div > div").shadowRoot.querySelector("iframe").ownerDocument''
    for i in range(timeout):
        try:
            ele = await page.evaluateHandle(js_path)
            if isinstance(ele, ElementHandle):
                return ele
        except:
            await asyncio.sleep(1)
    else:
        show_error_log('等待元素出现失败')
        return None


async def retry_goto(page, url, retry_times=3, timeout=30, ignore_timeout=False, interval=3, **kwargs):
    options = {'timeout': timeout * 1000, 'waitUntil': ['domcontentloaded', 'networkidle2']}
    for n in range(retry_times):
        try:
            return await asyncio.wait_for(page.goto(url, options=options, **kwargs), timeout + 1)
        except Exception as e:
            if ignore_timeout and 'timeout' in str(e).lower():
                return None
            show_error_log('retry_goto', e)
            if retry_times <= n - 1:
                raise e
        time.sleep(interval)


async def get_cookie(page, cookie_name):
    for item in await page.cookies():
        if item.get('name') == cookie_name:
            return item.get('value')


async def set_cookies(page, cookies: [dict]):
    for item in cookies:
        await page.setCookie(item)


async def clear_cookies(page):
    cookies = await page.cookies()
    for i in cookies:
        await page.deleteCookie(i)


async def get_all_cookies(page):
    res = await page._client.send('Network.getAllCookies')
    cookies = res.get('cookies', [])
    return [cut_dict(i, ["name", "value", "domain", "path"]) for i in cookies]


async def get_localstorage(page):
    command = """() => {
        let json = {};
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          json[key] = localStorage.getItem(key);
        }
        return json;
      }"""
    res = await page.evaluate(command)
    return res


async def clear_localstorage(page):
    await page.evaluate("localStorage.clear()")


async def scroll_to_bottom(page):
    await page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')


async def scroll_to_top(page):
    await page.evaluate('window.scrollTo(0, 0)')


async def set_localstorage(page, dic: dict):
    for k, v in dic.items():
        command = f"localStorage.setItem('{k}', '{v}')"
        await page.evaluate(command)


async def open_new_page(browser):
    page = await browser.newPage()
    await _format_page(page, **browser.__getattribute__('params'))  # 自定义
    return page


async def screen_shot(page, file_name='screen_shot.png', full_page=True):
    tmp_dir = get_tmp_dir()
    options = dict(path=os.path.join(tmp_dir, file_name), fullPage=full_page)
    await page.screenshot(options=options)


async def handle_dialog(dialog):
    await asyncio.sleep(1)
    await dialog.dismiss()


async def clear_input(page, ele):
    await ele.hover()
    await ele.focus()
    await ele.click()
    await asyncio.sleep(0.3)
    await page.keyboard.down('Control')
    await page.keyboard.press('KeyA')
    await page.keyboard.up('Control')
    await page.keyboard.press('Backspace')
    await asyncio.sleep(0.3)


async def click_and_wait_nav(page, ele, timeout=60):
    try:
        await asyncio.gather(
            ele.click(),
            page.waitForNavigation(
                options={'timeout': timeout * 1000, 'waitUntil': ['domcontentloaded', 'networkidle2']}),
        )
    except:
        print_error_info(log=True)


async def _format_page(page, **kwargs):
    user_agent = kwargs.get('user_agent')
    user_agent and await page.setUserAgent(user_agent)

    extra_headers = kwargs.get('extra_headers')
    img = kwargs.get('img')

    if kwargs.get('steal'):
        await stealth(page)
    if not img:
        client = page._networkManager._client
        client.send('Network.setRequestInterception', {'patterns': [{'urlPattern': '*'}]})
        await img_intercept(page)

    if extra_headers:
        await page.setExtraHTTPHeaders(extra_headers)

    page.on('dialog', lambda dialog: asyncio.ensure_future(handle_dialog(dialog)))


async def init_pyppeteer(gpu=True, auto_close=True, img=True, extra_headers=None, proxy=None, steal=False,
                         execute_path=None, max_window=False, window_size=(1920, 1080), user_data_dir=None,
                         devtools=False, in_thread=False, user_agent=None, chrome_params=None):
    local_var = locals()
    params_keys = inspect.signature(init_pyppeteer).parameters.keys()
    params = {i: local_var.get(i) for i in params_keys}

    browser_args = [
        '--no-default-browser-check',  # 默认浏览器检测
        # '--no-sandbox',
        # f'--load-extension={extensions4}', # extensions4 = os.path.join(get_tmp_dir(), 'chrome_extension/fingerprint_spoofing')
    ]
    if chrome_params and isinstance(chrome_params, list):
        browser_args += chrome_params

    if proxy:
        browser_args.append(f"--proxy-server=http://{proxy}")
    if max_window:
        browser_args.append('--start-maximized')
    else:
        browser_args.append(f"--window-size={window_size[0]},{window_size[1]}")

    if platform.system() != 'Windows':
        auto_close = True

    launch_params = dict(
        headless=not gpu,
        autoClose=auto_close,
        defaultViewport={'width': window_size[0] - 20, 'height': window_size[1] - 100},
        ignoreDefaultArgs=['--enable-automation', '--disable-extensions'],
        args=browser_args,
        devtools=devtools,
    )
    if user_data_dir:
        # user_data_dir = r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data'
        launch_params.update(dict(userDataDir=user_data_dir))

    if in_thread:
        launch_params.update({"handleSIGINT": False, "handleSIGTERM": False, "handleSIGHUP": False})

    if execute_path:
        launch_params.update(executablePath=execute_path)

    browser = await launch(**launch_params)
    page = (await browser.pages())[-1]

    await _format_page(page, **params)
    browser.params = params
    return browser, page


def bezier_curve(points, t):  # 计算给定控制点和时间参数的贝塞尔曲线点。
    n = len(points) - 1
    x = y = 0.0
    for i, (px, py) in enumerate(points):
        binomial = np.math.factorial(n) / (np.math.factorial(i) * np.math.factorial(n - i))
        factor = binomial * (t ** i) * ((1 - t) ** (n - i))
        x += px * factor
        y += py * factor
    return x, y


def move_mouse_via_curve(start, end, num_points=60):  # 模拟鼠标经过贝塞尔曲线路径的移动。
    mid_points = [(random.randint(min(start[0], end[0]), max(start[0], end[0])),
                   random.randint(min(start[1], end[1]), max(start[1], end[1]))) for _ in range(3)]  # 创建三个控制点增加曲线复杂度
    control_points = [start] + mid_points + [end]
    curve_points = [bezier_curve(control_points, i / num_points) for i in range(num_points + 1)]
    return [[x + random.uniform(-0.5, 0.5), y + random.uniform(-0.5, 0.5)] for (x, y) in curve_points]


async def simulate_move_mouse(page, x=65, y=300):
    li = move_mouse_via_curve([100, 100], [x, y])
    for _x, _y in li:
        show_log(_x, _y)
        await page.mouse.move(_x, _y)

        await asyncio.sleep(0.05)


async def abort_(client, interceptionId):
    await respond_(client, interceptionId, {'body': 'Sorry, Only a Big Cat', 'headers': {}, 'status': 200})


async def continue_(client, interceptionId):
    try:
        await client.send("Network.continueInterceptedRequest", {'interceptionId': interceptionId})
    except Exception as e:
        if not "Invalid InterceptionId" in str(e):
            show_log('continue_ error', e)


async def respond_(client, interceptionId, response: dict):
    if response.get('body') and isinstance(response['body'], str):
        responseBody: Optional[bytes] = response['body'].encode('utf-8')
    else:
        responseBody = response.get('body')

    responseHeaders = {}
    if response.get('headers'):
        for header in response['headers']:
            responseHeaders[header.lower()] = response['headers'][header]
    if response.get('contentType'):
        responseHeaders['content-type'] = response['contentType']
    if responseBody and 'content-length' not in responseHeaders:
        responseHeaders['content-length'] = len(responseBody)

    statusCode = response.get('status', 200)
    statusText = statusTexts.get(statusCode, '')
    statusLine = f'HTTP/1.1 {statusCode} {statusText}'

    CRLF = '\r\n'
    text = statusLine + CRLF
    for header in responseHeaders:
        text = f'{text}{header}: {responseHeaders[header]}{CRLF}'
    text = text + CRLF
    responseBuffer = text.encode('utf-8')
    if responseBody:
        responseBuffer = responseBuffer + responseBody

    rawResponse = base64.b64encode(responseBuffer).decode('ascii')
    try:
        await client.send('Network.continueInterceptedRequest',
                          {'interceptionId': interceptionId, 'rawResponse': rawResponse, })
    except Exception as e:
        show_log('response error', e)


async def img_intercept(page):
    client = page._networkManager._client

    async def intercept(event) -> None:
        interception_id = event["interceptionId"]
        url = event["request"]['url']
        if event['resourceType'] == 'Image' and re.search('\.(png|jgp|svg|bmp|gif|jpeg|ico)(\?|$)', url):
            await abort_(client, interception_id)
        await continue_(client, interception_id)

    client.on("Network.requestIntercepted", lambda event: client._loop.create_task(intercept(event)))


# 截获响应实例
async def img_intercept_demo(page):
    client = page._networkManager._client
    client.send('Network.setRequestInterception', {'patterns': [{'urlPattern': '*'}]})

    async def intercept(event) -> None:
        request = event["request"]
        interceptionId = event["interceptionId"]
        _headers = {k.lower(): v for k, v in request.get('headers', {}).items()}
        if "https://i.waimai.meituan.com/openh5/search/globalpage" in request['url'] and request['method'] == 'POST':
            res = requests.post(url=request['url'], data=request['postData'], headers=_headers)
            print(res.text)
            await respond_(client, interceptionId, {
                'body': res.content,
                'headers': res.headers,
                'status': res.status_code,
                'contentType': 'application/json',
            })
        await continue_(client, interceptionId)

    client.on("Network.requestIntercepted", lambda event: client._loop.create_task(intercept(event)))


async def chrome_request(page, url, method='GET', data=None, headers=None, retry_times=3):
    for retry_time in range(retry_times):
        params = {"method": method.upper(), "credentials": 'include', 'headers': {}}
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
            params['headers'].update({'content-type': 'application/json'})

        if data:
            params.update({'body': data})
        if headers:
            params['headers'].update(headers)

        params = json.dumps(params)
        js_str = """
            async function Foo(){
                let response = await fetch("%s", %s)
                content = await response.text()
                return {content: content, status: response.status}
            }
            """ % (url, params)

        resp = await page.evaluate(js_str)
        return resp


async def intercept_response(res):
    # page.on('response', lambda response: asyncio.ensure_future(intercept_response(response)))
    resourceType = res.request.resourceType
    show_log(res.request.url)
    if resourceType in ['xhr', 'fetch']:
        resp = await res.text()
        show_log(resp)


async def conn_exits_browser_demo(browserURL='http://127.0.0.1:9222'):
    from pyppeteer import connect
    browser = await connect(browserURL=browserURL)
    page = await browser.newPage()
    return browser, page


async def arrow_test(page):
    # await retry_goto(page, "https://www.arrow.com/")
    await retry_goto(page, "https://www.icgoo.net")
    await asyncio.sleep(1)
    error_count = 0
    for part_num in get_tmp_json('ti.json')['data']:
        # url = f'https://www.arrow.com/en/products/search?q={part_num}'
        url = f'https://www.icgoo.net/search/{quote(part_num, safe="")}/1'
        show_log('url', url)
        await retry_goto(page, url)
        content = await page.content()
        if 'Access Denied' in content:
            show_log('Access Denied')
            error_count += 1
            if error_count > 2:
                break
        else:
            show_log('pass')


async def init_browser():
    execute_path = r"d:\src\chromium\src\out\Default\chrome.exe"
    # execute_path = r"C:\Users\Administrator\Desktop\chrome.packed-v1.0.3\chrome\Chrome-bin\chrome.exe"
    browser, page = await init_pyppeteer(gpu=True, auto_close=True, execute_path=execute_path,
                                         user_data_dir=rf"d:/user_data_dir/{get_random_str(32)}",
                                         window_size=[1280, 960],
                                         chrome_params=[
                                             '--fingerprints=1299921',
                                             '--timezone=Asia/Hong_Kong',
                                             '--lang=zh-CN',
                                             # '--timezone=America/Los_Angeles',
                                             # '--ignores="useragent"',
                                             # '--disable-site-isolation-trials'
                                             # '--disable-web-security'
                                         ]
                                         )

    # url = "https://www.wilko.com/"
    # url = "https://www.browserscan.net"
    url = "https://wizzair.com/en-gb/booking/select-flight/TIA/CRL/2024-09-14/null/1/0/0/null"

    await retry_goto(page, url, timeout=9999)

    await asyncio.sleep(99999)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(init_browser())
