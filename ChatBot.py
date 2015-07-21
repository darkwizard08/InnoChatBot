# coding=utf-8

__author__ = 'darkwizard'
from threading import Thread
import time
import json

import grab


class ChatBot:
    def __init__(self):
        self.API_ADDR = "https://api.telegram.org/bot68323259:AAHnTI_xn2axEe_gi2Cl6ptoUSG77fXbGhk/"
        self.commands = ["/start", "/add_link", "/get_links"]
        self.conn = grab.Grab()
        self.msg_pool = list()
        self.t_load = Thread(target=self.load_messages)
        self.t_req = Thread(target=self.process_links)
        self.msg_offset = 0
        self.chat_id = -1
        self.links = []

    def start(self):
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
                # print "new offset is: ", self.msg_offset

    def send_message(self, message):
        self.conn.setup(post={'chat_id': self.chat_id,
                              'text': message,
                              'disable_web_page_preview': 'true'}
                        )
        return self.conn.go(self.API_ADDR + "sendMessage")

    def process_links(self):
        while True:
            if len(self.msg_pool) > 0:
                last = self.msg_pool[0]
                self.msg_pool = self.msg_pool[1:]
                message = last[u"message"]
                self.chat_id = message[u"chat"][u"id"]
                if u"left_chat_participant" in message:
                    self.send_message(u"Хорошего дня вдали от чатов!")
                elif u"new_chat_participant" in message:
                    self.send_message(u"Добро пожаловать в чат! Нажмите /chats , чтобы получить список диалогов")
                # print last
            else:
                time.sleep(0.4)


if __name__ == "__main__":
    bot = ChatBot()
    bot.start()