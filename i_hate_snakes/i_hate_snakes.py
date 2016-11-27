
from SpelunkyBot import irc_thread
from memory import Spelunker
from threading import Thread
import irc, time
from odds import oddsEngine
from bets import bettingEngine

def i_hate_snakes():
	odds = oddsEngine()
	bets = bettingEngine(odds)
	thread = Thread(target = irc_thread,args=('oauth_token','#rellim7','spelunkybot', bets, odds))
	thread.start()
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
			bets.tallyWinnings(level,killedBy,gold,ropes,bombs)
			print (killedBy)
			tripped = True
		elif sp.is_dead ==1 and tripped==True:
			print('gameover')
		if sp.is_dead ==0 and tripped == True:
			tripped = False

if __name__ == "__main__":
	i_hate_snakes()
