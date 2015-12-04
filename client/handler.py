from PyQt5 import QtCore

import json

from . import connection
from common import protocol
from common import sujeongku

class handler(QtCore.QObject):

    on_login_success = QtCore.pyqtSignal()
    on_login_fail = QtCore.pyqtSignal()
    on_logout_success = QtCore.pyqtSignal()
    on_logout_fail = QtCore.pyqtSignal()
    on_refresh_room = QtCore.pyqtSignal()
    on_join_success = QtCore.pyqtSignal()
    on_join_fail = QtCore.pyqtSignal()
    on_spectate_success = QtCore.pyqtSignal()
    on_spectate_fail = QtCore.pyqtSignal()
    on_create_success = QtCore.pyqtSignal()
    on_create_fail = QtCore.pyqtSignal()
    on_leave_success = QtCore.pyqtSignal()
    on_leave_fail = QtCore.pyqtSignal()
    on_refresh_board = QtCore.pyqtSignal()
    on_refresh_player = QtCore.pyqtSignal()
    on_refresh_spectator = QtCore.pyqtSignal()
    on_chat = QtCore.pyqtSignal(dict, str)
    on_highscore = QtCore.pyqtSignal(list)

    def __init__(self, conn):
        super(handler, self).__init__()
        self.__conn = conn

        self.game = sujeongku.game()
        self.players = list()
        self.symbols = dict()

        self.id = protocol.INVALID_ID
        self.rooms = list()
        self.rooms_idx = list()
        self.playing = False
        self.room_name = ""
        self.on_room = False
        self.highscore = list()

        self.__symbol_list = "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ"
        self.__symbol_self = "☢"

        self.__keep_running = True

    def handle(self):
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

                msg_list = msg_recv.split(protocol.PROTO_END)
                for msg in msg_list:
                    if not msg:
                        continue
                    self.recv(json.loads(msg))

            except ValueError:
                pass


    def recv(self, message):
        if protocol.ACTION not in message:
            return

        action = message[protocol.ACTION]
        recv_action = getattr(self, "recv_" + action, None)
        if callable(recv_action):
            recv_action(message)
        else:
            print("Action not implemented:", action)


    def recv_login(self, message):
        if protocol.PROP_STATUS not in message:
            return

        status = message[protocol.PROP_STATUS]
        if status > 0 and protocol.PROP_ID in message:
            self.id = int(message[protocol.PROP_ID])
            self.on_login_success.emit()
        else:
            self.on_login_fail.emit()


    def recv_logout(self, message):
        if protocol.PROP_STATUS not in message:
            return

        status = message[protocol.PROP_STATUS]
        if status > 0:
            self.id = protocol.INVALID_ID
            self.on_logout_success.emit()
        else:
            self.on_logout_fail.emit()


    def recv_room_list(self, message):
        if protocol.PROP_ROOMS not in message:
            return

        self.rooms = message[protocol.PROP_ROOMS]
        self.rooms_id = list(self.rooms.keys())
        self.on_refresh_room.emit()


    def recv_join(self, message):
        if protocol.PROP_STATUS not in message:
            return

        status = message[protocol.PROP_STATUS]
        if status > 0:
            self.playing = True
            self.on_room = True
            self.on_join_success.emit()
        else:
            self.playing = False
            self.on_join_fail.emit()


    def recv_spectate(self, message):
        if protocol.PROP_STATUS not in message:
            return

        status = message[protocol.PROP_STATUS]
        if status > 0:
            self.on_room = True
            self.playing = False
            self.on_spectate_success.emit()
        else:
            self.playing = False
            self.on_spectate_fail.emit()


    def recv_create(self, message):
        if protocol.PROP_STATUS not in message:
            return

        status = message[protocol.PROP_STATUS]
        if status > 0:
            self.on_room = True
            self.playing = True
            self.on_create_success.emit()
        else:
            self.playing = False
            self.on_create_fail.emit()


    def recv_leave(self, message):
        if protocol.PROP_STATUS not in message:
            return

        status = message[protocol.PROP_STATUS]
        if status > 0:
            self.on_room = False
            self.playing = False
            self.on_leave_success.emit()
        else:
            self.on_leave_fail.emit()


    def recv_chat(self, message):
        if  protocol.PROP_SENDER not in message or \
            protocol.PROP_CONTENT not in message:
            return

        sender = message[protocol.PROP_SENDER]
        content = message[protocol.PROP_CONTENT]
        self.on_chat.emit(sender, content)


    def recv_game(self, message):
        if  protocol.PROP_STATUS not in message or \
            protocol.PROP_TURN not in message or \
            protocol.PROP_BOARD not in message:
            return

        if protocol.PROP_WINNING_ROWS in message:
            self.game.winning_rows = message[protocol.PROP_WINNING_ROWS]
        if protocol.PROP_WINNING_COLUMNS in message:
            self.game.winning_columns = message[protocol.PROP_WINNING_COLUMNS]
        self.game.status = message[protocol.PROP_STATUS]
        self.game.turn = message[protocol.PROP_TURN]
        self.game.board = message[protocol.PROP_BOARD]
        self.on_refresh_board.emit()


    def recv_highscore(self, message):
        if protocol.PROP_HIGHSCORE not in message:
            return

        self.on_highscore.emit(message[protocol.PROP_HIGHSCORE])


    def recv_player_list(self, message):
        if protocol.PROP_PLAYERS not in message:
            return

        self.players = message[protocol.PROP_PLAYERS]

        idx = 0
        for player in self.players:
            id = int(player[protocol.PROP_ID])
            if id == self.id:
                self.symbols[id] = self.__symbol_self
            else:
                self.symbols[id] = self.__symbol_list[idx]
                idx = (idx + 1) % len(self.__symbol_list)
        self.on_refresh_player.emit()


    def recv_spectator_list(self, message):
        if protocol.PROP_SPECTATORS not in message:
            return

        self.spectators = message[protocol.PROP_SPECTATORS]
        self.on_refresh_spectator.emit()
