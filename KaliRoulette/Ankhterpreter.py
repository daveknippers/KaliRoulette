

from memory import Spelunker
import pandas as pd

import time
import sqlite3
import cmd

pd.set_option('display.max_columns', None)

# to-do: make this part of Spelunker, it's ugly here.
ALL_ATTRIBUTES = ['level',
			'is_dead',
			'killed_by',
			'health',
			'bombs',
			'ropes',
			'gold_count',
			'favour',
			'angry_shopkeeper_1',
			'angry_shopkeeper_2',
			'lvl_dark',
			'lvl_worm',
			'lvl_black_market',
			'lvl_hmansion',
			'lvl_yeti',
			'lvl_cog',
			'lvl_mothership',
			'has_compass',
			'has_parachute',
			'has_jetpack',
			'has_climbing_gloves',
			'has_pitchers_mitt',
			'has_spring_shoes',
			'has_spike_shoes',
			'has_spectacles',
			'has_kapala',
			'has_hedjet',
			'has_udjat_eye',
			'has_book_of_dead',
			'has_ankh',
			'has_paste',
			'has_cape',
			'has_vlads_cape',
			'has_crysknife',
			'has_vlads_amulet',
			'game_timer']
			
			
def produce_state(start_time, seq, sp):
	state = [start_time,seq]
	state.extend(list(map(lambda attr: getattr(sp,attr),ALL_ATTRIBUTES)))
	return state,seq+1
	

def Ankhterpreter(db_file='Ankhterpreter_2016_12_22.db'):
	
	sp = Spelunker()
	
	sql_engine = sqlite3.connect(db_file)
	run_columns = ['start_time','seq']
	run_columns.extend(ALL_ATTRIBUTES)

	last_level = 0
	angry_keeper_trigger = False
	mothership_trigger = False

	# it should never be read before it gets set in the while below,
	# but in case it is because i missed a race condition or something,
	# we're going to set it to be sure.
	start_time = int(time.time())


	current_run = []
	informed = False

	while not sp.is_dead:
		if not informed:
			print('Waiting until you\'re dead to start data collection.\n')
			informed = True
		time.sleep(1)

	print('Game over state detected. Death collection will begin next life.\n')
	
	timer = sp.level_timer
	

	try:
		while True:
			current_level = sp.level
			dead = sp.is_dead
			last_timer = timer
			timer = sp.level_timer

			in_mothership = sp.lvl_mothership
			angry_keeper = sp.angry_shopkeeper_1 or sp.angry_shopkeeper_2
						
			if dead and last_level:
				# first time death notification
				time.sleep(1) # anti-race
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				dc_df = pd.DataFrame(current_run,columns=run_columns)
				dc_df.to_sql('run_states',sql_engine,if_exists='append',index=False)
				last_level = 0
				current_run = []

				print('You have died. This is what\'s being saved in the database:')
				print(dc_df)

			elif not dead and not last_level and current_level > 0:
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
				
			elif not dead and current_level > last_level and timer > 0:
				# just got to a new level
				last_level = current_level
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				print('Finished level.')
				
			elif not dead and in_mothership and current_level == 11 and not mothership_trigger:
				# entered the mothership, special level processing
				mothership_trigger = True
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				print('Entered the mothership, repeating 3-3.')
				
			elif not dead and not in_mothership and current_level == 12 and mothership_trigger:
				# finished the mothership, special level processing
				mothership_trigger = False
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				print('Exited the mothership, repeating 3-4')
				
			if not dead and not angry_keeper_trigger and angry_keeper:
				angry_keeper_trigger = True
				state,seq = produce_state(start_time,seq,sp)
				current_run.append(state)
				print('Shopkeeper is kinda pissed...')
				
		
			time.sleep(1)
	except ValueError:
		print('\nSpelunky data collection stopped.\n')
	except AttributeError:
		print('\nSpelunky data collection stopped.\n')

	

if __name__ == "__main__":
	Ankhterpreter()

