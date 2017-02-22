
from win32com.client import GetObject
import ctypes as c
from ctypes import wintypes
from copy import copy
from collections import UserDict
from functools import partial
import win32api, win32con, struct, binascii, win32, sys, time, math, logging

class MEMORY_BASIC_INFORMATION(c.Structure):

	_fields_ = [ ("BaseAddress",  c.c_ulong),
			("AllocationBase", c.c_ulong),
			("AllocationProtect", c.c_long),
			("RegionSize", c.c_long),
			("State", c.c_long),
			("Protect", c.c_long),
			("Type", c.c_long)    ]

class MEMORY_BASIC_INFORMATION64(c.Structure):

	_fields_ = [ ("BaseAddress",  c.c_ulonglong),
			("AllocationBase", c.c_ulonglong),
			("AllocationProtect", c.c_long),
			("__alignment1", c.c_long),
			("RegionSize", c.c_longlong),
			("State", c.c_long),
			("Protect", c.c_long),
			("Type", c.c_long),
			("__alignment2", c.c_long)]

class TimeInfo(c.Structure):

	_fields_ = [ ("minutes",  c.c_uint),
			("seconds", c.c_uint),
			("milliseconds", c.c_double)]

	def total_ms(self):
		return self.milliseconds + self.seconds*1000 + self.minutes*60*1000
	

# this probably isn't kosher.
IS_64BIT = sys.maxsize > 2**32
if IS_64BIT:
	MBI = MEMORY_BASIC_INFORMATION64
else:
	MBI = MEMORY_BASIC_INFORMATION

def debug_byte_array(buf):
	str_out = []
	if len(buf) < 8:
		print(':'.join('{:02x}'.format(x) for x in buf))
		return
	for i in range(0,math.floor(len(buf)/8)):
		str_out.append(':'.join('{:02x}'.format(x) for x in buf[i*8:min((i+1)*8,len(buf))]))
		if len(str_out) >= 40:
			result = '\n'.join(str_out)
			print(result)
			str_out = []
	if len(str_out) > 0:
		result = '\n'.join(str_out)
		print(result)

# we check memory and see if it's been 'commited' by the spelunky process
def VirtualQueryEx(handle, addr):
	mbi = MBI()
	mbi_pointer = c.byref(mbi)
	mbi_size = c.sizeof(mbi)

	return mbi if c.windll.kernel32.VirtualQueryEx(handle, addr, mbi_pointer, mbi_size) else None

# read memory into an arbitrary sized char array 
def ReadProcessMemory_array(handle, addr, buffer_size):
	data = c.create_string_buffer(buffer_size)

	if IS_64BIT:
		count = c.c_ulonglong(0)
	else:
		count = c.c_ulong(0)

	return data if c.windll.kernel32.ReadProcessMemory(handle, c.c_void_p(addr), data, buffer_size, c.byref(count)) else None

# read memory into a specific c type
def ReadProcessMemory_ctype(handle, addr, buffer_type):
	data = buffer_type()

	if IS_64BIT:
		count = c.c_ulonglong(0)
	else:
		count = c.c_ulong(0)

	return data if c.windll.kernel32.ReadProcessMemory(handle, c.c_void_p(addr), c.byref(data), c.sizeof(data), c.byref(count)) else None

# get the base addr of a handle
def GetModuleBase(handle):
	hModule = c.c_ulong()
	if IS_64BIT:
		count = c.c_ulonglong(0)
	else:
		count = c.c_ulong(0)

	# if anyone has any clue at all on how to get this to work in a 64-bit python i'm all ears.
	# hell, the Ex version of this call is DESIGNED for 64-bit.
	if not c.windll.psapi.EnumProcessModulesEx(handle, c.byref(hModule), c.sizeof(hModule), c.byref(count),0x1):
		raise RuntimeError('EnumProcessModules returned error code {}'.format(c.GetLastError()))
	return hModule.value

# takes a ctypes string buffer (as created by ReadProcessMemory_array).
# the __contains__ definition allows one to check if a Signature
# object (defined below) is 'in' it 
class Buffer:

	def __init__(self, buf):

		self.buf = buf.raw

	def __contains__(self, sig):
		m = sig.mask
		s = sig.sig

		if len(m) > len(self.buf):
			return False
		for i in range(len(self.buf) - len(m)):
			for j in range(len(m)):
				if m[j] == 'x' and self.buf[i+j] == s[j]:
					if j == len(m) - 1:
						sig.offset = i
						return True
				elif m[j] != '.':
					break
				else:
					if j == len(m) - 1:
						sig.offset = i
						return True
		return False

# nothing too complicated
class Signature:

	def __init__(self,name,mask,sig):

		self.name = name
		self.mask = mask
		self.sig = sig

		self.base_addr = None
		self.offset = None

	def addr(self):
		return self.base_addr + self.offset

# UserDict allows dictionary assignment to self,
# and allows instances of SpelunkySignatures to 
# behave as a dictionary.
class SpelunkySignatures(UserDict):

	def __init__(self,sp):
		UserDict.__init__(self)

		names = ['game_state',
			 'timer',
			 'gold_count_offset_ptr',
			 'player_container',
			 'pent_container',
			 'game_container',
			 'level_offset_container',
			 'ctrl_size',
			 'run_switch',
			 'menu_ptr',
			 'game_state_ptr',
			 'lvl_worm',
			 'lvl_black_market',
			 'lvl_hmansion',
			 'lvl_yeti',
			 'lvl_cog',
			 'lvl_mothership',
			 'lvl_dark']

		masks = ['xxxxxxxx.xx.xx.xxxxxx.x',
			 'xxx.....xxxxx.x.x.....x',
			 'xx....xx.xx....xx....xx....xx....',
			 'x.x.x......xxxxx......x......x',
			 'x.....x.x.x......x.x....x',
			 'x..x..x..x....x....x.....x',
			 '.xxxxx.....x.....x.x',
			 'x...x..x.....x.x.x',
			 'x..x.x.....x......x.x.x',
			 'x.....x.x.x.....x.x',
			 'xxxxxxxx.xx.xx.xxxxxx.x',
			 'x....x......x.x...x.x.x',
			 'x.x......x.x...x.x.x',
			 'x.x......x.x.x...x.x.x',
			 'x.x......x.x....x.x.x',
			 'x......x.x.x..x',
			 'x....x......x.x....x.x.x.x',
			 'x.....xx.x.x....x.x.x']

		sigs = [[ 0xBB, 0x0F, 0x00, 0x00, 0x00, 0x3B, 0xC3, 0x75,
			0xFF, 0x8B, 0x7E, 0xFF, 0xC7, 0x46, 0xFF, 0x1B,
			0x00, 0x00, 0x00, 0x89, 0x5E, 0xFF, 0xE8],
		      [ 0xD8, 0xC2, 0xDD, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
			0xD8, 0xD9, 0xDF, 0xE0, 0x84, 0xFF, 0x75, 0xFF,
			0xDD, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x01],
		      [ 0x8B, 0x97, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x50,
			0xFF, 0x8B, 0x87, 0xFF, 0xFF, 0xFF, 0xFF, 0x8B,
			0x0D, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x81, 0xFF,
			0xFF, 0xFF, 0xFF, 0x8B, 0x83, 0x00, 0x00, 0x00,
			0x00 ],
		      [ 0x33, 0xCC, 0x8B, 0xCC, 0x69, 0xCC, 0xAA, 0xAA,
			0xAA, 0xAA, 0xCC, 0x04, 0x00, 0x00, 0x00, 0x89,
			0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0x89, 0xCC,
			0xCC, 0xAA, 0xAA, 0xAA, 0xAA, 0x89],
		      [ 0x8B, 0xCC, 0xAA, 0xAA, 0xAA, 0xAA, 0x85, 0xCC,
			0x74, 0xCC, 0x80, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
			0xCC, 0x74, 0xCC, 0xC6, 0xCC, 0xCC, 0xCC, 0xCC,
			0x80 ],
		      [ 0x8B, 0xCC, 0xCC, 0x8D, 0xCC, 0xCC, 0x8D, 0xCC,
			0xCC, 0xBF, 0xCC, 0xCC, 0xCC, 0xCC, 0xE8, 0xCC,
			0xCC, 0xCC, 0xCC, 0x8B, 0xCC, 0xAA, 0xAA, 0xAA,
			0xAA, 0x80], 
		      [ 0xCC, 0x01, 0x00, 0x00, 0x00, 0x01, 0xCC, 0xAA,
			0xAA, 0xAA, 0xAA, 0x38, 0xCC, 0xCC, 0xCC, 0xCC, 
			0xCC, 0x74, 0xCC, 0x88],
		      [ 0x89, 0xFF, 0xFF, 0xFF, 0x8D, 0xFF, 0xFF ,0x69,
		        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x33, 0xFF, 0x8B,
			0xFF, 0x89],
		      [ 0x83, 0xFF, 0xFF, 0x75, 0xFF, 0x8B, 0xFF, 0xFF,
			0xFF, 0xFF, 0xFF, 0x8D, 0xFF, 0xFF, 0xFF, 0xFF,
			0xFF, 0xFF, 0x33, 0xFF, 0x39, 0xFF, 0x0F],
		      [ 0x8b, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0x85, 0xaa,
			0x74, 0xAA, 0x89, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
			0xEB, 0xAA, 0x83], 
		      [ 0xBB, 0x0F, 0x00, 0x00, 0x00, 0x3B, 0xC3, 0x75,
			0xFF, 0x8B, 0x7E, 0xFF, 0xC7, 0x46, 0xFF, 0x1B,
			0x00, 0x00, 0x00, 0x89, 0x5E, 0xFF, 0xE8],
		      [ 0xE9, 0xCC, 0xCC, 0xCC, 0xCC, 0x80, 0xCC, 0xCC,
			0xCC, 0xCC, 0xCC, 0xCC, 0x74, 0xCC, 0x8D, 0xCC,
			0xCC, 0xCC, 0x8B, 0xCC, 0x8B, 0xCC, 0xE8],
		      [ 0x7F, 0xCC, 0x80, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
			0xCC, 0x74, 0xCC, 0x8D, 0xCC, 0xCC, 0xCC, 0x8B,
			0xCC, 0x8B, 0xCC, 0xE8],
		      [ 0x7F, 0xCC, 0x80, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
			0xCC, 0x74, 0xCC, 0x8B, 0xCC, 0x8D, 0xCC, 0xCC,
			0xCC, 0x8B, 0xCC, 0x8B, 0xCC, 0xE8],
		      [ 0x74, 0xCC, 0x80, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
			0xCC, 0x74, 0xCC, 0x8D, 0xCC, 0xCC, 0xCC, 0xCC,
			0x8B, 0xCC, 0x8B, 0xCC, 0x8B],
		      [ 0x80, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0x74,
			0xCC, 0x33, 0xCC, 0x83, 0xCC, 0xCC, 0x0F],
		      [ 0xE9, 0xCC, 0xCC, 0xCC, 0xCC, 0x80, 0xCC, 0xCC,
			0xCC, 0xCC, 0xCC, 0xCC, 0x74, 0xCC, 0x8D, 0xCC,
			0xCC, 0xCC, 0xCC, 0x8B, 0xCC, 0x8B, 0xCC, 0x8B,
			0xCC, 0xE8],
		      [ 0x80, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0x00, 0x74,
			0xCC, 0x8B, 0xCC, 0xE8, 0xCC, 0xCC, 0xCC, 0xCC,
			0x84, 0xCC, 0x74, 0xCC, 0x6A]]

		if len(masks) != len(names) or len(names) != len(sigs):
			raise RuntimeError('signature data not all the same length.')
		for i in range(len(names)):
			if len(masks[i]) != len(sigs[i]):
				raise RuntimeError('Non-matching mask/sig pairs defined in Signatures at index {}'.format(i))

		self._scan_memory(sp, list(map(lambda x: Signature(*x),zip(names,masks,sigs))))
		self._setup_hooks(sp)

	# scans for valid memory with VirtualQueryEx, then takes every block of 
	# valid memory and checks for each signature in 4096 sized chunks.
	# stops when they've all been found.
	def _scan_memory(self, sp, signatures):

		BUF_SCAN_SIZE = 4096

		# spelunky_base from GetModuleBase
		current_addr = sp.spelunky_base

		found_sigs = []

		# what's the max memory range here?
		while(current_addr < 0x7FFFFFFF):
			mbi = VirtualQueryEx(sp.handle, current_addr)
			if not mbi:
				raise RuntimeError('VirtualQueryEx returned error code {}'.format(c.GetLastError()))
			end = mbi.BaseAddress + mbi.RegionSize
			remainder = end - current_addr
			if remainder > BUF_SCAN_SIZE:
				remainder = BUF_SCAN_SIZE

			# MEM_COMMIT == 0x00001000
			if mbi.State == 0x00001000:
				buf = ReadProcessMemory_array(sp.handle, current_addr, remainder)
				if not buf:
					current_addr += remainder
					continue
				buf = Buffer(buf)
				not_found_sigs = []
				while len(signatures) > 0:
					s = signatures.pop()
					# look at Buffer's __contains__
					if s in buf:
						s.base_addr = current_addr
						found_sigs.append(s)
					else:
						not_found_sigs.append(s)

				signatures.extend(not_found_sigs)
			if len(signatures) == 0:
				break

			current_addr += remainder

		if len(signatures) > 0:
			raise RuntimeError('Could not find all signatures in memory.')
		signatures = found_sigs

		# replace each Signature object with an address
		for s in signatures:
			self[s.name] = s.base_addr+s.offset

	# use the memory addresses found in _scan_memory to wrangle some pointers and addresses we're interested in.
	# the naming scheme for the dictonary entries is important; if they don't match the pattern *_offset_uint,
	# *_offset_char or *_offset_short they will be ignored by Spelunker (the class that owns SpelunkySignatures).
	def _setup_hooks(self, sp):
		self['current_game_ptr'] = ReadProcessMemory_ctype(sp.handle, self['game_container']+21, c.c_ulong).value
		self['current_game_offset_uint'] = ReadProcessMemory_ctype(sp.handle, self['current_game_ptr'], c.c_ulong).value

		self['gold_count_offset_int'] = ReadProcessMemory_ctype(sp.handle, self['gold_count_offset_ptr']+0x17,c.c_ulong).value

		player_container = self['player_container']

		# setting player_ss to zero means we're one player only. the rest of the code omits player_ss as a simplification
		#player_ss = ReadProcessMemory_ctype(sp.handle, player_container+6, c.c_ulong).value
		#player_ss = 0
		#self['player_struct_size'] = player_ss

		# why is one offset always size 7 off the next instead of size 8?
		self['health_offset_uint'] = ReadProcessMemory_ctype(sp.handle, player_container+32, c.c_uint).value
		self['bombs_offset_uint'] = ReadProcessMemory_ctype(sp.handle, player_container+39, c.c_uint).value
		self['ropes_offset_uint'] = ReadProcessMemory_ctype(sp.handle, player_container+46, c.c_uint).value
		self['level_offset_uint'] = ReadProcessMemory_ctype(sp.handle, self['level_offset_container']+7, c.c_uint).value
		
		self['game_timer_offset_TimeInfo'] = ReadProcessMemory_ctype(sp.handle, self['timer']+4, c.c_uint).value
		self['game_timer_offset_TimeInfo'] = self['game_timer_offset_TimeInfo'] - 8
		self['level_timer_offset_TimeInfo'] = self['game_timer_offset_TimeInfo'] + 16

		self['lvl_dark_offset_char'] = ReadProcessMemory_ctype(sp.handle, self['lvl_dark']+2, c.c_uint).value
		self['lvl_worm_offset_char'] = ReadProcessMemory_ctype(sp.handle, self['lvl_worm']+7, c.c_uint).value
		self['lvl_black_market_offset_char'] = ReadProcessMemory_ctype(sp.handle, self['lvl_black_market']+4, c.c_uint).value
		self['lvl_hmansion_offset_char'] = ReadProcessMemory_ctype(sp.handle, self['lvl_hmansion']+4, c.c_uint).value
		self['lvl_yeti_offset_char'] = ReadProcessMemory_ctype(sp.handle, self['lvl_yeti']+4, c.c_uint).value
		self['lvl_cog_offset_char'] = ReadProcessMemory_ctype(sp.handle, self['lvl_cog']+2, c.c_uint).value
		self['lvl_mothership_offset_char'] = ReadProcessMemory_ctype(sp.handle, self['lvl_mothership']+7, c.c_uint).value

		# the rest is what i'm calling 'original research'. i'm finding offsets of 
		# interest from offsets calculated by the signature method because i don't quite know what i'm doing.
		# ideally i'd be able to figure out how to get memory signatures for each of these myself,
		# but i don't at present.

		self['favour_offset_int'] = self['ropes_offset_uint']+0x5288

		self['is_dead_offset_char'] = int(ReadProcessMemory_ctype(sp.handle, self['level_offset_container']+7, c.c_uint).value)
		self['is_dead_offset_char'] = self['is_dead_offset_char'] - 6
		self['killed_by_offset_uint'] = self['is_dead_offset_char'] + 0x52

		# lunkybox has the pointers/offsets from game.exe and i could have used them directly,
		# but this ended up taking less work. 
		self['has_compass_offset_char'] = self['ropes_offset_uint']+0x5C
		self['has_parachute_offset_char'] = self['ropes_offset_uint']+0x5D
		self['has_jetpack_offset_char'] = self['ropes_offset_uint']+0x5E
		self['has_climbing_gloves_offset_char'] = self['ropes_offset_uint']+0x5F
		self['has_pitchers_mitt_offset_char'] = self['ropes_offset_uint']+0x60
		self['has_spring_shoes_offset_char'] = self['ropes_offset_uint']+0x61
		self['has_spike_shoes_offset_char'] = self['ropes_offset_uint']+0x62
		self['has_spectacles_offset_char'] = self['ropes_offset_uint']+0x63
		self['has_kapala_offset_char'] = self['ropes_offset_uint']+0x64
		self['has_hedjet_offset_char'] = self['ropes_offset_uint']+0x65
		self['has_udjat_eye_offset_char'] = self['ropes_offset_uint']+0x66
		self['has_book_of_dead_offset_char'] = self['ropes_offset_uint']+0x67
		self['has_ankh_offset_char'] = self['ropes_offset_uint']+0x68
		self['has_paste_offset_char'] = self['ropes_offset_uint']+0x69
		self['has_cape_offset_char'] = self['ropes_offset_uint']+0x6A
		self['has_vlads_cape_offset_char'] = self['ropes_offset_uint']+0x6B
		self['has_crysknife_offset_char'] = self['ropes_offset_uint']+0x6C
		self['has_vlads_amulet_offset_char'] = self['ropes_offset_uint']+0x6D

		# both values seem to be 1 when he's mad on a stage. wanted to collect enough
		# data to confirm angry_shopkeeper_1 is always the same as angry_shopkeeper_2
		self['angry_shopkeeper_1_offset_char'] = self['health_offset_uint']-0x88
		self['angry_shopkeeper_2_offset_char'] = self['health_offset_uint']-0xAB

		for location,value in sorted(list(self.items()),key=lambda x: x[1]):
			logging.info(hex(int(value)),location)
			print(hex(int(value)),location)

class Spelunker:

	ALL_ATTRIBUTES = ['level',
			'is_dead',
			'killed_by',
			'health',
			'bombs',
			'ropes',
			'gold_count',
			'favour',
			'angry_shopkeeper',
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


	def __init__(self):
	

		self._set_pid()

		# these are the OpenProcess flags Frozlunky uses.
		# i kinda looked into them. seemed reasonable. i'm not sure if they'd work 
		# if we were doing a dll injection.
		self.spelunky_process = win32api.OpenProcess(win32con.PROCESS_CREATE_THREAD|
								win32con.PROCESS_QUERY_INFORMATION|
								win32con.PROCESS_SET_INFORMATION|
								win32con.PROCESS_SET_QUOTA|
								win32con.PROCESS_TERMINATE|
								win32con.PROCESS_VM_OPERATION|
								win32con.PROCESS_VM_READ|
								win32con.PROCESS_VM_WRITE,
								True,self.pid)
		self.handle = self.spelunky_process.handle

		# this doesn't work in 64 bit and i have no idea why. help!
		self.spelunky_base = GetModuleBase(self.handle)

		if not self.spelunky_process:
			raise RuntimeError('Couldn\'t open the spelunky process.')

		self.mem = SpelunkySignatures(self)

		# this is set for convienence
		self.current_game = self.mem['current_game_offset_uint']
		
		# goes through the memory dictionary looking for names matching
		# *_offset_uint, *_offset_int, *_offset_char and *_offset_short. seperates matching
		# names into their respective lists. 
		self.offset_uint = list(
					filter(lambda z: len(z) > 0,
					map(lambda y: y[:len(y) - len('_offset_uint')],
					filter(lambda x: x.endswith('_offset_uint'),
					self.mem.keys()))))
					
		self.offset_int = list(
					filter(lambda z: len(z) > 0,
					map(lambda y: y[:len(y) - len('_offset_int')],
					filter(lambda x: x.endswith('_offset_int'),
					self.mem.keys()))))

		self.offset_char = list(
					filter(lambda z: len(z) > 0,
					map(lambda y: y[:len(y) - len('_offset_char')],
					filter(lambda x: x.endswith('_offset_char'),
					self.mem.keys()))))
		self.offset_short = list(
					filter(lambda z: len(z) > 0,
					map(lambda y: y[:len(y) - len('_offset_short')],
					filter(lambda x: x.endswith('_offset_short'),
					self.mem.keys()))))

		# sets self.alt_attributes so that each name in self.offset_uint,
		# self.offset_char and self.offset_short is a key. the value of each
		# key is a partially applied function of self.read_uint, self.read_short
		# or self.read_char.
		self.alt_attributes = {}
		for k in self.offset_uint:
			self.alt_attributes[k] = partial(self.read_uint,name=k+'_offset_uint')
		for k in self.offset_int:
			self.alt_attributes[k] = partial(self.read_int,name=k+'_offset_int')
		for k in self.offset_char:
			self.alt_attributes[k] = partial(self.read_char,name=k+'_offset_char')
		for k in self.offset_short:
			self.alt_attributes[k] = partial(self.read_short,name=k+'_offset_short')

	# for a Spelunker instance sp, this allows us to access the value of memories of interest
	# via sp's attributes. it's easier shown by example:
	# sp.health will call read_uint with name argument 'health_offset_uint', which will return 
	# the health read from game.
	# if the name of the memory defined in SpelunkySignatures matched one of the *_offset_*
	# labels, the sp object will automatically have that name as an attribute.
	def __getattr__(self,name):
		try:
			return self.alt_attributes[name]()
		except KeyError:
			msg = "'{0}' object has no attribute '{1}'"
			raise AttributeError(msg.format(type(self).__name__, name))

	# read and return a uint from the specificed named memory location
	def read_uint(self,name):
		return ReadProcessMemory_ctype(self.handle,self.current_game+self.mem[name],c.c_uint).value
		
	# read and return an int from the specificed named memory location
	def read_int(self,name):
		return ReadProcessMemory_ctype(self.handle,self.current_game+self.mem[name],c.c_int).value
			
	# read and return a short from the specificed named memory location
	def read_short(self,name):
		return ReadProcessMemory_ctype(self.handle,self.current_game+self.mem[name],c.c_short).value
	
	# read and return a byte from the specificed named memory location
	def read_char(self,name):
		ch = ReadProcessMemory_ctype(self.handle,self.current_game+self.mem[name],c.c_char).value
		return int.from_bytes(ch,byteorder='little')
	
	# read a TimeInfo struct from game addr + timer_offset_TimeInfo
	@property
	def game_timer(self):
		t = ReadProcessMemory_ctype(self.handle,self.current_game+self.mem['game_timer_offset_TimeInfo'],TimeInfo)
		return t.total_ms()

	# read a TimeInfo struct from game addr + timer_offset_TimeInfo
	@property
	def level_timer(self):
		t = ReadProcessMemory_ctype(self.handle,self.current_game+self.mem['level_timer_offset_TimeInfo'],TimeInfo)
		return t.total_ms()
		
	@property
	def angry_shopkeeper(self):
		return self.angry_shopkeeper_2 or self.angry_shopkeeper_1

	# enumerate all processes to find spelunky.exe and set self.pid
	def _set_pid(self):

		WMI = GetObject('winmgmts:')
		processes = WMI.InstancesOf('Win32_Process')
		spelunky_candidates = list(
					filter(lambda x: x[1].lower() == 'spelunky.exe',
					map(lambda p: (p.Properties_('ProcessID').Value, p.Properties_('Name').Value), processes)))

		if len(spelunky_candidates) == 0:
			raise RuntimeError('No active Spelunky process found.')
		if len(spelunky_candidates) > 1:
			raise RuntimeError('More than one active Spelunky process found.')
		else:
			self.pid = spelunky_candidates[0][0]
			
