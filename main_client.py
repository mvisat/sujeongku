#!/usr/bin/python3

import sys
import signal
import errno
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from common import protocol
from common import sujeongku
from client import connection
from client import handler
from client import client

from client.ui.window_main import Ui_window_main
from client.ui.dialog_highscore import Ui_dialog_highscore



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
        self.__conn = connection.connection()
        self.client = client.client(self.__conn)
        self.handler = handler.handler(self.__conn)
        self.thread = QThread()
        self.setupUi(self)
        self.setupConnect()
        self.__exit = False

    def __close(self):
        self.__exit = True
        self.client.exit()

    def closeTerminal(self, *args):
        self.close()

    def closeEvent(self, event):
        self.__close()
        super(window_main, self).closeEvent(event)

    def close(self):
        self.__close()
        super(window_main, self).close()

    def setupConnect(self):
        self.button_login.clicked.connect(self.button_login_click)
        self.button_refresh.clicked.connect(self.button_refresh_click)
        self.button_join.clicked.connect(self.button_join_click)
        self.button_spectate.clicked.connect(self.button_spectate_click)
        self.button_create.clicked.connect(self.button_create_click)
        self.button_send.clicked.connect(self.button_send_click)
        self.button_leave.clicked.connect(self.button_leave_click)
        self.button_about.clicked.connect(self.button_about_click)
        self.button_highscore.clicked.connect(self.button_highscore_click)
        for i in range(sujeongku.ROW_SIZE):
            for j in range(sujeongku.COLUMN_SIZE):
                button = self.__dict__["button_" + str(i) + "_" + str(j)]
                button.clicked.connect(self.button_symbol_click)

        self.text_nickname.returnPressed.connect(self.button_login.click)
        self.text_room.returnPressed.connect(self.button_create.click)
        self.text_message.returnPressed.connect(self.button_send.click)

        self.handler.moveToThread(self.thread)
        self.handler.on_login_success.connect(self.on_login_success)
        self.handler.on_login_fail.connect(self.on_login_fail)
        self.handler.on_refresh_room.connect(self.on_refresh_room)
        self.handler.on_join_success.connect(self.on_join_success)
        self.handler.on_join_fail.connect(self.on_join_fail)
        self.handler.on_spectate_success.connect(self.on_spectate_success)
        self.handler.on_spectate_fail.connect(self.on_spectate_fail)
        self.handler.on_create_success.connect(self.on_create_success)
        self.handler.on_create_fail.connect(self.on_create_fail)
        self.handler.on_leave_success.connect(self.on_leave_success)
        self.handler.on_leave_fail.connect(self.on_leave_fail)
        self.handler.on_refresh_board.connect(self.on_refresh_board)
        self.handler.on_refresh_player.connect(self.on_refresh_player)
        self.handler.on_refresh_spectator.connect(self.on_refresh_spectator)
        self.handler.on_chat.connect(self.on_chat)
        self.thread.started.connect(self.handler.handle)
        self.thread.start()


    def button_symbol_click(self):
        button_name = self.sender().objectName().split('_')
        r, c = int(button_name[1]), int(button_name[2])
        if self.handler.id > 0 and self.handler.id == self.handler.game.turn and self.handler.game.board[r][c] < 0:
            self.client.move(r, c)


    def button_login_click(self):
        self.nickname = self.text_nickname.text().strip()
        if len(self.nickname) > 0 and self.handler.id == protocol.INVALID_ID:
            self.client.login(self.nickname)
        else:
            self.text_nickname.setFocus()


    def button_refresh_click(self):
        self.client.refresh()


    def button_join_click(self):
        idx = self.list_room.currentIndex()
        if idx == -1:
            QMessageBox.critical(self, "Error", "Select a room first")
            return
        if idx >= 0 and idx < len(self.handler.rooms_id):
            room_id = self.handler.rooms_id[idx]
            name, size = self.handler.rooms[room_id]
            self.handler.room_name = name
            self.client.join(room_id)


    def button_send_click(self):
        message = self.text_message.text().strip()
        if len(message) > 0:
            self.client.chat(message)
        self.text_message.setText("")
        self.text_message.setFocus()


    def button_spectate_click(self):
        idx = self.list_room.currentIndex()
        if idx == -1:
            QMessageBox.critical(self, "Error", "Select a room first")
            return
        if idx >= 0 and idx < len(self.handler.rooms_id):
            room_id = self.handler.rooms_id[idx]
            name, size = self.handler.rooms[room_id]
            self.handler.room_name = name
            self.client.spectate(room_id)


    def button_create_click(self):
        name = self.text_room.text().strip()
        if len(name) > 0:
            self.handler.room_name = name
            size = self.spin_room_size.value()
            if sujeongku.MIN_ROOM_SIZE <= size <= sujeongku.MAX_ROOM_SIZE:
                self.client.create(name, size)
            else:
                QMessageBox.critical(self, "Error", "Invalid room size")
        else:
            self.text_room.setFocus()


    def button_leave_click(self):
        pass


    def button_about_click(self):
        pass


    def button_highscore_click(self):
        dialog = dialog_highscore(self)
        dialog.exec_()


    def check_connection(self):
        if not self.__exit and not self.__conn.connected:
            QMessageBox.critical(self, "Error", "Disconnected from server")
            self.close()


    def __on_outside(self):
        self.label_nickname.setEnabled(True)
        self.text_nickname.setEnabled(True)
        self.button_login.setEnabled(True)

        self.label_room_list.setEnabled(False)
        self.button_refresh.setEnabled(False)
        self.list_room.setEnabled(False)
        self.button_spectate.setEnabled(False)
        self.button_join.setEnabled(False)
        self.label_room_create.setEnabled(False)
        self.text_room.setEnabled(False)
        self.button_create.setEnabled(False)

        self.text_nickname.setFocus()

    def __on_lobby(self):
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
        self.label_room_size.setEnabled(True)
        self.spin_room_size.setEnabled(True)
        self.button_create.setEnabled(True)
        self.button_leave.setEnabled(False)

        self.label_player.setEnabled(False)
        self.list_player.setEnabled(False)

        self.label_spectator.setEnabled(False)
        self.list_spectator.setEnabled(False)

        self.label_chat.setEnabled(False)
        self.text_chat.setEnabled(False)
        self.text_message.setEnabled(False)
        self.button_send.setEnabled(False)

        for i in range(sujeongku.ROW_SIZE):
            for j in range(sujeongku.COLUMN_SIZE):
                button = self.__dict__["button_" + str(i) + "_" + str(j)]
                button.setText("")
                button.setEnabled(False)

        self.statusBar().showMessage("Annyeong, {name}".format(name=self.handler.nickname))
        self.button_refresh.click()
        self.text_room.setFocus()

    def __on_room(self):
        self.label_room_list.setEnabled(False)
        self.button_refresh.setEnabled(False)
        self.list_room.setEnabled(False)
        self.button_spectate.setEnabled(False)
        self.button_join.setEnabled(False)
        self.label_room_create.setEnabled(False)
        self.text_room.setEnabled(False)
        self.label_room_size.setEnabled(False)
        self.spin_room_size.setEnabled(False)
        self.button_create.setEnabled(False)
        self.button_leave.setEnabled(True)

        self.label_player.setEnabled(True)
        self.list_player.setEnabled(True)

        self.label_spectator.setEnabled(True)
        self.list_spectator.setEnabled(True)

        self.label_chat.setEnabled(True)
        self.text_chat.setEnabled(True)
        self.text_message.setEnabled(True)
        self.button_send.setEnabled(True)

        for i in range(sujeongku.ROW_SIZE):
            for j in range(sujeongku.COLUMN_SIZE):
                button = self.__dict__["button_" + str(i) + "_" + str(j)]
                button.setText("")
                button.setEnabled(False)

        self.statusBar().showMessage("Room " + self.handler.room_name + " | Waiting players to start...")
        self.text_message.setFocus()


    # methods to handle sujeongku receiver

    def on_login_success(self):
        self.__on_lobby()

    def on_login_fail(self):
        QMessageBox.critical(self, "Error", "Nickname already taken")

    def on_refresh_room(self):
        self.list_room.clear()
        for (name, size) in self.handler.rooms.values():
            self.list_room.addItem(name)

        enabled = len(self.handler.rooms) > 0
        self.list_room.setEnabled(enabled)
        self.button_join.setEnabled(enabled)
        self.button_spectate.setEnabled(enabled)

    def on_join_success(self):
        self.__on_room()

    def on_join_fail(self):
        QMessageBox.critical(self, "Error", "Failed to join the room")

    def on_spectate_success(self):
        self.__on_room()

    def on_spectate_fail(self):
        QMessageBox.critical(self, "Error", "Failed to spectate the room")

    def on_create_success(self):
        self.__on_room()

    def on_create_fail(self):
        QMessageBox.critical(self, "Error", "Failed to create the room")

    def on_leave_success(self):
        pass

    def on_leave_fail(self):
        pass

    def on_chat(self, sender, content):
        name = sender[protocol.PROP_NAME]
        if self.handler.id == int(sender[protocol.PROP_ID]):
            name = name + " (You)"
        self.text_chat.appendPlainText("{name}: {content}".format(name=name, content=content))

    def on_refresh_player(self):
        self.list_player.clear()
        for player in self.handler.players:
            id = int(player[protocol.PROP_ID])
            name = str(player[protocol.PROP_NAME])
            if id == self.handler.id:
                name = name + " (You)"
            self.list_player.addItem("{symbol} - {name}".format(symbol=self.handler.symbols[id], name=name))

    def on_refresh_spectator(self):
        self.list_spectator.clear()
        for player in self.handler.spectators:
            id = int(spectator[protocol.PROP_ID])
            name = str(spectator[protocol.PROP_NAME])
            if id == self.handler.id:
                name = name + " (You)"
            self.list_spectator.addItem(name)

    def on_refresh_board(self):

        for i in range(sujeongku.ROW_SIZE):
            for j in range(sujeongku.COLUMN_SIZE):
                button = self.__dict__["button_" + str(i) + "_" + str(j)]
                id = self.handler.game.board[i][j]
                if id < 0:
                    button.setEnabled(self.handler.game.turn == self.handler.id)
                    button.setText("")
                else:
                    button.setEnabled(False)
                    button.setText(self.handler.symbols[id])

        # a player has been disconnected
        if self.handler.game.status == -10:
            QMessageBox.warning(self, "Warning", "Someone has disconnected from this game")

        # still playing
        elif self.handler.game.status == sujeongku.STATUS_PLAYING:
            pass

        # draw
        elif self.handler.game.status == sujeongku.STATUS_DRAW:
            QMessageBox.information(self, "Draw!", "")

        # someone has win
        elif self.handler.game.status == sujeongku.STATUS_FINISHED:
            winner_name = ""
            for player in self.handler.players:
                if player[protocol.PROP_ID] == self.handler.game.turn:
                    winner_name = player[protocol.PROP_NAME]
                    break

            # disable the buttons
            for i in range(sujeongku.ROW_SIZE):
                for j in range(sujeongku.COLUMN_SIZE):
                    button = self.__dict__["button_" + str(i) + "_" + str(j)]
                    button.setEnabled(False)

            # colorize the winning symbol
            for i in range(len(self.handler.game.winning_rows)):
                r = self.handler.game.winning_rows[i]
                c = self.handler.game.winning_columns[i]
                button = self.__dict__["button_" + str(r) + "_" + str(c)]
                button.setStyleSheet("background-color: #FF4040; color: white")

            if self.handler.playing:
                if self.handler.game.turn == self.handler.id:
                    QMessageBox.information(self, "Win!", "Congrats! You win this game!")
                else:
                    QMessageBox.information(self, "Lose!", "Aw, player {winner} win this game :(".format(winner=winner_name))
            else:
                QMessageBox.information(self, "Finished!", "Player {winner} win this game!".format(winner=winner_name))
            return

        room_name = "Room " + self.handler.room_name
        if self.handler.playing:
            if self.handler.game.turn == self.handler.id:
                room_status = "Now it's your turn!"
            else:
                room_status = "Waiting other players to move..."
        else:
            room_status = "Spectating the game..."
        self.statusBar().showMessage("{room_name} | {room_status}".format(room_name=room_name, room_status=room_status))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = window_main()
    timer = QTimer()
    timer.timeout.connect(window.check_connection)
    timer.start(1000)
    signal.signal(signal.SIGINT, window.closeTerminal)
    window.show()
    sys.exit(app.exec_())
