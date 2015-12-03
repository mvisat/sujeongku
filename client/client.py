import json

from common import protocol

class client:

    def __init__(self, conn):
        self.__conn = conn


    def send(self, message):
        message = json.dumps(message)
        self.__conn.send(message + protocol.PROTO_END)


    def login(self, nickname):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_LOGIN
        msg_send[protocol.PROP_NAME] = nickname
        self.send(msg_send)


    def refresh(self):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_ROOM_LIST
        self.send(msg_send)


    def join(self, room_id):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_JOIN
        msg_send[protocol.PROP_ROOM_ID] = room_id
        self.send(msg_send)


    def spectate(self, room_id):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_SPECTATE
        msg_send[protocol.PROP_ROOM_ID] = room_id
        self.send(msg_send)


    def leave(self):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_LEAVE
        self.send(msg_send)


    def create(self, name, size):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_CREATE
        msg_send[protocol.PROP_NAME] = name
        msg_send[protocol.PROP_SIZE] = size
        self.send(msg_send)


    def chat(self, content):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_CHAT
        msg_send[protocol.PROP_CONTENT] = content
        self.send(msg_send)


    def move(self, row, column):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_MOVE
        msg_send[protocol.PROP_ROW] = row
        msg_send[protocol.PROP_COLUMN] = column
        self.send(msg_send)


    def highscore(self):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_HIGHSCORE
        self.send(msg_send)


    def exit(self):
        msg_send = {}
        msg_send[protocol.ACTION] = protocol.ACTION_EXIT
        self.send(msg_send)
        self.__conn.close()
