
import time, argparse, os, sys
import pandas as pd
import irc.bot


from oauth_token import oauth_token
from memory import Spelunker

from sqlalchemy import create_engine
from threading import Lock, Timer, Thread


class Bookie(Thread):

	def __init__(self,death_map,streamer_name):
		Thread.__init__(self)

		self.death_map = death_map
		self.streamer_name = streamer_name

		def run(self):

			if not os.path.exists('KaliRoulette.db'):
				print('No Kali Roulette database exists. Creating {}'.format('KaliRoulette.db'))
				sqlite_db = create_engine('sqlite:///KaliRoulette.db',echo=False)
				init_entry = [(streamer_name,1000)]
				bet_ledger_df = pd.DataFrame(init_entry,columns=['nickname','salt'])
				bet_ledger_df.to_sql('bet_ledger',sqlite_db,index=False)
			else: 
				sqlite_db = create_engine('sqlite:///KaliRoulette.db',echo=False)

			while True:


class KaliBot(irc.bot.SingleServerIRCBot):

	def __init__(self, server, channel, streamer_name, nickname):
		irc.bot.SingleServerIRCBot.__init__(self, [server], nickname, nickname)

		if not os.path.exists('death_types.csv'):
			raise ValueError('death_types.csv not found, cannot continue.')

		self.death_types_df = pd.read_csv('death_types.csv',index_col=False,
				names=['death_id','internal_death_name','death_name','death_reason'],
				dtype={'death_id':int,'internal_death_name':str,'death_name':str, 'death_reason':str})

		self.death_reason_map = {}
		for (k,v) in self.death_types_df[['death_id','death_reason']].values:
			self.death_reason_map[k] = v

		self.death_map = {}
		for (k,v) in self.death_types_df[['death_id','death_name']].values:
			self.death_map[k] = v
		
		self.bookie = Bookie(self.death_map,streamer_name)
		self.bookie.start()
		sys.exit()

		self.channel = channel
		self.sp = Spelunker()

		self.enable_bets = False
		
		self.timer = self.sp.game_timer
		self.level = self.sp.level
		self.is_dead = self.sp.is_dead
		self.angry_shopkeeper = self.sp.angry_shopkeeper
		self.has_ankh  = self.sp.has_ankh
		self.killed_by = self.sp.killed_by
		
		self.show_pause = True
		self.lock = Lock()

		self.bookie = Bookie(self.death_map)
		self.bookie.start()

		self.reactor.scheduler.execute_every(2,self.process_spelunker)

	def process_spelunker(self):
		self.lock.acquire()

		sp = self.sp
		current_timer = sp.game_timer
		current_level = sp.level
		current_is_dead = sp.is_dead
		current_has_ankh = sp.has_ankh
		current_angry_shopkeeper = sp.angry_shopkeeper
		current_killed_by = sp.killed_by

		if self.has_ankh and not current_has_ankh:
			self.send_pub_message('Good thing I have the Ankh.')
		if not self.angry_shopkeeper and current_angry_shopkeeper:
			self.send_pub_message('Always bet on the shopkeeper.')

		if not self.is_dead and current_is_dead:
			cause = self.death_map[current_killed_by]
			explanation = self.death_reason_map[current_killed_by]
			n_bets,n_winners = self.process_payouts(cause)

			compose_message = 'Streamer has found the sweet release of death.'
			compose_message += ' They were {}'.format(explanation)
			self.send_pub_message(compose_message)

			if n_bets > 0:
				compose_message += ' They were {} There were {} bet(s) total and {} winning bet(s).'.format(explanation,n_bets,n_winners)
			else:
				pass


		elif not current_is_dead:
			if self.timer == current_timer:
				if current_level == 0 and (self.level == 16 or self.level == 20):
					self.send_pub_message("Streamer has won! Your bets are now forfeit.")
					self.process_payouts(None)
				elif self.enable_bets == False and self.show_pause:
					self.send_pub_message('Game paused, betting is available for the next 30 seconds.')
					self.enable_bets = True
					self.show_pause = False
					Timer(30,self.end_betting).start()
			else:
				self.show_pause = True
		
		self.timer = current_timer
		self.is_dead = current_is_dead
		self.level = current_level
		self.has_ankh = current_has_ankh
		self.angry_shopkeeper = current_angry_shopkeeper
		self.killed_by = current_killed_by
		
		self.lock.release()

	def process_payouts(self,cause):
		if cause is None:
			pass
		
	def make_bet(self, user, amount, cause):
		pass


	def end_betting(self):
		self.lock.acquire()

		self.send_pub_message('Betting has ended.')
		self.enable_bets = False

		self.lock.release()

	def send_message(self, message, user):
		self.connection.privmsg(self.channel,'/w {} {}'.format(user,message))
		
	def send_pub_message(self, message):
		self.connection.privmsg(self.channel, message)
			
	def on_pubmsg(self, c, e):
		msg = e.arguments[0].split("!", 1)[1:][0]
		if len(msg) > 0:
			self.do_command(msg,e)

	def on_whisper(self, c, e):
		self.on_pubmsg(c,e)

	def on_welcome(self, c, e):
		print('joining {}'.format(self.channel))
		c.send_raw("CAP REQ :twitch.tv/commands")
		c.join(self.channel)
		c.set_rate_limit(100/30)

	def do_command(self,msg,meta):
		user = meta.source.split("!")[0]
		msg = msg.strip().split()
		if len(msg) == 0:
			return

		command = msg[0]

		if command == 'help':
			self.send_message('Available commands: !bet amount death_cause, !balance',user)

		if command == 'bet':
			self.lock.acquire()
			if self.enable_bets:
				if len(msg) != 3:
					reason = "Invalid betting parameters. Try !bet amount death_cause. The causes can be found on bunny_funeral's channel panels."
					self.send_message(user,reason)
				else:
					amount = msg[1]
					try:
						amount = int(amount)
						if amount < 1:
							raise ValueError()
					except ValueError:
						reason = 'Invalid betting amount. Please enter a positive whole number.'
						self.send_message(user,reason)
						amount = None

					if amount is not None:
						if len(msg[2]) == 0:
							reason = "Please enter a valid death reason. The causes can be found in bunny_funeral's channel panels."
							self.send_message(user,reason)
						else:
							response = self.make_bet(user,amount,cause)
							self.send_message(user,response)
			else:
				self.send_message('Betting is currently disallowed. Please wait for the game to pause.',user)
			self.lock.release()
		
		if command == 'balance':
				response = self.get_balance(user)
				self.send_message(user,response)


	def get_balance(self,user):
		pass

def KaliRoulette(streamer_name, bot_name):

	server = irc.bot.ServerSpec('irc.twitch.tv', port=6667, password=oauth_token)
	bot = KaliBot(server, '#{}'.format(streamer_name), streamer_name, bot_name)
	bot.start()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Start the Kali Roulette memory reader/IRC bot')
	parser.add_argument('-s', '--streamer', dest='streamer', type=str, help='your twitch username')
	parser.add_argument('-b', '--bot-name', dest='bot_name', type=str, help="your bot's twitch username")
	args = parser.parse_args()
	if args.streamer is None or args.bot_name is None:
		parser.print_help()
	else:
		KaliRoulette(args.streamer,args.bot_name)
				   
