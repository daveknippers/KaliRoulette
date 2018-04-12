

def process_spelunker(self):
'''early in development we had grandiose ideas. we wanted
to capture and piece together the history of the game from
a bunch of snapshots of variables in the game's memory.
we eventually abandoned this idea, but if a variant of the idea
ever comes back, here's the code preserved.'''

	self.seq = 1
	self.last_level = 0

	self.start_time = None
	self.mothership_trigger = None
	self.angry_shopkeeper_trigger = None
	sp = self.sp
	self.timer_paused = None

	try:
		timer = sp.level_timer

		current_level = sp.level
		dead = sp.is_dead

		in_mothership = sp.lvl_mothership
		angry_keeper = sp.angry_shopkeeper

		if last_timer == timer and not self.timer_paused:
			self.timer_paused = True
			self.announce()
		elif last_timer != timer:
			self.announce()
			self.timer_paused = False

		if dead:
			if self.last_level:
				# first time death notification
				self.last_level = 0
				self.announce()
				print('You have died')
		else:
			if not current_level and (self.last_level == 16 or self.last_level == 20):
				# we just won!
				self.last_level = 0
				self.announce()
				print('We just won!')
			elif not self.last_level and current_level >= 0 and self.seq > 1:
				# just started a new game
				self.start_time = int(time.time())
				self.angry_shopkeeper_trigger = False
				self.mothership_trigger = False
				self.seq = 1
				self.last_level = current_level
				print('Cleansing our state')
				if current_level % 4 == 1: # deal with shortcuts
					self.announce()
					print('New game started')
				
			elif current_level > self.last_level:
				# just got to a new level
				self.last_level = current_level
				if self.seq == 1 and current_level % 4 == 1:
					print('New game started')
					self.announce()
				elif self.seq == 1:
					pass
				else:
					print('Level Finished')
					self.announce()
			elif in_mothership and current_level == 11 and not self.mothership_trigger:
				# entered the mothership, special level processing
				self.mothership_trigger = True
				#self.announce()
				print('Entered the mothership, repeating 3-3.')
				
			elif not in_mothership and current_level == 12 and self.mothership_trigger:
				# finished the mothership, special level processing
				self.mothership_trigger = False
				#self.announce()
				print('Exited the mothership, repeating 3-4')
				
			elif not self.angry_shopkeeper_trigger and angry_keeper:
				self.angry_shopkeeper_trigger = True
				#self.announce()
				print('Shopkeeper is kinda pissed...')
	except ValueError:
		print('\nSpelunky data collection stopped.\n')
	except AttributeError:
		print('\nSpelunky data collection stopped.\n')
