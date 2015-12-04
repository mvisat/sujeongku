from common import protocol

MIN_ROOM_SIZE = 2
MAX_ROOM_SIZE = 10

STATUS_ABORT = -1
STATUS_WAITING = 0
STATUS_PLAYING = 1
STATUS_DRAW = 2
STATUS_WIN = 3
STATUS_FINISHED = 4

ROW_SIZE = 20
COLUMN_SIZE = 20
WIN_SEQUENCE = 5


class game:

    def __init__(self, player_size=3):
        self.players = []
        self.spectators = []
        self.board = [[protocol.INVALID_ID for i in range(COLUMN_SIZE)] for j in range(ROW_SIZE)]
        self.player_size = player_size
        self.turn = protocol.INVALID_ID
        self.status = STATUS_WAITING
        self.winning_rows = []
        self.winning_columns = []

    def start(self):
        if self.status != STATUS_WAITING:
            return

        if len(self.players) < self.player_size:
            return

        self.status = STATUS_PLAYING
        self.turn = self.players[0]

    def add_player(self, id):
        if id in self.players:
            return -1

        self.players.append(id)
        return 1

    def remove_player(self, id):
        if id not in self.players:
            return -1

        # if it's his turn, skip to next player
        if id == self.turn:
            self.next_turn()

        # remove the player
        self.players.remove(id)
        return 1

    def next_turn(self):
        if self.status != STATUS_PLAYING or len(self.players) == 0:
            return -1

        self.turn = self.players[(self.players.index(self.turn) + 1) % len(self.players)]
        return 1


    def move(self, id, row, column):
        if self.status != STATUS_PLAYING:
            return -1

        if 0 > row >= ROW_SIZE or 0 > column >= COLUMN_SIZE:
            return -1

        self.board[row][column] = id

        # check if draw
        draw = True
        for i in range(ROW_SIZE):
            if not draw: break
            for j in range(COLUMN_SIZE):
                if self.board[i][j] == protocol.INVALID_ID:
                    draw = False
                    break
        if draw:
            self.status = STATUS_DRAW
            return 1

        # check vertically
        for i in range(row - WIN_SEQUENCE + 1, row + 1):
            if i < 0:
                continue
            elif i + WIN_SEQUENCE > ROW_SIZE:
                break
            win = True
            for j in range(i, i + WIN_SEQUENCE):
                if self.board[j][column] != id:
                    win = False
                    break
            if win:
                self.winning_rows = [j for j in range(i, i + WIN_SEQUENCE)]
                self.winning_columns = [column for j in range(WIN_SEQUENCE)]
                self.status = STATUS_WIN
                return 1

        # check horizontally
        for i in range(column - WIN_SEQUENCE + 1, column + 1):
            if i < 0:
                continue
            elif i + WIN_SEQUENCE > COLUMN_SIZE:
                break
            win = True
            for j in range(i, i + WIN_SEQUENCE):
                if self.board[row][j] != id:
                    win = False
                    break
            if win:
                self.winning_rows = [row for j in range(WIN_SEQUENCE)]
                self.winning_columns = [j for j in range(i, i + WIN_SEQUENCE)]
                self.status = STATUS_WIN
                return 1

        # check diagonally from bottom-right to top-left
        for i in range(WIN_SEQUENCE):
            r = row - i
            c = column - i
            win = True
            for j in range(WIN_SEQUENCE):
                if  r < 0 or r >= ROW_SIZE or \
                    c < 0 or c >= COLUMN_SIZE or \
                    self.board[r][c] != id:
                    win = False
                    break
                r, c = r + 1, c + 1
            if win:
                self.winning_rows = [j for j in range(row - i, row - i + WIN_SEQUENCE)]
                self.winning_columns = [j for j in range(column - i, column - i + WIN_SEQUENCE)]
                self.status = STATUS_WIN
                return 1

        # check diagonally from bottom-left to top-right
        for i in range(WIN_SEQUENCE):
            r = row - i
            c = column + i
            win = True
            for j in range(WIN_SEQUENCE):
                if  r < 0 or r >= ROW_SIZE or \
                    c < 0 or c >= COLUMN_SIZE or \
                    self.board[r][c] != id:
                    win = False
                    break
                r, c = r + 1, c - 1
            if win:
                self.winning_rows = [j for j in range(row - i, row - i + WIN_SEQUENCE)]
                self.winning_columns = [j for j in range(column + i, column + i - WIN_SEQUENCE, -1)]
                self.status = STATUS_WIN
                return 1

        self.status = STATUS_PLAYING
        return self.next_turn()
