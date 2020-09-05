import sqlite3
import operator
import pickle
#import _pickle as cPickle
import os
#import _json as cJson

class AccountNotFound(Exception):
	pass
class UsernameTaken(Exception):
	pass
class MoreThanTwoLoggedIn(Exception):
	pass
class AlreadyLoggedIn(Exception):
	pass
class NotLoggedIn(Exception):
	pass


def CreateTables():
	command = """CREATE TABLE Player (
		PlayerID INTEGER PRIMARY KEY,
		Username VARCHAR(30) NOT NULL,
		PasswordHash VARCHAR(255)
	);"""
	conn.execute(command)

	command = """CREATE TABLE Game
		(GameID INTEGER PRIMARY KEY,
		CurrentBoard BLOB,
		MoveStack BLOB,
		TimeStamp DATETIME NOT NULL,
		TimeRemaining INT NOT NULL);"""
	conn.execute(command)

	command = """CREATE TABLE GamePlayed
		(GamePlayedID INTEGER PRIMARY KEY,
		GameID INTEGER NOT NULL,
		PlayerID INTEGER NOT NULL,
		PlayerColour TEXT NOT NULL,
		State TEXT NOT NULL,
		FOREIGN KEY(GameID) REFERENCES Game(GameID),
		FOREIGN KEY(PlayerID) REFERENCES Player(PlayerID)
		);"""
	conn.execute(command)


def PopulateDatabase():
	#Inserting testing data - 3 players: Vij,Tij, Nij. Vij and Nij are in a game, Tij and Vij have completed a game (Vij won), Nij and Tij completed a game (Tij won), Vij and Nij have completed a game (Vij won).
	insert = """INSERT INTO Player (Username, PasswordHash)
						VALUES ('Vij' , 'safdjpow123p9834');
						INSERT INTO Player (Username, PasswordHash)
						VALUES ('Tij', 'rflkn234inwedad');
						INSERT INTO Player (Username, PasswordHash)
						VALUES ('Nij', 'ioqwqne1234oidsru');
						INSERT INTO Game (CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
						VALUES (011010101, 10101011001, '2020-07-08 15:46:53', 12);
						INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						VALUES (1, 1, 'B', 'MyTurn');
						INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						VALUES (1, 3, 'W', 'TheirTurn');
						INSERT INTO Game (CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
						VALUES (1010010110, 1010110110, '2020-03-15 11:24:53', 8);
						INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						VALUES (2, 2, 'W', 'Lost');
						INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						VALUES (2, 1, 'B', 'Won');
						INSERT INTO Game (CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
						VALUES (1010101101010, 10101011010110, '2020-01-03 19:21:12', 27);
						INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						VALUES (3, 3, 'B', 'Lost');
						INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						VALUES (3, 2, 'W', 'Won');
						INSERT INTO Game (CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
						VALUES (101011010101, 10101010101101, '2019-12-03 21:34:57', 3);
						INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						VALUES (4, 1, 'B', 'Won');
						INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						VALUES (4, 3, 'W', 'Lost');"""
	for i in insert.split(';'):
		conn.execute(i)


def CreateAccount(username,passwordhash):
	query = f"""SELECT Username FROM Player WHERE Username = '{username}';"""
	result = list(conn.execute(query))
	if result: raise UsernameTaken
	insert = f"""INSERT INTO Player (Username, PasswordHash)
							 VALUES ('{username}', '{passwordhash}')"""
	conn.execute(insert)
	Login(username,passwordhash)


def Login(username,passwordhash):
	query = f"""SELECT PasswordHash, PlayerID FROM Player WHERE Username = '{username}';"""
	result = list(conn.execute(query))
	if not result: raise AccountNotFound
	if passwordhash != result[0][0]: raise AccountNotFound
	global LoggedIn
	if len(LoggedIn) == 2: raise MoreThanTwoLoggedIn
	if result[0][1] in LoggedIn.values(): raise AlreadyLoggedIn
	LoggedIn[username] = result[0][1]


def Logout(username, GameInProgress, CurrentBoard=[], MoveStack=[], TimeStamp='', TimeRemaining=0, Colour='', State=''):
	global LoggedIn
	if username not in LoggedIn.keys(): raise NotLoggedIn
	if GameInProgress:
		SaveGame(CurrentBoard, MoveStack, TimeStamp, TimeRemaining, LoggedIn[username], Colour, State)
	del LoggedIn[username]


def SaveGame(CurrentBoard, MoveStack, TimeStamp, TimeRemaining, P1ID, P1Colour, P1State):
	CurrentBoardData = pickle.dumps(CurrentBoard, -1)
	print(CurrentBoardData, type(CurrentBoardData))
	#print(cPickle.loads(CurrentBoardData))
	CurrentBoardBlob = sqlite3.Binary(CurrentBoardData)
	print(CurrentBoardBlob, type(CurrentBoardBlob))
	#print(CurrentBoardBlob, type(CurrentBoardBlob))
	#CurrentBoardBlob = CurrentBoardData.tobytes()
	#print(type(CurrentBoardData), type(CurrentBoardBlob))
	MoveStackData = bytes(pickle.dumps(MoveStack, -1))
	MoveStackBlob = sqlite3.Binary(MoveStackData)
	#MoveStackBlob = MoveStackData.tobytes()

	insert = f"""INSERT INTO Game (CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
							 VALUES ('{CurrentBoardBlob}', '{MoveStackBlob}', '{TimeStamp}', '{TimeRemaining}')"""
	conn.execute(insert)
	query = """SELECT last_insert_rowid()"""
	GameID = list(conn.execute(query))[0][0]
	insert = f"""INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
						   VALUES ({GameID}, {P1ID}, '{P1Colour}', '{P1State}')"""
	conn.execute(insert)
	P2State = {'Won':'Lost','Lost':'Won','Drew':'Drew','MyTurn':'TheirTurn','TheirTurn':'MyTurn'}[P1State]
	insert = f"""INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
							 VALUES ({GameID}, {[i for i in LoggedIn.values() if i!=P1ID][0]}, '{ {'B':'W','W':'B'}[P1Colour]}', '{P2State}')"""
	conn.execute(insert)


def ForfeitGame(username, CurrentBoard, MoveStack, TimeStamp, TimeRemaining, P1Colour):
	if username not in LoggedIn.keys(): raise AccountNotFound
	SaveGame(CurrentBoard, MoveStack, TimeStamp, TimeRemaining, LoggedIn[username], P1Colour, 'Lost')


def ShowLeaderboard():
	query = """SELECT COUNT(*) FROM Player;"""
	PlayerCount = list(conn.execute(query))[0][0]
	
	leaderboard = []
	for i in range(PlayerCount):
		query = f"""SELECT State, Username FROM GamePlayed
		           	JOIN Player ON Player.PlayerID = GamePlayed.PlayerID
		           	WHERE Player.PlayerID = {i+1};"""
		result = list(conn.execute(query))
		states = [j[0] for j in result]
		score = (3 * states.count('Won')) + (1 * states.count('Drew'))
		leaderboard.append({'PlayerID':i+1, 'Username': result[0][1], 'Wins':states.count('Won'), 'Losses':states.count('Lost'), 'Draws':states.count('Drew'), 'Points':score})
		
	leaderboard.sort(key = operator.itemgetter('Points'), reverse = True)
	return leaderboard


def ShowHeadToHead():
	if len(LoggedIn) < 2: raise NotLoggedIn
	query = f"""SELECT GameID FROM GamePlayed
				      WHERE PlayerID = {list(LoggedIn.values())[0]}
							AND (STATE != 'MyTurn' AND STATE != 'TheirTurn')"""
	GameList = [i[0] for i in conn.execute(query)]
	results = {"Won":0,"Lost":0,"Drew":0}
	for id in GameList:
		query = f"""SELECT GamePlayed.State FROM GamePlayed JOIN Game ON
									GamePlayed.GameID = Game.GameID WHERE Game.GameID = {id}
									AND GamePlayed.PlayerID = {list(LoggedIn.values())[1]}"""
		result = list(conn.execute(query))
		if result:
			results[result[0][0]] += 1
	FinalResults = {f"{list(LoggedIn.keys())[1]} Won": results["Won"], f"{list(LoggedIn.keys())[0]} Won": results["Lost"], "Drew": results["Drew"]}
	return FinalResults


def ShowCurrentGames():
	if not LoggedIn : raise NotLoggedIn
	query = f"""SELECT GameID FROM GamePlayed
				      WHERE PlayerID = {list(LoggedIn.values())[0]}
							AND (STATE = 'MyTurn' OR STATE = 'TheirTurn')"""
	GameList = [i[0] for i in conn.execute(query)]
	Games = []
	if len(LoggedIn) == 1:
		for id in GameList:
			query = f"""SELECT GamePlayed.PlayerID, Game.TimeStamp FROM GamePlayed JOIN Game ON
									GamePlayed.GameID = Game.GameID WHERE Game.GameID = {id}
									AND GamePlayed.PlayerID!={list(LoggedIn.values())[0]}"""
			result = list(conn.execute(query))[0]
			Games.append({'GameID': id, 'OpponentID': result[0], 'Timestamp': result[1]})
	else:
		for id in GameList:
			select = f"""SELECT GameID FROM GamePlayed
				        	 WHERE PlayerID = {list(LoggedIn.values())[1]}
									 AND GameID = {id}"""
			if list(conn.execute(select)):
				query = f"""SELECT TimeStamp FROM Game
						        WHERE GameID = {id}"""
				Games.append({'GameID': id, 'Timestamp':list(conn.execute(query))[0][0]})

	Games.sort(key=operator.itemgetter('Timestamp'), reverse=True)
	return Games


def LoadGame(GameID):
	print('TESTING...')
	query = f"""SELECT * FROM Game WHERE GameID = {GameID}"""
	result = conn.execute(query)
	array = list(result)[0][1]
	print(type(array))
	print(array)
	
	#<memory at 0x00000242E5E7F648> <class 'memoryview'>
	#print(cPickle.loads(result[1]))
	#print(result)
	#for i in result:
	#	print(i['GameID'])
	data = []
	#print(cPickle.loads(result[1]))
	#cPickle.loads(result[1])
	#sqlite3.Text()
	
	
	'''
	for i in range(len(result)):
		print(type(result[i]))
		try:
			#print(cPickle.loads(str(result[i])))
			data.append(cPickle.loads(result[i]))
		except TypeError:
			print(result[i])
			data.append(result[i])
	print(data)
	'''

		



if os.path.isfile('test.db'):
	conn = sqlite3.connect('test.db')
else:
	conn = sqlite3.connect('test.db')
	CreateTables()
	#PopulateDatabase()

LoggedIn = dict()
'''
print(type(cPickle.dumps([1,2,3],-1)))
#print(print(sqlite3.Binary(cPickle.dumps([1,2,3],-1))))

x = cPickle.dumps([1,2,3],-1)
x = sqlite3.Binary(x)
print(x)
#y = sqlite3.Text(x)
#print(type(x))
#print(list(x))
#print(y)
y = cPickle.loads(x)
print(y)
'''
#Test functions:
#print('GamePlayed:', list(conn.execute('SELECT * FROM GamePlayed')))
#print('Game: ', list(conn.execute('SELECT * FROM Game')))
#print('Player: ', list(conn.execute('SELECT * FROM Player')))
CreateAccount('Vij','safdjpow123p9834')
CreateAccount('Tij','rflkn234inwedad')
Logout('Vij',True,[1,2,3],[1,2,[1,2],2,3],"2020-07-13 21:17:45", 12, "B", "Won")
LoadGame(1)

conn.commit()
conn.close()