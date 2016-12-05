#! /usr/bin/env python
from memory import Spelunker
import irc.bot
import irc.strings
import people, csv
from bets import bettingEngine
from odds import oddsEngine
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from threading import Thread, Lock, Timer


class BetBot(irc.bot.SingleServerIRCBot):

	def __init__(self, channel, nickname, server):
		irc.bot.SingleServerIRCBot.__init__(self, [server], nickname, nickname)
		self.channel = channel
		self.theOdds = oddsEngine()
		self.theBetter = bettingEngine(self.theOdds)
		self.user = people.users()
		self.sp = Spelunker()
		self.is_dead = self.sp.is_dead
		self.past_level = self.sp.level
		self.deathDict={}
		with open('death_list.csv') as csvfile:
			rawData = csv.reader(csvfile, delimiter = ',')
			for row in rawData:
				self.deathDict[row[1]]=row[0]
		self.reactor.execute_every(5,self.process_spelunker)
		self.theLock = Lock()
		self.start()

	def process_spelunker(self):
		death_state = int(self.sp.is_dead)
		current_level = int(self.sp.level)
		if self.past_level != current_level:
			#trigger level change stuff
			item_dict = self.get_item_list()
			print(current_level)
			self.theOdds.levelChangeOdds(self.sp.level,self.sp.health,item_dict, self.sp.ropes,self.sp.bombs,self.special_level)
			if current_level == 1:
				self.theOdds = oddsEngine()
				self.theBetter = bettingEngine(self.theOdds)
			special = self.special_level()
			print (str(special))
			if special == None:
				special = 'nope'
			self.connection.privmsg(str(self.channel),"Level "+str(self.sp.level)+" "+str(self.sp.health)+ ' is the current heath left. Special level = ' + str(special))
			self.theLock.release
		self.past_level = current_level
		if not self.is_dead and death_state:
			#trigger player death stuff
			killedBy = self.deathDict[str(self.sp.killed_by)]
			special_level_outcome = self.special_level()
			holdOff =Timer(7,self.gameOver,args=(self.sp.level, killedBy, special_level_outcome, self.sp.gold_count, self.sp.ropes,self.sp.bombs))
			pubMess = Timer(10,self.theLock.release)
			holdOff.run()
			pubMess.run()
		self.is_dead = death_state

	def get_item_list(self):
		itemList = {}
		itemList['jetpack'] = self.sp.has_jetpack
		itemList['compass'] = self.sp.has_compass
		itemList['parachute'] = self.sp.has_parachute
		itemList['climbing_gloves'] = self.sp.has_climbing_gloves
		itemList['pitchers_mitt'] = self.sp.has_pitchers_mitt
		itemList['spring_shoes'] = self.sp.has_spring_shoes
		itemList['spike_shoes'] = self.sp.has_spike_shoes
		itemList['spectacles'] = self.sp.has_spectacles
		itemList['kapala'] = self.sp.has_kapala
		itemList['hedjet'] = self.sp.has_hedjet
		itemList['udjat_eye'] = self.sp.has_udjat_eye
		itemList['book_of_dead'] = self.sp.has_book_of_dead
		itemList['ankh'] = self.sp.has_ankh
		itemList['paste'] = self.sp.has_paste
		itemList['cape'] = self.sp.has_cape
		itemList['vlads_cape'] = self.sp.has_vlads_cape
		itemList['crysknife'] = self.sp.has_crysknife
		itemList['vlads_amulet'] = self.sp.has_vlads_amulet
		return itemList

	def special_level(self):
		levelList= {}
		levelList['lvl_dark'] =self.sp.lvl_dark
		levelList['lvl_worm'] =self.sp.lvl_worm
		levelList['lvl_black_market'] =self.sp.lvl_black_market
		levelList['lvl_hmansion'] =self.sp.lvl_hmansion
		levelList['lvl_yeti'] =self.sp.lvl_yeti
		levelList['lvl_cog'] =self.sp.lvl_cog
		levelList['lvl_mothership'] =self.sp.lvl_mothership
		for key in levelList:
			if levelList[key]:
				return key
		return None

	def send_message(self, message, user):
		self.connection.privmsg(str(self.channel),"/w "+user+ " "+ message)

	def send_pub_message(self, message):
		self.theLock.acquire()
		self.connection.privmsg(str(self.channel), message)


	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def gameOver(self,condtion1, condition2,special_level, gold=None, ropes =None, bombs=None):
		self.theBetter.tallyWinnings(condtion1, condition2,special_level, gold, ropes, bombs)
		self.send_pub_message("Bets calculated. Died on level "+str(condtion1) + " and "+ str(condition2) + " was the killer.")

	def on_welcome(self, c, e):
		print('joining {0}'.format(self.channel))
		c.send_raw("CAP REQ :twitch.tv/commands")
		c.join(self.channel)
		c.set_rate_limit(100/30)

	def on_pubmsg(self, c, e):
	  a = e.arguments[0].split("!", 1) #splitsthe
	  #print(e)
	  #print(a)
	  if (len(a) > 1):
		  self.do_command(e, a[1].strip())
	  return

	def on_whisper(self, c, e):
		self.on_pubmsg(c,e)

	def do_command(self, e, cmd):
		nick = self._nickname
		cmd = cmd.split(" ")
		bet = 0
		if (len(cmd)> 1):
			if (len(cmd)== 3):
				condition1 = str(cmd[2])
				condition2 = None
				try:
					bet = int(cmd[1])
				except:
					bet = 0
				cmd = cmd[0]
			elif (len(cmd)== 4):
				condition1 = str(cmd[2])
				condition2 = str(cmd[3])
				if condition1 == condition2:
					condtion2 = None
				try:
					bet = int(cmd[1])
				except:
					bet = 0
				cmd = cmd[0]
		c = self.connection
		twitchUser = str(e.source.split("!")[0])
		channelName = self.channel
		if cmd == "bet" and bet!= 0:
			userBet = self.theBetter.placeBet(twitchUser, bet, condition1, condition2)
			balance = self.user.getUserBalance(twitchUser)
			if userBet == -2:
				c.privmsg(str(channelName),"/w "+ twitchUser+ " you bet "+ str(bet) + " but you only have " + str(balance) + " Golden Daves so thats the amount you bet you cheater")
			elif userBet == -1:
				c.privmsg(str(channelName),"/w "+ twitchUser+ " you bet on something that doesnt exist.  Ive refunded your money but make sure you spell it right next time or maybe i wont be so nice")
			else:
				c.privmsg(str(channelName),"/w "+ twitchUser+ " odds are "+ str(userBet[2])+ " winnings =" + str(userBet[3]) + " Golden Daves balance = "+ str(balance) + " Golden Daves")
		elif cmd[0] == "balance":
			balance = self.user.getUserBalance(twitchUser)
			c.privmsg(str(channelName),"/w "+ twitchUser +" Your balance is " + str(balance)+ " Golden Daves")
		elif cmd[0] == "stfu":
			c.privmsg(str(channelName),"no Kappa")
		elif cmd[0] == "nobet":
			returned = self.theBetter.stopBet(twitchUser)
			if returned == True:
				c.privmsg(str(channelName),"/w "+ twitchUser +" Your Bet(s) were canceled")
			else:
				c.privmsg(str(channelName),"/w "+ twitchUser +" Your bet was not canncled since the player died or your 10 second window passed")
		elif cmd[0] == "hi":
			c.privmsg(str(channelName),"/w "+ twitchUser+ " hi")
		elif cmd[0] == "ankh":
			c.privmsg(str(channelName),"Good thing I have the ankh")
		elif cmd[0] == "die" and (twitchUser == 'rellim7' or twitchUser == 'bunny_funeral'):
			self.die()
		else:
			c.privmsg(str(channelName),"/w "+ twitchUser+ " Not understood: " + str(cmd))

def irc_thread(oauth_file,channel,nickname):
	odds = oddsEngine.oddsEngine()
	bets = betEngine.bettingEngine(odds)

	with open(oauth_file, 'r') as fp:
		password = fp.read()

	server = irc.bot.ServerSpec('irc.twitch.tv', port=6667, password=password.strip())

	bot = BetBot(channel, nickname, server, bets, odds)
	bot.start()


def main():
	odds = oddsEngine()
	bets = bettingEngine(odds)

	with open('oauth_token', 'r') as fp:
		password = fp.read()

	server = irc.bot.ServerSpec('irc.twitch.tv', port=6667, password=password.strip())

	bot = BetBot('#rellim7','spelunkybot', server)
	bot.start()


if __name__ == "__main__":
	main()
