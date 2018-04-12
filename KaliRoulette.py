import pandas as pd
import irc.bot
import time

import argparse

from oauth_token import oauth_token
from memory import Spelunker

from threading import Lock, Timer

class KaliBot(irc.bot.SingleServerIRCBot):

	def __init__(self, server, channel, nickname):
		irc.bot.SingleServerIRCBot.__init__(self, [server], nickname, nickname)

		self.channel = channel
		self.sp = Spelunker()

		self.reactor.scheduler.execute_every(2,self.process_spelunker)

		self.run_columns = ['start_time','seq','player']
		self.run_columns.extend(Spelunker.ALL_ATTRIBUTES)

		self.enable_bets = False
		
		self.timer = self.sp.game_timer
		self.level = self.sp.level
		self.is_dead = self.sp.is_dead
		self.angry_shopkeeper = self.sp.angry_shopkeeper
		self.has_ankh  = self.sp.has_ankh

		self.lock = Lock()

	def process_spelunker(self):
		self.lock.acquire()

		sp = self.sp
		current_timer = sp.game_timer
		current_level = sp.level
		current_is_dead = sp.is_dead
		current_has_ankh = sp.has_ankh
		current_angry_shopkeeper = sp.angry_shopkeeper

		if self.has_ankh and not current_has_ankh:
			self.send_pub_message('Good thing I have the Ankh.')
		if not self.angry_shopkeeper and current_angry_shopkeeper:
			self.send_pub_message('Always bet on the shopkeeper.')

		if not self.is_dead and current_is_dead:
			self.send_pub_message('Streamer has found the sweet release of death.')
		elif not current_is_dead:
			if self.timer == current_timer:
				if current_level == 0 and (self.level == 16 or self.level == 20):
					self.send_pub_message('Streamer has won!')
				elif self.enable_bets == False:
					self.send_pub_message('Game paused, betting available for next 30 seconds')
					self.enable_bets = True

		
		self.timer = current_timer
		self.is_dead = current_is_dead
		self.level = current_level
		self.has_ankh = current_has_ankh
		self.angry_shopkeeper = current_angry_shopkeeper
		
		self.lock.release()

	def send_message(self, message, user):
		self.connection.privmsg(self.channel,'/w {} {}'.format(user,message))
		
	def send_pub_message(self, message):
		#self.lock.acquire()
		self.connection.privmsg(self.channel, message)
			
	def on_pubmsg(self, c, e):
		print(c,e)
		#a = e.arguments[0].split("!", 1)
		#if (len(a) > 1):
		#	print(e, a[1].strip(),a)

	def on_whisper(self, c, e):
		self.on_pubmsg(c,e)


	def on_welcome(self, c, e):
		print('joining {}'.format(self.channel))
		c.send_raw("CAP REQ :twitch.tv/commands")
		c.join(self.channel)
		c.set_rate_limit(100/30)


				   
def KaliRoulette(streamer_name):

	server = irc.bot.ServerSpec('irc.twitch.tv', port=6667, password=oauth_token)
	bot = KaliBot(server, '#{}'.format(streamer_name), 'SpelunkyBot')
	bot.start()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Start the Kali Roulette memory reader/IRC bot')
	parser.add_argument('-s', '--streamer', dest='streamer', type=str, help='your twitch username')
	args = parser.parse_args()
	if args.streamer is None:
		parser.print_help()
	else:
		KaliRoulette(args.streamer)
				   
