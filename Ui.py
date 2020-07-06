from Game import Game
from abc import ABC, abstractmethod

class Ui(ABC):
	
	@abstractmethod
	def run(self):
		raise NotImplementedError
	

class Gui(Ui):
	def __init__(self):
		pass
	
	def run(self):
		pass
	

class Terminal(Ui):
	def __init__(self):
		pass
	
	def run(self):
		pass
	
	
if __name__ == '__main__':
	#Unit Testing
	pass


