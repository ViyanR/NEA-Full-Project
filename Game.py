from enum import auto,Enum

class GameError(Exception):
	pass

class Game:
	P1 = 'B'
	P2 = 'W'
	DRAW = auto()
	SIZE = 8
	
	def __init__(self):
		pass
	
	def __repr__(self):
		pass
	
	def play(self,row,column):
		pass
	
	@property
	def winner(self):
		pass
	
	@property
	def drawer(self):
		pass
	
if __name__ == '__main__':
	#Unit Testing
	pass
