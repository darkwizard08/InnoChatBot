__author__ = 'darkwizard'
import grab
from threading import Thread
import time
import json


class ChatBot:
    def __init__(self):
        self.API_ADDR = "https://api.telegram.org/bot68323259:AAHnTI_xn2axEe_gi2Cl6ptoUSG77fXbGhk/"
        self.hello = u'\u041f\u0440\u0438\u0432\u0435\u0442. \u042f \u043d\u0430\u0447\u0430\u043b \u0440\u0430\u0431\u043e\u0442\u0443.'
        self.not_implemented = "Not yet implemented"
        self.commands = ["/start", "/add_link", "/get_links"]
        self.conn = grab.Grab()
        self.msg_pool = list()
        self.t_load = Thread(target=self.loadMessages)
        self.t_req = Thread(target=self.processLinks)
        self.msg_offset = 0
        self.chat_id = -1

    def start(self):
        self.t_load.start()
        self.t_req.start()

    def loadMessages(self):
        while True:
            time.sleep(0.7)
            self.conn.setup(post={'offset': self.msg_offset})
            data = self.conn.go(self.API_ADDR + "getUpdates").unicode_body()
            parsed = json.loads(data)
            self.msg_pool = parsed["result"]
            total = len(parsed["result"])
            if total != 0:
                self.msg_offset = self.msg_pool[total - 1]["update_id"] + 1
                print "new offset is: ", self.msg_offset

    def processLinks(self):
        while True:
            if len(self.msg_pool) > 0:
                last = self.msg_pool[0]
                self.msg_pool = self.msg_pool[1:]
                message = last[u"message"]
                self.chat_id = last[u"message"][u"chat"][u"id"]

                text = message[u"text"].split(" ")
                if text[0] == self.commands[0]:
                    self.conn.setup(post={'chat_id': self.chat_id, 'text': self.hello})
                    resp = self.conn.go(self.API_ADDR + "sendMessage")
                    print resp.unicode_body()

                elif text[0] == self.commands[1] or text[0] == self.commands[2]:
                    self.conn.setup(post={'chat_id': self.chat_id, 'text': self.not_implemented})
                    resp = self.conn.go(self.API_ADDR + "sendMessage")
                    print resp.unicode_body()
            else:
                time.sleep(0.4)


if __name__ == "__main__":
    bot = ChatBot()
    bot.start()