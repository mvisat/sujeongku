from player import *
from room import *

class Game:
	def __init__ (self, rid, pid):
		self.room = rid
		self.board = [ [ 0 for x in range(20) ] for x in range(20) ]
		self.turn = 0
		self.winner = -1
		self.players = []
		self.isStart = False

	def setBoard(self, x, y, char):
		self.board[x][y] = char

	def getOwner (self):
		if self.getPlayerCount() == 0:
			return ""
		else:
			return self.players[0]

	def isOwner (self, player):
		return player.getID() == self.getOwner().getID()

	def isGameStarted (self):
		return self.isStart

	def getPlayerCount (self):
		return len(self.players)

	def getTurn (self):
		return self.players[self.turn]

	def nextTurn (self):
		self.turn += 1
		if self.turn > len(self.players):
			self.turn = 0

	def getPlayerList (self):
		return self.players

	def addPlayer (self, pid):
		self.players.append(pid)

	def delPlayer (self, pid):
		self.players.remove(pid)

	def startGame (self):
		self.isStart = True

	def stopGame (self):
		self.isStart = False

	def __del__ (self):
		print "Game from Room ( " + str(self.room) + " ) stopped"