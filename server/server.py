import operator
import threading

from common import protocol
from common import sujeongku

class server:

    def __init__(self):
        self.handlers = []
        self.handlers_lock = threading.Lock()
        self.keep_running = True

        # private locks
        self.__player_lock = threading.Lock()
        self.__room_lock = threading.Lock()

        self.user_names = set()
        self.user_name = dict()
        self.user_last_id = 0

        self.rooms = dict()
        self.room_last_id = 0
        self.room_game = dict()
        self.room_size = dict()

        # room id -> [player id]
        self.room_player = dict()
        # room id -> [spectator id]
        self.room_spectator = dict()
        # user id -> [room id]
        self.user_room = dict()

        self.scoreboard = dict()
        self.__highscore_limit = 10


    def login(self, name):
        with self.__player_lock:
            if name in self.user_names:
                return -1
            self.user_names.add(name)
            self.user_last_id = self.user_last_id + 1
            self.user_name[self.user_last_id] = name
            return self.user_last_id


    def logout(self, id):
        self.leave(id)
        with self.__player_lock:
            if id in self.user_name:
                name = self.user_name[id]
                del self.user_name[id]
                if name in self.user_names:
                    self.user_names.remove(name)
                    return 1
        return -1


    def room_list(self):
        rooms = dict()
        with self.__room_lock:
            for room_id, (name, size) in self.rooms.items():
                if room_id not in self.room_game:
                    continue

                # only list room that is still waiting or playing
                game = self.room_game[room_id]
                if  game.status == sujeongku.STATUS_WAITING or \
                    game.status == sujeongku.STATUS_PLAYING:
                    current_size = len(game.players)
                    rooms[room_id] = (name, size, current_size)

        return rooms


    def create(self, id, name, size):
        if size > sujeongku.MAX_ROOM_SIZE or size < sujeongku.MIN_ROOM_SIZE or id in self.user_room:
            return -1

        with self.__room_lock:
            self.room_last_id = self.room_last_id + 1
            self.rooms[self.room_last_id] = (name, size)
            self.room_game[self.room_last_id] = sujeongku.game(size)
            self.room_size[self.room_last_id] = size
            self.room_player[self.room_last_id] = set()
            self.room_spectator[self.room_last_id] = set()

        self.join(id, self.room_last_id)
        return self.room_last_id


    def join(self, id, room_id):
        with self.__room_lock:
            if (id not in self.user_name) or (room_id not in self.rooms):
                return -1

            # check if room is full
            players = self.room_player[room_id]
            room_size = self.room_size[room_id]
            if len(players) >= room_size:
                return -1

            # only add player if it's still waiting players
            game = self.room_game[room_id]
            if game.status != sujeongku.STATUS_WAITING:
                return -1

            # add to room as player
            game.add_player(id)
            players.add(id)
            self.user_room[id] = room_id
            return 1


    def spectate(self, id, room_id):
        with self.__room_lock:
            if (id not in self.user_name) or (room_id not in self.rooms):
                return -1

            # only add spectator if it's still waiting or playing
            game = self.room_game[room_id]
            if  game.status != sujeongku.STATUS_WAITING and \
                game.status != sujeongku.STATUS_PLAYING:
                return -1

            # add to room as spectator
            room = self.room_spectator[room_id]
            room.add(id)
            self.user_room[id] = room_id
            return 1


    def leave(self, id):
        with self.__room_lock:
            if (id not in self.user_name) or (id not in self.user_room):
                return -1

            # delete him from user room
            room_id = self.user_room[id]
            del self.user_room[id]

            if room_id not in self.room_player or room_id not in self.room_spectator:
                return -1
            room_player = self.room_player[room_id]
            room_spectator = self.room_spectator[room_id]

            # user is playing in the room
            if id in room_player:
                room_player.remove(id)
                # remove from the game
                if room_id in self.room_game:
                    game = self.room_game[room_id]
                    game.remove_player(id)

                    # if player size < allowed minimum, abort the game
                    if len(game.players) < sujeongku.MIN_ROOM_SIZE:
                        game.status = sujeongku.STATUS_ABORT
                        game.turn = protocol.INVALID_ID

            # user is spectating the room
            elif id in room_spectator:
                room_spectator.remove(id)

            # delete the room if there is no player or spectator
            if len(room_player) == 0 and len(room_spectator) == 0:
                if room_id in self.rooms:
                    del self.rooms[room_id]
                if room_id in self.room_game:
                    del self.room_game[room_id]
                if room_id in self.room_size:
                    del self.room_size[room_id]
                if room_id in self.room_player:
                    del self.room_player[room_id]
            return 1


    def player_list(self, room_id):
        players = list()
        with self.__room_lock:
            if room_id in self.room_player:
                for player_id in self.room_player[room_id]:
                    players.append(
                        {protocol.PROP_ID: player_id, protocol.PROP_NAME: self.user_name[player_id]})
        return players


    def spectator_list(self, room_id):
        spectators = list()
        with self.__room_lock:
            if room_id in self.room_spectator:
                for player_id in self.room_spectator[room_id]:
                    spectators.append(
                        {protocol.PROP_ID: player_id, protocol.PROP_NAME:self.user_name[player_id]})
        return spectators


    def move(self, id, row, column):
        if id not in self.user_room:
            return -1

        room_id = self.user_room[id]
        if id not in self.room_player[room_id]:
            return -1

        if room_id not in self.room_game:
            return -1
        game = self.room_game[room_id]

        return game.move(id, row, column)


    # return list of highscore
    # sort by score descending, limit to __highscore_limit
    def highscore(self):
        return sorted(self.scoreboard.items(), key=operator.itemgetter(1), reverse=True)[:self.__highscore_limit]


    def exit(self, id):
        self.logout(id)
