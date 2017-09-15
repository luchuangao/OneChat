import uuid
import json
import tornado.ioloop
import tornado.web
import tornado.websocket


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class ChatHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    messages = []

    def open(self, *args, **kwargs):
        ChatHandler.waiters.add(self)
        uid = str(uuid.uuid4())
        self.write_message(uid)

        for msg in ChatHandler.messages:
            content = self.render_string('message.html',**msg)
            self.write_message(content)

    def on_message(self, message):
        msg = json.loads(message)
        ChatHandler.messages.append(msg)

        for client in ChatHandler.waiters:
            content = client.render_string('message.html', **msg)
            client.write_message(content)

    def on_close(self):
        ChatHandler.waiters.remove(self)


def run():
    settings = {
        'template_path': 'templates',
        'static_path': 'static',
    }
    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/chat", ChatHandler),
    ], **settings)
    application.listen(8888, '0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    run()