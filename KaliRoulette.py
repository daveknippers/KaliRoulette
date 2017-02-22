

from memory import Spelunker
import pandas as pd
import numpy as np
import multiprocessing as mp


import time, sqlite3, cmd, logging

try:
	import readline
except ImportError:
	import pyreadline as readline
	
import tkinter as tk
import tkinter.scrolledtext as ScrolledText

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

		logging.info('Initializing KaliState...')
		while True:
			self.evaluate_state()
			time.sleep(1)

	def announce(self):
		state = [self.start_time,self.seq,PLAYER_NAME]
		state.extend(list(map(lambda attr: getattr(self.sp,attr),Spelunker.ALL_ATTRIBUTES)))
		self.seq += 1
		logging.info(state)
		self.state_queue.put(state)

	def evaluate_state(self):
		sp = self.sp

		try:
			timer = sp.level_timer
			current_level = sp.level
			dead = sp.is_dead

			in_mothership = sp.lvl_mothership
			angry_keeper = sp.angry_shopkeeper

			logging.info(self.last_level,self.seq)

			if dead:
				if self.last_level:
					# first time death notification
					self.last_level = 0
					self.announce()
					logging.info('In KaliState process, You have died')
			else:
				if not current_level and (self.last_level == 16 or self.last_level == 20):
					# we just won!
					self.last_level = 0
					self.announce()
					logging.info('In KaliState process, We just won!')
				elif not self.last_level and current_level >= 0 and self.seq > 1:
					# just started a new game
					self.start_time = int(time.time())
					self.angry_shopkeeper_trigger = False
					self.mothership_trigger = False
					self.seq = 1
					self.last_level = current_level
					logging.info('In KaliState process, cleansing our state')
					if current_level % 4 == 1: # deal with shortcuts
						self.announce()
						logging.info('In KaliState process, New game started')
					
				elif current_level > self.last_level:
					# just got to a new level
					self.last_level = current_level
					if self.seq == 1 and current_level % 4 == 1:
						logging.info('In KaliState process, New game started')
						self.announce()
					elif self.seq == 1:
						pass
					else:
						logging.info('In KaliState process, Level Finished')
						self.announce()
				elif in_mothership and current_level == 11 and not self.mothership_trigger:
					# entered the mothership, special level processing
					self.mothership_trigger = True
					self.announce()
					logging.info('In KaliState process, entered the mothership, repeating 3-3.')
					
				elif not in_mothership and current_level == 12 and self.mothership_trigger:
					# finished the mothership, special level processing
					self.mothership_trigger = False
					self.announce()
					logging.info('In KaliState process, exited the mothership, repeating 3-4')
					
				elif not self.angry_shopkeeper_trigger and angry_keeper:
					self.angry_shopkeeper_trigger = True
					self.announce()
					logging.info('In KaliState process, shopkeeper is kinda pissed...')

			self.last_timer = timer

		except ValueError:
			logging.info('\nSpelunky data collection stopped.\n')
		except AttributeError:
			logging.info('\nSpelunky data collection stopped.\n')

class KaliWhisper(cmd.Cmd):
	intro = 'Welcome to the KaliRoulette shell. Type help or ? to list commands.\n'
	prompt = '(Whisper to Kali) '

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.state_queue = mp.Queue()
		self.logging_process = mp.Process(target=WindowLogging, args=())
		self.logging_process.start()
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

class TKLogging(tk.Frame):
	'''http://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget'''

	def __init__(self, parent, *args, **kwargs):
			tk.Frame.__init__(self, parent, *args, **kwargs)
			self.root = parent
			self.build_gui()
		
	# Build GUI
	def build_gui(self):                    
		self.root.title('KaliState logger')
		self.root.option_add('*tearOff', 'FALSE')
		self.grid(column=0, row=0, sticky='ew')
		self.grid_columnconfigure(0, weight=1, uniform='a')
		self.grid_columnconfigure(1, weight=1, uniform='a')
		self.grid_columnconfigure(2, weight=1, uniform='a')
		self.grid_columnconfigure(3, weight=1, uniform='a')

		# Add text widget to display logging info
		st = ScrolledText.ScrolledText(self, state='disabled')
		st.configure(font='TkFixedFont')
		st.grid(column=0, row=1, sticky='w', columnspan=4)

		# Create textLogger
		text_handler = TextHandler(st)

		# Logging configuration
		logging.basicConfig(filename='test.log',
				level=logging.INFO, 
				format='%(asctime)s - %(levelname)s - %(message)s')        

		# Add the handler to logger
		logger = logging.getLogger()   
		logger.addHandler(text_handler)

class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(Tkinter.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(Tkinter.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

		
def WindowLogging():
	root = tk.Tk()
	tk_logging = TKLogging(root)
	root.mainloop()

			
if __name__ == "__main__":
	KaliWhisper().cmdloop()

