#! /usr/bin/env python

import irc.bot
import irc.strings
import people
import bets as betEngine
import odds as oddEngine
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from threading import Thread

class BetBot(irc.bot.SingleServerIRCBot):

	def __init__(self, channel, nickname, server, bets, odds):
		irc.bot.SingleServerIRCBot.__init__(self, [server], nickname, nickname)
		self.channel = channel
		self.theOdds = odds
		self.theBetter = bets
		self.user = people.users()
	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")
	def gameOver(self,condtion1, condition2, gold=None, ropes =None, bombs=None):
		self.theBetter.tallyWinnings(condtion1, condition2, gold, ropes, bombs)
		c.privmsg(str(channelName),"Bets calculated " + condtion1 + " and "+ condition2 + " was the death cericumstances.")
	def on_welcome(self, c, e):
		print('joining {0}'.format(self.channel))
		c.send_raw("CAP REQ :twitch.tv/commands")
		c.join(self.channel)
		c.set_rate_limit(100/30)


	def on_pubmsg(self, c, e):
	  a = e.arguments[0].split("!", 1) #splitsthe
	  print(e)
	  print(a)
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
				bet = int(cmd[1])
				cmd = cmd[0]
			elif (len(cmd)== 4):
				condition1 = str(cmd[2])
				condition2 = str(cmd[3])
				bet = int(cmd[1])
				cmd = cmd[0]
		c = self.connection
		twitchUser = str(e.source.split("!")[0])
		channelName = self.channel
		if cmd == "bet" and bet!= 0:
			userBet = self.theBetter.placeBet(twitchUser, bet, condition1, condition2)
			blanance = self.user.getUserBalance(twitchUser)
			if userBet == -2:
				c.privmsg(str(channelName),"/w "+ twitchUser+ " you bet "+ str(bet) + " but you only have " + str(balance) + " Golden Daves so thats the amount you bet you cheater")
			elif userbet == -1:
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
		else:
			c.privmsg(str(channelName),"/w "+ twitchUser+ " Not understood: " + str(cmd))

def irc_thread(oauth_file,channel,nickname):
	odds = oddsEngine()
	bets = bettingEngine(odds)

	with open(oauth_file, 'r') as fp:
		password = fp.read()

	server = irc.bot.ServerSpec('irc.twitch.tv', port=6667, password=password.strip())

	bot = BetBot(channel, nickname, server, bets, ods)
	bot.start()


def main():
	ods = oddEngine.oddsEngine()
	bets = betEngine.bettingEngine(ods)
	thread = Thread(target = irc_thread,args=('oauth_token','#rellim7','spelunkybot', bets, ods))
	thread.start() # this will start the thread and continue executing the current thread
	# when the code from the 'parent' thread gets here and calls join(),
	# it will wait until the 'child' thread terminates before returning from join().


if __name__ == "__main__":
	main()
