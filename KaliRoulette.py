

from memory import Spelunker
import pandas as pd
import numpy as np
import multiprocessing as mp


import time, sqlite3, cmd

try:
	import readline
except ImportError:
	import pyreadline as readline

pd.set_option('display.max_columns', None)

PLAYER_NAME = 'bunny_funeral'



class Oracle(mp.Process):
	'''Makes predictions about future states given current state.'''
	def __init__(self,state_queue):
		super(Oracle,self).__init__()
		self.state_queue = state_queue

	def run(self):

		while True:
			last_state = self.state_queue.get()
			


class KaliState(mp.Process):

	def __init__(self,state_queue):
		super(KaliState,self).__init__()
		self.state_queue = state_queue

	def run(self):

		self.sp = Spelunker()

		self.run_columns = ['start_time','seq','player']
		self.run_columns.extend(Spelunker.ALL_ATTRIBUTES)

		self.seq = 1
		self.last_level = 0
		self.last_timer = None

		self.start_time = None
		self.mothership_trigger = None
		self.angry_shopkeeper_trigger = None

		while True:
			self.evaluate_state()
			time.sleep(1)

	def announce(self):
		state = [self.start_time,self.seq,PLAYER_NAME]
		state.extend(list(map(lambda attr: getattr(self.sp,attr),Spelunker.ALL_ATTRIBUTES)))
		self.seq += 1
		print(state)
		self.state_queue.put(state)

	def evaluate_state(self):
		sp = self.sp

		try:
			timer = sp.level_timer
			current_level = sp.level
			dead = sp.is_dead

			in_mothership = sp.lvl_mothership
			angry_keeper = sp.angry_shopkeeper

			if dead:
				if self.last_level:
					# first time death notification
					self.last_level = 0
					self.announce()
					print('In KaliState process, You have died')
			else:
				if not current_level and self.last_level == 16 or self.last_level == 20:
					# we just won!
					self.last_level = 0
					self.announce()
					print('In KaliState process, We just won!')
				elif not self.last_level and current_level > 0:
					# just started a new game
					self.start_time = int(time.time())
					self.angry_shopkeeper_trigger = False
					self.mothership_trigger = False
					self.seq = 1
					if current_level % 4 == 1: # deal with shortcuts
						self.announce()
						print('In KaliState process, New game started')
					self.last_level = current_level
					
				elif current_level > self.last_level and timer > 0:
					# just got to a new level
					self.last_level = current_level
					self.announce()
					print('In KaliState process, finished level.')
					
				elif in_mothership and current_level == 11 and not self.mothership_trigger:
					# entered the mothership, special level processing
					self.mothership_trigger = True
					self.announce()
					print('In KaliState process, entered the mothership, repeating 3-3.')
					
				elif not in_mothership and current_level == 12 and self.mothership_trigger:
					# finished the mothership, special level processing
					self.mothership_trigger = False
					self.announce()
					print('In KaliState process, exited the mothership, repeating 3-4')
					
				elif not self.angry_shopkeeper_trigger and angry_keeper:
					self.angry_shopkeeper_trigger = True
					self.announce()
					print('In KaliState process, shopkeeper is kinda pissed...')

			self.last_timer = timer

		except ValueError:
			print('\nSpelunky data collection stopped.\n')
		except AttributeError:
			print('\nSpelunky data collection stopped.\n')


				
class KaliWhisper(cmd.Cmd):
	intro = 'Welcome to the KaliRoulette shell. Type help or ? to list commands.\n'
	prompt = '(Whisper to Kali) '

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.state_queue = mp.Queue()
		self.game_state = None
		self.oracle = None

	def emptyline(self):
		pass

	def do_init(self,line):
		if self.game_state:
			print('init already called')
		else:
			self.game_state = KaliState(self.state_queue)
			self.game_state.start()
			self.oracle = Oracle(self.state_queue)
			self.oracle.start()








	
	
	

if __name__ == "__main__":
	KaliWhisper().cmdloop()

