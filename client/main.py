#!/usr/bin/python3

import sys
import signal
import errno
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from sujeongku import sujeongku

from ui.window_main import Ui_window_main
from ui.dialog_highscore import Ui_dialog_highscore



class dialog_highscore(QDialog, Ui_dialog_highscore):

    def __init__(self, parent=None):
        super(dialog_highscore, self).__init__(parent)
        self.ui = Ui_dialog_highscore()
        self.ui.setupUi(self)

    def accept(self):
        super(dialog_highscore, self).accept()

    def reject(self):
        super(dialog_highscore, self).reject()



class window_main(QMainWindow, Ui_window_main):

    def __init__(self, parent=None):
        super(window_main, self).__init__(parent)
        self.sujeongku = sujeongku(self)
        self.setupUi(self)
        self.setup_connect()
        self.__exit = False

    def __close(self):
        self.__exit = True
        self.sujeongku.exit()

    def closeTerminal(self, *args):
        self.close()

    def closeEvent(self, event):
        self.__close()
        super(window_main, self).closeEvent(event)

    def close(self):
        self.__close()
        super(window_main, self).close()

    def setup_connect(self):
        self.button_login.clicked.connect(self.button_login_click)
        self.button_refresh.clicked.connect(self.button_refresh_click)
        self.button_join.clicked.connect(self.button_join_click)
        self.button_spectate.clicked.connect(self.button_spectate_click)
        self.button_create.clicked.connect(self.button_create_click)
        self.button_send.clicked.connect(self.button_send_click)
        self.button_highscore.clicked.connect(self.button_highscore_click)
        self.button_exit.clicked.connect(self.close)
        for i in range(self.sujeongku.row_size):
            for j in range(self.sujeongku.column_size):
                self.__dict__["button_" + str(i) + "_" + str(j)].clicked.connect(self.button_symbol_click)

    def button_symbol_click(self):
        button_name = self.sender().objectName().split('_')
        r, c = int(button_name[1]), int(button_name[2])
        print(r, c)
        if self.sujeongku.logged_in and self.sujeongku.id == self.sujeongku.turn and self.sujeongku.board[r][c] < 0:
            print("move", r, c)
            self.sujeongku.move(r, c)

    def button_login_click(self):
        self.nickname = self.text_nickname.text()
        if len(self.nickname) > 0 and not self.sujeongku.logged_in:
            self.sujeongku.login(self.nickname)

            # TODO: remove stub
            self.on_login_success()

    def button_refresh_click(self):
        self.sujeongku.refresh()

        # TODO: remove stub
        self.on_refresh_room([{"name":"wkwk", "id":1}, {"name":"hehe", "id":2}])

    def button_join_click(self):
        idx = self.list_room.currentIndex()
        if idx == -1:
            QMessageBox.critical(self, "Error", "Select a room first")
            return
        if idx >= 0 and idx < len(self.sujeongku.rooms):
            room = self.sujeongku.rooms[idx]
            if "id" in room:
                self.sujeongku.join(room["id"])

                # TODO: remove stub
                self.on_join_success(room["id"])

    def button_send_click(self):
        message = self.text_message.text().trim()
        if len(message) > 0:
            self.sujeongku.chat(message)
        self.text_message.setText("")

    def button_spectate_click(self):
        idx = self.list_room.currentIndex()
        if idx == -1:
            QMessageBox.critical(self, "Error", "Select a room first")
            return
        if idx >= 0 and idx < len(self.sujeongku.rooms):
            if "id" in self.sujeongku.rooms[idx]:
                self.sujeongku.spectate(self.sujeongku.rooms[idx]["id"])

                # TODO: remove stub
                self.on_spectate_success(self.sujeongku.rooms[idx]["id"])

    def button_create_click(self):
        name = self.text_create.text()
        if len(name) > 0:
            self.sujeongku.create(name)

            # TODO: remove stub
            self.on_create_success()

    def button_highscore_click(self):
        dialog = dialog_highscore(self)
        dialog.exec_()

    def check_connection(self):
        if not self.__exit and not self.sujeongku.connected():
            QMessageBox.critical(self, "Error", "Disconnected from server")
            self.close()


    # methods to handle sujeongku receiver

    def on_login_success(self):
        self.label_nickname.setEnabled(False)
        self.text_nickname.setEnabled(False)
        self.button_login.setEnabled(False)

        self.label_room_list.setEnabled(True)
        self.button_refresh.setEnabled(True)
        self.list_room.setEnabled(True)
        self.button_spectate.setEnabled(True)
        self.button_join.setEnabled(True)
        self.label_room_create.setEnabled(True)
        self.text_room.setEnabled(True)
        self.button_create.setEnabled(True)

    def on_login_fail(self):
        QMessageBox.critical(self, "Error", "Failed to login")

    def on_refresh_room(self):
        self.list_room.clear()
        for room in self.sujeongku.rooms:
            if "name" in room:
                self.list_room.addItem(room["name"])

    def on_join_success(self):
        self.label_room_list.setEnabled(False)
        self.button_refresh.setEnabled(False)
        self.list_room.setEnabled(False)
        self.button_spectate.setEnabled(False)
        self.button_join.setEnabled(False)
        self.label_room_create.setEnabled(False)
        self.text_room.setEnabled(False)
        self.button_create.setEnabled(False)

        self.label_chat.setEnabled(True)
        self.text_chat.setEnabled(True)
        self.text_message.setEnabled(True)
        self.button_send.setEnabled(True)

    def on_join_fail(self):
        QMessageBox.critical(self, "Error", "Failed to join the room")

    def on_spectate_success(self):
        pass

    def on_spectate_fail(self):
        QMessageBox.critical("Failed to spectate the room")

    def on_create_success(self):
        pass

    def on_create_fail(self):
        pass

    def on_chat(self, sender, content):
        self.text_chat.appendPlainText("%s: %s" % (sender["name"], content))

    def on_refresh_player(self):
        pass

    def on_refresh_spectator(self):
        pass

    def on_refresh_board(self):
        # check status of the board
        # a player has been disconnected
        if self.sujeongku.status < 0:
            pass
        # still playing
        elif self.sujeongku.status == 0:
            pass
        # someone has win
        else:
            pass

        symbol = {}
        idx = 0
        for player in self.sujeongku.players:
            id = player["id"]
            if id == self.sujeongku.id:
                symbol[id] = 'O'
            else:
                symbol[id] = chr(ord('A')+idx)
                idx = idx + 1

        for i in range(self.sujeongku.column_size):
            for j in range(self.sujeongku.row_size):
                button = self.__dict__["button_" + str(i) + "_" + str(j)]
                id = self.sujeongku.boards[i][j]
                if id < 0:
                    button.setEnabled(True)
                    button.setText("")
                else:
                    button.setEnabled(False)
                    button.setText(symbol[id])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = window_main()
    timer = QTimer()
    timer.timeout.connect(window.check_connection)
    timer.start(1000)
    signal.signal(signal.SIGINT, window.closeTerminal)
    window.show()
    sys.exit(app.exec_())
