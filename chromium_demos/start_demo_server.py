from flask import Flask, make_response, render_template
from flask import request, send_file

from libs.print_error_info import *
from io import BytesIO

import threading
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# 实例化产生一个Flask对象
app = Flask(__name__)


@app.route('/echo', methods=['GET', 'POST'])
def echo():
    if request.method == "GET":
        kw = request.args.get('kw')
        return request.args
    elif request.method == "POST":
        print(request.data.decode())
        print(request.headers)
        print(request.cookies)
    return {'ip': get_host_ip()}


@app.route('/', methods=['GET', 'POST'])
def index_():
    return render_template('111.html')

@app.route('/222.html', methods=['GET', 'POST'])
def index2_():
    return render_template('222.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
