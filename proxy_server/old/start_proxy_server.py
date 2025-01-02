import socket, select
import socks  # python3 -m pip install PySocks
from libs.print_error_info import *


class HttpRequestPacket(object):
    def __init__(self, data):
        self.__parse(data)

    def __parse(self, data):
        '''
        解析一个HTTP请求数据包
        GET http://test.wengcx.top/index.html HTTP/1.1\r\nHost: test.wengcx.top\r\nProxy-Connection: keep-alive\r\nCache-Control: max-age=0\r\n\r\n
        参数：data 原始数据
        '''
        i0 = data.find(b'\r\n')  # 请求行与请求头的分隔位置
        i1 = data.find(b'\r\n\r\n')  # 请求头与请求数据的分隔位置

        # 请求行 Request-Line
        self.req_line = data[:i0]
        self.method, self.req_uri, self.version = self.req_line.split()  # 请求行由method、request uri、version组成

        # 请求头域 Request Header Fields
        self.req_header = data[i0 + 2:i1]
        self.headers = {}
        for header in self.req_header.split(b'\r\n'):
            if not header:
                continue
            k, v = header.split(b': ')
            self.headers[k] = v
        self.host = self.headers.get(b'Host')

        # 请求数据
        self.req_data = data[i1 + 4:]


class SimpleHttpProxy(object):
    def __init__(self, host='0.0.0.0', port=10086, listen=1024, bufsize=4096, delay=1):
        # 初始化代理套接字，用于与客户端、服务端通信

        self.socket_proxy = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                     1)  # 将SO_REUSEADDR标记为True, 当socket关闭后，立刻回收该socket的端口
        self.socket_proxy.bind((host, port))
        self.socket_proxy.listen(listen)

        self.socket_recv_bufsize = bufsize * 1024
        self.delay = delay / 1000.0

        show_log('info', 'bind=%s:%s' % (host, port))
        show_log('info', 'listen=%s' % listen)
        show_log('info', 'bufsize=%skb, delay=%sms' % (bufsize, delay))

    def __del__(self):
        self.socket_proxy.close()

    def __connect(self, host, port):
        '''
        解析DNS得到套接字地址并与之建立连接
        参数：host 主机
        参数：port 端口
        返回：与目标主机建立连接的套接字
        '''
        # 解析DNS获取对应协议簇、socket类型、目标地址
        # getaddrinfo -> [(family, sockettype, proto, canonname, target_addr),]
        (family, sockettype, _, _, target_addr) = socket.getaddrinfo(host, port)[0]

        tmp_socket = socks.socksocket(family, sockettype)
        tmp_socket.setblocking(False)
        tmp_socket.settimeout(30)

        return tmp_socket

    def __proxy(self, socket_client):
        # 代理核心程序
        # 参数：socket_client 代理端与客户端之间建立的套接字
        # 接收客户端请求数据
        req_data = socket_client.recv(self.socket_recv_bufsize)

        if req_data == b'':
            return

        # 解析http请求数据
        http_packet = HttpRequestPacket(req_data)
        # source_ip = socket_client.getpeername()[0]
        # des_uri = http_packet.req_uri

        # 获取服务端host、port
        if not http_packet.host:
            http_packet.host = http_packet.req_uri

        try:
            show_log('__dict__.keys: ', http_packet.__dict__.keys())
            show_log('__dict__: ', http_packet.__dict__)
        except:
            show_log('obj has no __dict__')
        show_log('dir(): ', dir(http_packet))
        show_log('http_packet.req_header: ', http_packet.req_header)
        show_log('http_packet.req_line: ', http_packet.req_line)
        show_log('http_packet.headers: ', http_packet.headers)

        if b':' in http_packet.host:
            server_host, server_port = http_packet.req_uri.split(b':')
        else:
            server_host, server_port = http_packet.host, 80

        # 修正http请求数据
        tmp = b'%s//%s' % (http_packet.req_uri.split(b'//')[0], http_packet.host)
        req_data = req_data.replace(tmp, b'')

        # HTTP
        if http_packet.method in [b'GET', b'POST', b'PUT', b'DELETE', b'HEAD']:
            socket_server = self.__connect(server_host, server_port)  # 建立连接
            socket_server.send(req_data)  # 将客户端请求数据发给服务端

        # HTTPS，会先通过CONNECT方法建立TCP连接; CONNECT应该是代理特有的
        elif http_packet.method == b'CONNECT':

            socket_server = self.__connect(server_host, server_port)  # 建立连接
            success_msg = b'%s %d Connection Established\r\nConnection: close\r\n\r\n' % (http_packet.version, 200)
            show_log('success_msg', success_msg)
            socket_client.send(success_msg)  # 完成连接，通知客户端

            # 客户端得知连接建立，会将真实请求数据发送给代理服务端
            for i in range(2):
                req_data = socket_client.recv(self.socket_recv_bufsize)  # 接收客户端真实数据

                if req_data.strip():
                    break

            socket_server.send(req_data)  # 将客户端真实请求数据发给服务端

        # 使用select异步处理，不阻塞
        self.__nonblocking(socket_client, socket_server)

    def __nonblocking(self, socket_client, socket_server):

        '''
        使用select实现异步处理数据

        参数：socket_client 代理端与客户端之间建立的套接字
        参数：socket_server 代理端与服务端之间建立的套接字
        '''
        _rlist = [socket_client, socket_server]
        is_recv = True
        while is_recv:
            try:
                # rlist, wlist, elist = select.select(_rlist, _wlist, _elist, [timeout])
                # 参数1：当列表_rlist中的文件描述符fd状态为readable时，fd将被添加到rlist中
                # 参数2：当列表_wlist中存在文件描述符fd时，fd将被添加到wlist
                # 参数3：当列表_xlist中的文件描述符fd发生错误时，fd将被添加到elist
                # 参数4：超时时间timeout
                #  1) 当timeout==None时，select将一直阻塞，直到监听的文件描述符fd发生变化时返回
                #  2) 当timeout==0时，select不会阻塞，无论文件描述符fd是否有变化，都立刻返回
                #  3) 当timeout>0时，若文件描述符fd无变化，select将被阻塞timeout秒再返回

                rlist, _, elist = select.select(_rlist, [], [], 2)
                if elist:
                    show_log('elist', elist)
                    break
                for tmp_socket in rlist:
                    is_recv = True
                    # 接收数据
                    # show_log('tmp_socket', tmp_socket)
                    time.sleep(self.delay)
                    data = tmp_socket.recv(self.socket_recv_bufsize)
                    # if tmp_socket is socket_client:
                    #     show_log('socket_client data', data)
                    # elif tmp_socket is socket_server:
                    #     show_log('socket_server data', data)

                    if data == b'':
                        is_recv = False
                        continue

                    # socket_client状态为readable, 当前接收的数据来自客户端
                    if tmp_socket is socket_client:
                        socket_server.send(data)  # 将客户端请求数据发往服务端

                    # socket_server状态为readable, 当前接收的数据来自服务端
                    elif tmp_socket is socket_server:
                        socket_client.send(data)  # 将服务端响应数据发往客户端

                time.sleep(self.delay)  # 适当延迟以降低CPU占用
            except Exception as e:
                print_error_info(log=True)
                show_error_log(202, e)
                break

        socket_client.close()
        socket_server.close()

    def client_socket_accept(self):
        '''
        获取已经与代理端建立连接的客户端套接字，如无则阻塞，直到可以获取一个建立连接套接字
        返回：socket_client 代理端与客户端之间建立的套接字
        '''
        socket_client, _ = self.socket_proxy.accept()
        return socket_client

    def handle_client_request(self, socket_client):
        try:
            self.__proxy(socket_client)
        except Exception as e:
            for i in ['Connection refused', 'Connection closed unexpectedly', 'timed out', ]:
                if i in str(e):
                    show_error_log(222, e)
                    break
            else:
                print_error_info(log=True)

    def start(self):
        try:
            import _thread as thread  # py3
        except ImportError:
            import thread  # py2
        while True:
            try:
                # self.handle_client_request(self.client_socket_accept())
                thread.start_new_thread(self.handle_client_request, (self.client_socket_accept(),))
            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    # 参数：host 监听地址，默认0.0.0.0，代表本机任意ipv4地址
    # 参数：port 监听端口，10086
    # 参数：listen 监听客户端数量，默认10
    # 参数：bufsize 数据传输缓冲区大小，单位kb，默认16kb
    # 参数：delay 数据转发延迟，单位ms，默认1ms

    host, port, listen, bufsize, delay = '0.0.0.0', 10086, 10, 8, 1
    SimpleHttpProxy(host, port, listen, bufsize, delay).start()
