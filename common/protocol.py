"""
Module containing protocol constants
"""

INVALID_ID = -1

PROTO_END = "\n"

ACTION = "action"
ACTION_LOGIN = "login"
ACTION_LOGOUT = "logout"
ACTION_CREATE = "create"
ACTION_JOIN = "join"
ACTION_SPECTATE = "spectate"
ACTION_LEAVE = "leave"
ACTION_CHAT = "chat"
ACTION_ROOM_LIST = "room_list"
ACTION_PLAYER_LIST = "player_list"
ACTION_SPECTATOR_LIST = "spectator_list"
ACTION_MOVE = "move"
ACTION_GAME = "game"
ACTION_HIGHSCORE = "highscore"

PROP_ID = "id"
PROP_ROOM_ID = "room_id"
PROP_NAME = "name"
PROP_STATUS = "status"
PROP_SIZE = "size"
PROP_ROOMS = "rooms"
PROP_PLAYERS = "players"
PROP_SPECTATORS = "spectators"
PROP_ROW = "row"
PROP_COLUMN = "column"
PROP_SENDER = "sender"
PROP_CONTENT = "content"
PROP_BOARD = "board"
PROP_TURN = "turn"
PROP_HIGHSCORE = "highscore"
PROP_WINNING_ROWS = "winning_rows"
PROP_WINNING_COLUMNS = "winning_columns"
