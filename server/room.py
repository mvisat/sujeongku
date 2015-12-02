class Room:
	def __init__ (self, rid, name, pid):
		self.id = rid
		self.name = name

	def getID (self):
		return self.id

	def getName (self):
		return self.name

	def __del__ (self):
		print "Room [ " + self.name + "(" + str(self.id) + ") ] deleted"