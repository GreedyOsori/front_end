import tornado.ioloop
import tornado.web
import tornado.websocket
import json

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in list..
clients = list()
#

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        #self.write("This is your response")
        self.render("index.html")
        #we don't need self.finish() because self.render() is fallowed by self.finish() inside tornado
        #self.finish()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print "WebSocketHandler.open"
        self.stream.set_nodelay(True)

    def on_message(self, message):
        js = json.loads(message)
        if js['msg'] == 'connect' :
            self.id = js['id']
            clients.append(self)

            # send adduser msg to existed clients
            dictAddUser = {'msg':'adduser'}
            dictAddUser['id'] = js['id']
            msgAddUser = json.dumps(dictAddUser)
            for client in clients :
                if client != self :
                    client.write_message(msgAddUser)

            # send alluser msg to new client
            dictAllUser = {'msg':'alluser'}
            dictAllUser['num'] = len(clients)

            i = 0
            dictUserList = dict()
            for client in clients :
                dictUserList[i] = client.id
                i += 1
            dictAllUser['users'] = dictUserList

            msgAllUser = json.dumps(dictAllUser)
            self.write_message(msgAllUser)

    def on_close(self):
        print "WebSocketHandler.on_close"
        if self in clients:
            clients.remove(self)

            # send deluser msg to existed clients
            dictDelUser = {'msg': 'deluser'}
            dictDelUser['id'] = self.id
            msgDelUser = json.dumps(dictDelUser)
            for client in clients:
                client.write_message(msgDelUser)

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()