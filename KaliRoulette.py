

from memory import Spelunker
import pandas as pd
import numpy as np
import multiprocessing as mp

import time
import sqlite3
import cmd
import readline

pd.set_option('display.max_columns', None)

PLAYER_NAME = 'bunny_funeral'

class Oracle:
	'''Makes predictions about future states given current state.'''
	def __init__(self):
		pass

	def store_game_over(entire_run_df):
		pass


class KaliState:

	def __init__(self):

		self.sp = Spelunker()

		#sql_engine = sqlite3.connect(db_file)

		self.run_columns = ['start_time','seq','player']
		self.run_columns.extend(Spelunker.ALL_ATTRIBUTES)
		self.last_level = 0
		self.last_timer = self.sp.level_timer

		self.angry_keeper_trigger = False
		self.mothership_trigger = False
		self.informed = False

		self.start_time = int(time.time())

		self.current_run = []


	def evaluate_state(self):
		try:
			

		except ValueError:
			print('\nSpelunky data collection stopped.\n')
		except AttributeError:
			print('\nSpelunky data collection stopped.\n')


		timer = sp.level_timer
		current_level = sp.level
		dead = sp.is_dead

		in_mothership = sp.lvl_mothership
		angry_keeper = sp.angry_shopkeeper

		if dead:
			if self.last_level:
				# first time death notification
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				dc_df = pd.DataFrame(current_run,columns=run_columns)
				dc_df.to_sql('run_states',sql_engine,if_exists='append',index=False)
				last_level = 0
				current_run = []

				print('You have died. This is what\'s being saved in the database:')
				print(dc_df)
		else:
			if not last_level and current_level > 0:
				# just started a new game
				start_time = int(time.time())
				angry_keeper_trigger = False
				mothership_trigger = False
				seq = 1
				if current_level % 4: # deal with shortcuts
					state,seq = produce_state(start_time,seq,sp)
					current_run.append(state)
				last_level = current_level
				print('New game started')
				
			elif current_level > last_level and timer > 0:
				# just got to a new level
				last_level = current_level
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				print('Finished level.')
				
			elif in_mothership and current_level == 11 and not mothership_trigger:
				# entered the mothership, special level processing
				mothership_trigger = True
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				print('Entered the mothership, repeating 3-3.')
				
			elif not in_mothership and current_level == 12 and mothership_trigger:
				# finished the mothership, special level processing
				mothership_trigger = False
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				print('Exited the mothership, repeating 3-4')
				
			elif not angry_keeper_trigger and angry_keeper:
				angry_keeper_trigger = True
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				print('Shopkeeper is kinda pissed...')

		self.last_timer = timer
				
			

class KaliWhisper(cmd.Cmd):
	intro = 'Welcome to the KaliRoulette shell. Type help or ? to list commands.\n'
	prompt = '(Whisper to Kali) '

	def do_init(
		self.gs = KaliState()







def produce_state(start_time, seq, sp):
	state = [start_time,seq,PLAYER_NAME]
	state.extend(list(map(lambda attr: getattr(sp,attr),Spelunker.ALL_ATTRIBUTES)))
	return state,seq+1
	
	
	
def KaliRoulette(db_file='KaliRoulette.db'):
	
	

	

if __name__ == "__main__":
	KaliWhisper().cmdloop()

