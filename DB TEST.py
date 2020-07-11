import sqlite3
import operator
import _pickle as cPickle

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


conn = sqlite3.connect('test.db')
LoggedIn = dict()

print("opened db successfully")

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
	insert = """INSERT INTO Player (PlayerID, Username, PasswordHash)
						VALUES (1 , 'Vij' , 'safdjpow123p9834');
						INSERT INTO Player (PlayerID, Username, PasswordHash)
						VALUES (2, 'Tij', 'rflkn234inwedad');
						INSERT INTO Player (PlayerID, Username, PasswordHash)
						VALUES (3, 'Nij', 'ioqwqne1234oidsru');
						INSERT INTO Game (GameID, CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
						VALUES (1, 01011010110110101, 101101011010, '2020-07-08 15:46:53', 12);
						INSERT INTO GamePlayed (GamePlayedID, GameID, PlayerID, PlayerColour, State)
						VALUES (1, 1, 1, 'B', 'MyTurn');
						INSERT INTO GamePlayed (GamePlayedID, GameID, PlayerID, PlayerColour, State)
						VALUES (2, 1, 3, 'W', 'TheirTurn');
						INSERT INTO Game (GameID, CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
						VALUES (2, 11101101010101, 101101010100110, '2020-03-15 11:24:53', 8);
						INSERT INTO GamePlayed (GamePlayedID, GameID, PlayerID, PlayerColour, State)
						VALUES (3, 2, 2, 'W', 'Lost');
						INSERT INTO GamePlayed (GamePlayedID, GameID, PlayerID, PlayerColour, State)
						VALUES (4, 2, 1, 'B', 'Won');
						INSERT INTO Game (GameID, CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
						VALUES (3, 1010101101010, 10101011010110, '2020-01-03 19:21:12', 27);
						INSERT INTO GamePlayed (GamePlayedID, GameID, PlayerID, PlayerColour, State)
						VALUES (5, 3, 3, 'B', 'Lost');
						INSERT INTO GamePlayed (GamePlayedID, GameID, PlayerID, PlayerColour, State)
						VALUES (6, 3, 2, 'W', 'Won');
						INSERT INTO Game (GameID, CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
						VALUES (4, 101011010101, 10101010101101, '2019-12-03 21:34:57', 3);
						INSERT INTO GamePlayed (GamePlayedID, GameID, PlayerID, PlayerColour, State)
						VALUES (7, 4, 1, 'B', 'Won');
						INSERT INTO GamePlayed (GamePlayedID, GameID, PlayerID, PlayerColour, State)
						VALUES (8, 4, 3, 'W', 'Lost');"""
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


def Logout(username, GameInProgress, CurrentBoard=bytes(), MoveStack=bytes(), TimeStamp='', TimeRemaining=0, Colour='', State=''):
	global LoggedIn
	if username not in LoggedIn.keys(): raise NotLoggedIn
	if GameInProgress:
		SaveGame(CurrentBoard, MoveStack, TimeStamp, TimeRemaining, LoggedIn[username], Colour, State)
	del LoggedIn[username]


def SaveGame(CurrentBoard, MoveStack, TimeStamp, TimeRemaining, P1ID, P1Colour, P1State):
	pdata = cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)
	
	insert = f"""INSERT INTO Game (CurrentBoard, MoveStack, TimeStamp, TimeRemaining)
									VALUES ('{CurrentBoard}', '{MoveStack}', '{TimeStamp}', '{TimeRemaining}')"""
	conn.execute(insert)
	query = f"""SELECT last_insert_rowid()"""
	GameID = list(conn.execute(query))[0][0]
	insert = f"""INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
									VALUES ('{GameID}', '{P1ID}', '{P1Colour}', '{P1State}')"""
	conn.execute(insert)
	P2State = {'Won':'Lost','Lost':'Won','Drew':'Drew','MyTurn':'TheirTurn','TheirTurn':'MyTurn'}[P1State]
	insert = f"""INSERT INTO GamePlayed (GameID, PlayerID, PlayerColour, State)
									VALUES ('{GameID}', '{(LoggedIn.values()-[P1ID])[0]}', '{(['B','W']-P1ID)[0]}', '{P2State}')"""
	conn.execute(insert)

def ForfeitGame(CurrentBoard, MoveStack, TimeStamp, TimeRemaining, P1ID, P1Colour, P1State):
	SaveGame(CurrentBoard, MoveStack, TimeStamp, TimeRemaining, P1ID, P1Colour, 'Lost')




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


#print(bytes([1,7,14,12]).hex())
#quit()
CreateTables()
CreateAccount('Yunger','numeter')
CreateAccount('Blood','Crip')
Logout('Blood', True, bytes([1,7,6,9]).hex(), bytes([1,7,16,13]).hex(), '2020-07-11 15:31:15', 29, 'B', 'Won')

conn.commit()
conn.close()