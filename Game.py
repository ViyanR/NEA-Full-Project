from enum import auto,Enum

class GameError(Exception):
	pass

class Game:
	EMPTY = ""
	P1 = "B"
	P2 = "W"
	DRAW = auto()
	SIZE = 8
	
	def __init__(self):
		self._board = [[Game.EMPTY for _ in Game.SIZE] for _ in Game.SIZE]
		self._player = Game.P1
	pass
	
	def __repr__(self):
		output += "".join([str(j + 1) + " " for j in range(Game.DIM)]) + "\n"
		for i in range(Game.DIM):
			output += str(i + 1) + " " + "|".join([self._board[i][j] for j in range(Game.DIM)]) + "\n"
		return output
	
	def play(self,row,column):
		if not (0 < row <= Game.DIM):
			raise GameError(f"Row {row} out of range")
		if not (0 < col <= Game.DIM):
			raise GameError(f"Column {col} out of range")
	
		row -= 1
		col -= 1
	
		if self._board[row][col] != Game.EMPTY:
			raise GameError(f"Board not empty in {row},{col}")
	
		self._board[row][col] = self._player
		if self._player == Game.P1:
			self._player = Game.P2
		else:
			self._player = Game.P1
	
	@property
	def winner(self):
		pass
	
	@property
	def drawer(self):
		pass
	
if __name__ == '__main__':
	#Unit Testing
	pass
