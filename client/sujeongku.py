#!/usr/bin/python3

import json
import threading

from connection import connection



class sujeongku(object):

    def __init__(self, parent):
        super(sujeongku, self).__init__()
        self.parent = parent
        self.__conn = connection()

        self.row_size = 20
        self.column_size = 20
        self.turn = -1
        self.board = []

        self.id = -1
        self.nickname = ""
        self.logged_in = False
        self.rooms = []

        self.__keep_running = True

        self.reader = threading.Thread(target=self.__reader)
        self.reader.Daemon = True
        self.reader.start()

    def __reader(self):
        while self.__keep_running:
            try:
                msg_recv = self.__conn.recv()
                if len(msg_recv) == 0:
                    if self.__conn.ready_to_read:
                        self.__conn.close()
                        self.__keep_running = False
                        break
                    else:
                        continue
                print("received:", msg_recv)
                msg_recv = json.loads(msg_recv)

                if "action" not in msg_recv:
                    continue

                action = msg_recv["action"]
                if action == "login":
                    if "id" in msg_recv:
                        self.id = msg_recv["id"]
                        self.parent.on_login_success()
                    else:
                        self.parent.on_login_fail()

                elif action == "refresh":
                    if "rooms" in msg_recv:
                        self.rooms = msg_recv["rooms"]
                        self.parent.on_refresh_room(self)

                elif action == "join":
                    if "status" in msg_recv:
                        status = msg_recv["status"]
                        if status != 0:
                            self.parent.on_join_success()
                        else:
                            self.parent.on_join_fail()

                elif action == "spectate":
                    if "status" in msg_recv:
                        status = msg_recv["status"]
                        if status > 0:
                            self.parent.on_spectate_success()
                        else:
                            self.parent.on_spectate_fail()

                elif action == "create":
                    if "status" in msg_recv:
                        status = msg_recv["status"]
                        if status > 0:
                            self.parent.on_create_success()
                        else:
                            self.parent.on_create_fail()

                elif action == "chat":
                    if "sender" in msg_recv and "content" in msg_recv:
                        sender = msg_recv["sender"]
                        content = msg_recv["content"]
                        self.parent.on_chat(sender, content)

                elif action == "game":
                    if "status" in msg_recv and "turn" in msg_recv and "board" in msg_recv:
                        status = msg_recv["status"]
                        self.turn = msg_recv["turn"]
                        self.board = msg_recv["board"]
                        self.parent.on_refresh_board()

                elif action == "player_list":
                    if "players" in msg_recv:
                        self.players = msg_recv["players"]
                        self.players = sorted(self.players, key=lambda k: k["id"])
                        self.parent.on_refresh_player()

                elif action == "spectator_list":
                    if "spectators" in msg_recv:
                        self.spectators = msg_recv["spectators"]
                        self.parent.on_refresh_spectator()

            except ValueError as e:
                pass

    def connected(self):
        return self.__conn.connected

    def login(self, nickname):
        self.nickname = nickname
        msg_send = {}
        msg_send["action"] = "login"
        msg_send["nickname"] = self.nickname
        self.__conn.send(json.dumps(msg_send))

    def refresh(self):
        msg_send = {}
        msg_send["action"] = "refresh"
        self.__conn.send(json.dumps(msg_send))

    def join(self, room_id):
        msg_send = {}
        msg_send["action"] = "join"
        msg_send["id"] = self.id
        msg_send["room_id"] = room_id
        self.__conn.send(json.dumps(msg_send))

    def spectate(self, room_id):
        msg_send = {}
        msg_send["action"] = "spectate"
        msg_send["id"] = self.id
        msg_send["room_id"] = room_id
        self.__conn.send(json.dumps(msg_send))

    def leave(self):
        msg_send = {}
        msg_send["action"] = "leave"
        msg_send["id"] = self.id
        self.__conn.send(json.dumps(msg_send))

    def create(self, name, size):
        msg_send = {}
        msg_send["action"] = "create"
        msg_send["id"] = self.id
        msg_send["name"] = name
        msg_send["size"] = size
        self.__conn.send(json.dumps(msg_send))

    def chat(self, message):
        msg_send = {}
        msg_send["action"] = "chat"
        msg_send["id"] = self.id
        msg_send["content"] = content
        self.__conn.send(json.dumps(msg_send))

    def move(self, row, column):
        msg_send = {}
        msg_send["action"] = "move"
        msg_send["id"] = self.id
        msg_send["row"] = row
        msg_send["column"] = column
        self.__conn.send(json.dumps(msg_send))

    def exit(self):
        msg_send = {}
        msg_send["action"] = "exit"
        msg_send["id"] = self.id
        self.__conn.send(json.dumps(msg_send))
        self.__keep_running = False
        self.__conn.close()

