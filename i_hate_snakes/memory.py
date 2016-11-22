
from win32com.client import GetObject
import ctypes as c
from ctypes import wintypes
from copy import copy
import win32api, win32con, struct, binascii, win32, sys, math

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


IS_64BIT = sys.maxsize > 2**32
if IS_64BIT:
	MBI = MEMORY_BASIC_INFORMATION64
else:
	MBI = MEMORY_BASIC_INFORMATION

_ReadProcessMemory = c.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
_ReadProcessMemory.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,c.c_size_t,c.POINTER(c.c_size_t)]
_ReadProcessMemory.restype = wintypes.BOOL


def debug_byte_array(buf):
	str_out = []
	for i in range(0,math.floor(len(buf)/8)):
		str_out.append(':'.join('{:02x}'.format(x) for x in buf[i*8:min((i+1)*8,len(buf))]))
		if len(str_out) >= 40:
			result = '\n'.join(str_out)
			if '22' in result:
				print(result)
				return
			str_out = []
	if len(str_out) > 0:
		result = '\n'.join(str_out)
		if '22' in result:
			print(result)



def VirtualQueryEx(handle, addr):
	mbi = MBI()
	mbi_pointer = c.byref(mbi)
	mbi_size = c.sizeof(mbi)

	return mbi if c.windll.kernel32.VirtualQueryEx(handle, addr, mbi_pointer, mbi_size) else None

def ReadProcessMemory(handle, addr, buffer_size):
	data = c.create_string_buffer(buffer_size)

	if IS_64BIT:
		count = c.c_ulonglong(0)
	else:
		count = c.c_ulong(0)

	return data if _ReadProcessMemory(handle, addr, data, buffer_size, c.byref(count)) else None

class Buffer:

	def __init__(self, buf):

		self.buf = buf.raw
		self.cursor = 0

	def __contains__(self, sig):
		m = sig.mask
		s = sig.sig
	
		if len(m) > len(self.buf):
			return False
		for i in range(len(self.buf) - len(m)):
			for j in range(len(m)):
				if m[j] == 'x' and self.buf[i+j] == s[j]:
					if j == len(m) - 1:
						sig.set_offset(i)
						return True
				elif m[j] != '.':
					break
				else:
					if j == len(m) - 1:
						sig.set_offset(i)
						return True
		m = sig.reverse_mask
		s = sig.reverse_sig

		for i in range(len(self.buf) - len(m)):
			for j in range(len(m)):
				if m[j] == 'x' and s[j] == self.buf[i+j]:
					if j == len(m) - 1:
						sig.set_offset(i)
						return True
				elif m[j] != '.':
					break
				else:
					if j == len(m) - 1:
						sig.set_offset(i)
						return True

		return False

						
class Signature:

	def __init__(self,name,mask,sig):

		self.name = name
		self.mask = mask
		self.reverse_mask = copy(mask)
		self.reverse_mask = ''.join(reversed(self.reverse_mask))
		self.sig = sig
		self.reverse_sig = copy(sig)
		self.reverse_sig.reverse()

		self.base_addr = None

	def set_offset(self, offset):
		self.offset = offset

class Signatures:

	def __init__(self,sp):

		names = ['game_state']
		''''
			 'timers',
			 'gold_count',
			 'player_data',
			 'pent_container']
		'''

		'''
		'ctrl_size',
		'run_switch_offs',
		'menu_data',
		'gfx_options',
		'level_flags',
		'entity_data']
		'''

		masks = ['xxxxxxxx.xx.xx.xxxxxx.x']


		'''
			 'xxx.....xxxxx.x.x.....x',
			 'xx....xx.xx....xx....xx....xx....',
			 'x.x.x......xxxxx......x......x',
			 'x.....x.x.x......x.x....x']
		'''
		
		sigs = [[ 0xBB, 0x0F, 0x00, 0x00, 0x00, 0x3B, 0xC3, 0x75, 
			0xFF, 0x8B, 0x7E, 0xFF, 0xC7, 0x46, 0xFF, 0x1B,
			0x00, 0x00, 0x00, 0x89, 0x5E, 0xFF, 0xE8]]

		'''
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
			0x80 ]]
		'''

		self.signatures = list(map(lambda x: Signature(*x),zip(names,masks,sigs)))
		self.search(sp)

	def search(self, sp):
		BUF_SCAN_SIZE = 4096

		current_addr = 0
		current_size = 0

		end = 10*1024*1024 # 10 mb

		while(current_addr < 0x7FFFFFFF):
			mbi = VirtualQueryEx(sp.handle, current_addr)
			if not mbi:
				print('handle:',sp.handle)
				print('region:', current_addr)
				raise RuntimeError('VirtualQueryEx returned error code {}'.format(c.GetLastError()))
			end = mbi.BaseAddress + mbi.RegionSize
			remainder = end - current_addr
			if remainder > BUF_SCAN_SIZE:
				remainder = BUF_SCAN_SIZE

			# MEM_COMMIT == 0x00001000
			if mbi.State == 0x00001000:
				if current_size < remainder:
					current_size = remainder
				buf = ReadProcessMemory(sp.handle, current_addr, remainder)

				if not buf:
					current_addr += remainder
					continue
				buf = Buffer(buf)

				for s in self.signatures:
					if not s.offset:
					if s in buf:
						print('found match')
					else:
						print('not found match')


				#debug_byte_array(buf)

			current_addr += remainder

		raise RuntimeError('Could not find all signatures in memory.')

	
class SP:

	def __init__(self):

		self.set_pid()
		self.spelunky_process = win32api.OpenProcess(win32con.PROCESS_CREATE_THREAD|
								win32con.PROCESS_QUERY_INFORMATION|
								win32con.PROCESS_SET_INFORMATION|
								win32con.PROCESS_SET_QUOTA|
								win32con.PROCESS_TERMINATE|
								win32con.PROCESS_VM_OPERATION|
								win32con.PROCESS_VM_READ|
								win32con.PROCESS_VM_WRITE,
								True,self.pid)
		if not self.spelunky_process:
			raise RuntimeError('Couldn\'t open the spelunky process.')

		self.handle = self.spelunky_process.handle
		self.signatures = Signatures(self)

	def set_pid(self):

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

def memory_test():
	spelunky_mem = SP()

if __name__ == "__main__":
	memory_test()

