import threading
import select
import json

from common import protocol
from common import sujeongku

class handler():

    def __init__(self, server, socket, addr):
        self.server = server
        self.socket = socket
        self.addr = addr
        self.socket.setblocking(0)
        self.buf_size = 4096
        self.__verbose = True

        self.id = -1
        self.room_id = -1
        self.nickname = ""
        self.connected = True
        self.keep_running = True
        self.thread = threading.Thread(target=self.handle)
        self.thread.Daemon = True
        self.thread.start()


    def close(self):
        self.keep_running = False
        self.server.exit(self.id)
        self.broadcast_player_list(self.room_id)
        self.broadcast_spectator_list(self.room_id)
        self.broadcast_game(self.room_id)
        if self in self.server.handlers:
            self.server.handlers.remove(self)
        self.socket.close()


    def handle(self):
        while self.keep_running and self.server.keep_running:
            try:
                messages = list()
                while self.keep_running and self.server.keep_running:

                    # check socket if it is ready to read
                    socket_ready_to_read, _, _ = select.select([self.socket], [], [], 0.5)
                    if self.socket not in socket_ready_to_read:
                        continue

                    # receive the packet
                    message = self.socket.recv(self.buf_size).decode('utf-8')

                    # client is disconnected
                    if len(message) == 0:
                        self.__verbose and print("Client", str(self.addr) ,"disconnected, exiting...")
                        self.close()
                        return

                    self.__verbose and print("Received", len(message), "bytes:", message.strip())
                    messages.append(message)

                    # keep recv until PROTO_END is received
                    if message.endswith(protocol.PROTO_END):
                        break

                self.recv("".join(messages))

            except select.error:
                pass


    def recv(self, message):
        try:
            message = message.split(protocol.PROTO_END)
            for msg in message:
                if not msg:
                    continue

                # try to load as json, check if action is in message
                message = json.loads(msg)
                if protocol.ACTION not in message:
                    return

                # call responsible method
                action = message[protocol.ACTION]
                recv_action = getattr(self, "recv_" + action, None)
                if callable(recv_action):
                    recv_action(message)
                else:
                    self.__verbose and print("Not implemented action:", action)

        except ValueError:
            pass

        except KeyError:
            pass


    def send(self, message):
        if not self.keep_running:
            return

        message = json.dumps(message)
        self.__verbose and print("Sending", len(message), "bytes:", message)
        self.socket.sendall((message + protocol.PROTO_END).encode())


    def broadcast(self, room_id, message):
        message = json.dumps(message)
        self.__verbose and print("Broadcasting", len(message), "bytes:", message)
        message = (message + protocol.PROTO_END).encode()
        with self.server.handlers_lock:
            for handler in self.server.handlers:
                if room_id != handler.room_id:
                    continue
                if not handler.keep_running:
                    continue
                handler.socket.sendall(message)


    """
    Methods to process received message
    """

    def recv_login(self, message):
        if protocol.PROP_NAME not in message:
            return

        name = str(message[protocol.PROP_NAME])
        id = self.server.login(name)

        msg_send = dict()
        msg_send[protocol.ACTION] = message[protocol.ACTION]
        if id > 0:
            self.id = id
            self.nickname = name
            msg_send[protocol.PROP_STATUS] = 1
            msg_send[protocol.PROP_ID] = id
        else:
            msg_send[protocol.PROP_STATUS] = 0

        self.send(msg_send)


    def recv_logout(self, message):
        status = self.server.logout(self.id)
        if status > 0:
            self.id = -1
            self.nickname = ""

        msg_send = dict()
        msg_send[protocol.ACTION] = message[protocol.ACTION]
        msg_send[protocol.PROP_STATUS] = status
        self.send(msg_send)


    def recv_room_list(self, message):
        msg_send = dict()
        msg_send[protocol.ACTION] = message[protocol.ACTION]
        msg_send[protocol.PROP_ROOMS] = self.server.room_list()
        self.send(msg_send)


    def recv_create(self, message):
        if  protocol.PROP_NAME not in message or \
            protocol.PROP_SIZE not in message:
            return

        name = str(message[protocol.PROP_NAME])
        size = int(message[protocol.PROP_SIZE])
        status = self.server.create(self.id, name, size)
        if status > 0:
            self.room_id = status

        msg_send = dict()
        msg_send[protocol.ACTION] = message[protocol.ACTION]
        msg_send[protocol.PROP_STATUS] = status
        self.send(msg_send)

        if status > 0:
            self.broadcast_player_list(self.room_id)

            if self.room_id not in self.server.room_game:
                return

            # start the game if full
            game = self.server.room_game[self.room_id]
            if len(game.players) < game.player_size:
                return

            game.start()
            self.broadcast_player_list(self.room_id)
            self.broadcast_spectator_list(self.room_id)
            self.broadcast_game(self.room_id)


    def recv_join(self, message):
        if protocol.PROP_ROOM_ID not in message:
            return

        room_id = int(message[protocol.PROP_ROOM_ID])
        status = self.server.join(self.id, room_id)
        if status > 0:
            self.room_id = room_id

        msg_send = dict()
        msg_send[protocol.ACTION] = message[protocol.ACTION]
        msg_send[protocol.PROP_STATUS] = status
        self.send(msg_send)

        if status > 0:
            self.broadcast_player_list(self.room_id)
            self.broadcast_spectator_list(self.room_id)

            if self.room_id not in self.server.room_game:
                return

            # start the game if full
            game = self.server.room_game[self.room_id]
            if len(game.players) < game.player_size:
                return

            game.start()
            self.broadcast_game(self.room_id)


    def recv_spectate(self, message):
        if protocol.PROP_ROOM_ID not in message:
            return

        room_id = int(message[protocol.PROP_ROOM_ID])
        status = self.server.spectate(self.id, room_id)
        if status > 0:
            self.room_id = room_id

        msg_send = dict()
        msg_send[protocol.ACTION] = message[protocol.ACTION]
        msg_send[protocol.PROP_STATUS] = status
        self.send(msg_send)

        if status > 0:
            # broadcast spectator list to that room
            self.broadcast_spectator_list(self.room_id)

            # send current player list and game state
            self.send_player_list()
            self.send_game()


    def recv_leave(self, message):
        status = self.server.leave(self.id)

        msg_send = dict()
        msg_send[protocol.ACTION] = message[protocol.ACTION]
        msg_send[protocol.PROP_STATUS] = status
        self.send(msg_send)

        if status > 0:
            room_id = self.room_id
            self.room_id = -1
            self.broadcast_player_list(room_id)
            self.broadcast_spectator_list(room_id)
            self.broadcast_game(room_id)


    def recv_move(self, message):
        if  protocol.PROP_ROW not in message or \
            protocol.PROP_COLUMN not in message:
            return

        row = int(message[protocol.PROP_ROW])
        column = int(message[protocol.PROP_COLUMN])
        status = self.server.move(self.id, row, column)

        if status > 0:
            self.broadcast_game(self.room_id)


    def recv_chat(self, message):
        if protocol.PROP_CONTENT not in message:
            return
        self.broadcast_chat(self.room_id, message[protocol.PROP_CONTENT])


    def recv_highscore(self, message):
        highscore = self.server.highscore()

        msg_send = dict()
        msg_send[protocol.ACTION] = message[protocol.ACTION]
        msg_send[protocol.PROP_HIGHSCORE] = highscore
        self.send(msg_send)


    """
    Methods to send message
    """
    def send_player_list(self):
        if not self.room_id > 0:
            return

        msg_send = dict()
        msg_send[protocol.ACTION] = protocol.ACTION_PLAYER_LIST
        msg_send[protocol.PROP_PLAYERS] = self.server.player_list(self.room_id)
        self.send(msg_send)

    def send_spectator_list(self):
        if not self.room_id > 0:
            return

        msg_send = dict()
        msg_send[protocol.ACTION] = protocol.ACTION_SPECTATOR_LIST
        msg_send[protocol.PROP_SPECTATORS] = self.server.spectator_list(self.room_id)
        self.send(msg_send)


    def send_game(self):
        if not self.room_id > 0:
            return

        if self.room_id not in self.server.room_game:
            return

        game = self.server.room_game[self.room_id]
        msg_send = dict()
        msg_send[protocol.ACTION] = protocol.ACTION_GAME
        msg_send[protocol.PROP_BOARD] = game.board
        msg_send[protocol.PROP_TURN] = game.turn
        msg_send[protocol.PROP_STATUS] = game.status
        msg_send[protocol.PROP_WINNING_ROWS] = game.winning_rows
        msg_send[protocol.PROP_WINNING_COLUMNS] = game.winning_columns
        self.send(msg_send)


    """
    Methods to broadcast message
    """
    def broadcast_game(self, room_id):
        if not room_id > 0:
            return

        if room_id not in self.server.room_game:
            return

        game = self.server.room_game[room_id]
        if game.status == sujeongku.STATUS_FINISHED:
            return

        msg_broadcast = dict()
        msg_broadcast[protocol.ACTION] = protocol.ACTION_GAME
        msg_broadcast[protocol.PROP_BOARD] = game.board
        msg_broadcast[protocol.PROP_TURN] = game.turn
        msg_broadcast[protocol.PROP_STATUS] = game.status
        if game.status == sujeongku.STATUS_WIN:
            msg_broadcast[protocol.PROP_WINNING_ROWS] = game.winning_rows
            msg_broadcast[protocol.PROP_WINNING_COLUMNS] = game.winning_columns
        self.broadcast(room_id, msg_broadcast)

        # update the highscore if win
        if game.status == sujeongku.STATUS_WIN and game.turn in self.server.user_name:
            player_name = self.server.user_name[game.turn]
            # player already on the scoreboard
            if player_name in self.server.scoreboard:
                score = self.server.scoreboard[player_name] + 1
            else:
                score = 1
            self.server.scoreboard[player_name] = score

        # mark as finished to avoid re-broadcast
        if  game.status == sujeongku.STATUS_DRAW or \
            game.status == sujeongku.STATUS_WIN or \
            game.status == sujeongku.STATUS_ABORT:
            game.status = sujeongku.STATUS_FINISHED


    def broadcast_player_list(self, room_id):
        if not room_id > 0:
            return

        msg_broadcast = dict()
        msg_broadcast[protocol.ACTION] = protocol.ACTION_PLAYER_LIST
        msg_broadcast[protocol.PROP_PLAYERS] = self.server.player_list(room_id)
        self.broadcast(room_id, msg_broadcast)


    def broadcast_spectator_list(self, room_id):
        if not room_id > 0:
            return

        msg_broadcast = dict()
        msg_broadcast[protocol.ACTION] = protocol.ACTION_SPECTATOR_LIST
        msg_broadcast[protocol.PROP_SPECTATORS] = self.server.spectator_list(room_id)
        self.broadcast(room_id, msg_broadcast)


    def broadcast_chat(self, room_id, content):
        if not room_id > 0:
            return

        msg_broadcast = dict()
        msg_broadcast[protocol.ACTION] = protocol.ACTION_CHAT
        msg_broadcast[protocol.PROP_SENDER] = {protocol.PROP_ID: self.id, protocol.PROP_NAME: self.nickname}
        msg_broadcast[protocol.PROP_CONTENT] = content
        self.broadcast(room_id, msg_broadcast)

