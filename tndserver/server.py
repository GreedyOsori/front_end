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

class DummyClientHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dummy_client.html")

class StoneHandler(tornado.web.RequestHandler):
    def get(self):
        id = self.get_argument("id")
        params = dict()
        for k in self.request.arguments:
            if k != "id" :
                params[k] = int(self.get_argument(k))
        params["msg"] = "notice_stone"

        reqStone = json.dumps(params)

        print reqStone

        for client in clients:
            if client.id == id :
                client.write_message(reqStone)

class BoardHandler(tornado.web.RequestHandler):
    def get(self):
        id = self.get_argument("id")

        board = list()
        board.append( [int(i) for i in list(self.get_argument("line1"))] )
        board.append( [int(i) for i in list(self.get_argument("line2"))] )
        board.append( [int(i) for i in list(self.get_argument("line3"))] )
        board.append( [int(i) for i in list(self.get_argument("line4"))] )
        board.append( [int(i) for i in list(self.get_argument("line5"))] )
        board.append( [int(i) for i in list(self.get_argument("line6"))] )
        board.append( [int(i) for i in list(self.get_argument("line7"))] )
        board.append( [int(i) for i in list(self.get_argument("line8"))] )

        params = dict()
        params["msg"] = "notice_stone"
        params["board"] = board
        reqBoard = json.dumps(params)

        print reqBoard

        for client in clients:
            if client.id == id :
                client.write_message(reqBoard)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print "WebSocketHandler.open"
        self.stream.set_nodelay(True)

    def on_message(self, message):
        js = json.loads(message)
        if js['msg'] == 'request_user_list' :
            self.id = js['id']
            clients.append(self)

            # send adduser msg to existed clients
            dictAddUser = {'msg':'notice_user_added'}
            dictAddUser['id'] = js['id']
            msgAddUser = json.dumps(dictAddUser)
            for client in clients :
                if client != self :
                    client.write_message(msgAddUser)

            # send alluser msg to new client
            dictAllUser = {'msg':'response_user_list'}
            dictAllUser['num'] = len(clients)

            i = 0
            dictUserList = dict()
            for client in clients :
                dictUserList[i] = client.id
                i += 1
            dictAllUser['users'] = dictUserList

            msgAllUser = json.dumps(dictAllUser)
            self.write_message(msgAllUser)

        elif js['msg'] == 'request_match' :
            # temp response - response_match
            id1 = js['id1']
            id2 = js['id2']
            dictMatch = {'msg':'response_match', 'error':0, 'id1':id1, 'id2':id2}
            msgMatch = json.dumps(dictMatch)
            self.write_message(msgMatch)

    def on_close(self):
        print "WebSocketHandler.on_close"
        if self in clients:
            clients.remove(self)

            # send deluser msg to existed clients
            dictDelUser = {'msg': 'notice_user_removed'}
            dictDelUser['id'] = self.id
            msgDelUser = json.dumps(dictDelUser)
            for client in clients:
                client.write_message(msgDelUser)

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket', WebSocketHandler),
    (r'/dummy_client', DummyClientHandler),
    (r'/stone', StoneHandler),
    (r'/board', BoardHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()