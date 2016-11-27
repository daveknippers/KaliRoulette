
from SpelunkyBot import BetBot
from memory import Spelunker
from threading import Thread
import irc, time, csv


def i_hate_snakes():

	with open('oauth_token', 'r') as fp:
		password = fp.read()
	server = irc.bot.ServerSpec('irc.twitch.tv', port=6667, password=password.strip())

	thread = Thread(target = BetBot,args=('#rellim7','spelunkybot',server))
	thread.start()
	deathDict={}
	with open('death_list.csv') as csvfile:
		rawData = csv.reader(csvfile, delimiter = ',')
		for row in rawData:
			deathDict[row[1]]=row[0]
	sp = Spelunker()
	tripped = False
	while True:
		time.sleep(4)
		if sp.is_dead == 1 and tripped ==False:
			bombs = sp.bombs
			ropes = sp.ropes
			level = sp.level
			gold = 0 #replace with sp.gold when its there
			killedBy = sp.last_killed_by
			killedBy = deathDict[str(killedBy)]
			thread.gameOver(level,killedBy,gold,ropes,bombs)
			print (killedBy)
			tripped = True
		elif sp.is_dead ==1 and tripped==True:
			print('gameover')
		if sp.is_dead ==0 and tripped == True:
			tripped = False

if __name__ == "__main__":
	i_hate_snakes()
