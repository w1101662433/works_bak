from libs.print_error_info import *
from libs.trans import trans_to_json
import tornado.web
import tornado.ioloop
from threading import Thread
from libs.save_mysql import save_to_json_record, save_suggest


class EchoHandler(tornado.web.RequestHandler):
    def post(self):
        post_data = self.request.arguments
        post_data = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
        if not post_data:
            post_data = self.request.body.decode('utf-8')
            post_data = json.loads(post_data)
        show_log('收到请求/echo', post_data)
        self.write(post_data)


class TransHandler(tornado.web.RequestHandler):
    def post(self):
        post_data = self.request.arguments
        post_data = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
        if not post_data:
            post_data = self.request.body.decode('utf-8')
            post_data = json.loads(post_data)
        show_log('收到请求/trans_to_json', post_data.get('content')[:100])
        content = post_data.get('content')

        t = Thread(target=save_to_json_record, args=(content,))
        t.start()

        if len(content) > 99999:
            self.write({'success': '/｀ｍ´）ﾉ ~┻━┻\n数据太长我处理不了啦'})
        else:
            res = trans_to_json(content)
            self.write({'success': res})


class SuggestHandler(tornado.web.RequestHandler):
    def post(self):
        post_data = self.request.arguments
        post_data = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
        if not post_data:
            post_data = self.request.body.decode('utf-8')
            post_data = json.loads(post_data)
        show_log('收到请求/send_suggest', str(post_data)[:100])
        name = post_data.get('name')
        description = post_data.get('description')

        t = Thread(target=save_suggest, args=(name, description))
        t.start()
        self.write({'success': 'success'})


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        show_log('收到请求 /')
        self.render('index.html')


class HtmlHandler(tornado.web.RequestHandler):
    def get(self, uri):
        # uri = self.request.uri
        show_log('收到请求', uri)
        self.render(uri)


class BaiduUnionHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('ce2c259bd1f24c765565269baf829b50')


def make_app():
    this_path = os.path.dirname(__file__)
    static_path = os.path.join(this_path, "static")
    template_path = os.path.join(this_path, "templates")

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/trans_to_json", TransHandler),
        (r"/send_suggest", SuggestHandler),
        (r"/echo", EchoHandler),
        (r"/(.*\.html)", HtmlHandler),
        (r"/bdunion.txt", BaiduUnionHandler),
        # 优化文件路径（不用在url打那么多），设置默认值为index
    ], static_path=static_path, template_path=template_path,  # 配置模板路径
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
