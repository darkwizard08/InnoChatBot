from entities.Entities import LinkEntity

__author__ = 'darkwizard'
from threading import Thread
import time
import json

import grab
from entities import Entities
from pony import orm


class ChatBot:
    def __init__(self):
        self.API_ADDR = "https://api.telegram.org/bot68323259:AAHnTI_xn2axEe_gi2Cl6ptoUSG77fXbGhk/"
        self.hello = u'\u041f\u0440\u0438\u0432\u0435\u0442. \u042f \u043d\u0430\u0447\u0430\u043b \u0440\u0430\u0431\u043e\u0442\u0443.'
        self.not_implemented = "Not yet implemented"
        self.commands = ["/start", "/add_link", "/get_links"]
        self.conn = grab.Grab()
        self.msg_pool = list()
        self.t_load = Thread(target=self.load_messages)
        self.t_req = Thread(target=self.process_links)
        self.msg_offset = 0
        self.chat_id = -1
        self.links = []
        self.db = Entities.db

    @orm.db_session
    def load_links(self):
        self.links = orm.select(p.name for p in LinkEntity)[:]
        print self.links

    def start(self):
        self.db.bind('sqlite', 'links_db.sqlite', create_db=True)
        self.db.generate_mapping(create_tables=True)
        self.load_links()
        self.t_load.start()
        self.t_req.start()

    def load_messages(self):
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

    def get_links_list(self):
        # generating list of links
        links_text = "Currently we have: "
        for link in self.links:
            links_text += "\n %s" % link

        return links_text

    def send_message(self, message):
        self.conn.setup(post={'chat_id': self.chat_id,
                              'text': message,
                              'disable_web_page_preview': 'true'}
                        )
        return self.conn.go(self.API_ADDR + "sendMessage")

    @orm.db_session
    def add_link(self, link_params):
        """link_params: list"""
        if len(link_params) < 3:
            self.send_message("Error! You need to send /add_link <http link> <description>")
            return
        new_link = link_params[1] + " - " + " ".join(link_params[2:])
        link_orm = LinkEntity(name=new_link)
        orm.commit()
        self.links.append(new_link)
        self.send_message("Link accepted")

    def process_links(self):
        while True:
            if len(self.msg_pool) > 0:
                last = self.msg_pool[0]
                self.msg_pool = self.msg_pool[1:]
                message = last[u"message"]
                print message
                self.chat_id = last[u"message"][u"chat"][u"id"]
                text = message[u"text"].split(" ")
                adressee = text[0]
                if "@" in adressee:
                    adressee = adressee.split("@")[0]

                if adressee == self.commands[0]:
                    self.send_message(self.hello)

                elif adressee == self.commands[1]:
                    self.add_link(text)

                elif adressee == self.commands[2]:
                    text = self.get_links_list()
                    self.send_message(text)
            else:
                time.sleep(0.4)


if __name__ == "__main__":
    bot = ChatBot()
    bot.start()