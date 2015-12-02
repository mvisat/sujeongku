class Player:
	def __init__ (self, pid, iport, name):
		self.id = pid
		self.iport = iport
		self.name = name
		self.room = -1
		self.char = '?'

	def getID (self):
		return self.id

	def getIPort (self):
		return self.iport

	def getName (self):
		return self.name

	def getChar (self):
		return self.char

	def getRoomID (self):
		return self.room

	def setRoomID (self, rid):
		self.room = rid

	def setChar (self, char):
		self.char = char

	def __del__ (self):
		print "Player [ " +  self.name + " ("  + str(self.id) + ") ] exited"
