
from win32com.client import GetObject
import ctypes as c
from ctypes import wintypes
import win32api, win32con, struct, binascii, win32

class MEMORY_BASIC_INFORMATION(c.Structure):

	_fields_ = [ ("BaseAddress",  c.c_ulong),
			("AllocationBase", c.c_ulong),
			("AllocationProtect", c.c_long),
			("RegionSize", c.c_long),
			("State", c.c_long),
			("Protect", c.c_long),
			("Type", c.c_long)    ]

_ReadProcessMemory = c.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
_ReadProcessMemory.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,c.c_size_t,c.POINTER(c.c_size_t)]
_ReadProcessMemory.restype = wintypes.BOOL

_VirtualQueryEx = c.WinDLL('kernel32',use_last_error=True).VirtualQueryEx
_VirtualQueryEx.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, c.POINTER(MEMORY_BASIC_INFORMATION), c.c_size_t] 
_VirtualQueryEx.restype = c.c_size_t

def VirtualQueryEx(handle, addr):
	mbi = MEMORY_BASIC_INFORMATION()
	mbi_size = c.c_int(c.sizeof(mbi))
	addr = c.c_long(addr)

	return mbi if _VirtualQueryEx(handle, addr, c.byref(mbi), mbi_size) else None

def ReadProcessMemory(handle, addr, buffer_size):
	
	# gold is stored in a short int (2 bytes)
	data = c.create_string_buffer(buffer_size)

	# for 64-bit python this should be count = c.c_ulongong(0)
	# for 32-bit python this should be count = c.c_ulong(0)
	count = c.c_ulonglong(0)

	return data if _ReadProcessMemory(handle, addr, data, buffer_size, c.byref(count)) else None

class Signatures:

	def search(self, handle):
		BUF_SCAN_SIZE = 4096

		current_addr = 0
		current_size = 0

		end = 10*1024*1024 # 10 mb

		while(current_addr < end):
			if not VirtualQueryEx(handle, current_addr):
				raise RuntimeError('VirtualQueryEx returned error code %d'.format(c.GetLastError()))
			end = mbi.BaseAddress + mbi.RegionSize
			remainder = end - curr_addr
			
			retain = []

			if mbi.State == win32.MEM_COMMIT:
					
				if current_size < remainder:
					current_size = remainder
				buf = ReadProcessMemory(handle, curr_addr, remainder)
				if not buf:
					curr_addr += remainder
					continue

				while len(self._signatures) > 0:
					n,m,s = self._signatures.pop()
					ptr = self.find_pattern(buf, remainder, m, s)

					if ptr:
						self._pointers[n] = (current_addr + (ptr - buf))
					else:
						retain.append((n,m,p))
				self._signatures = retain
				if not self._signatures:
					return

			curr_addr += remainder

		raise RuntimeError('Could not find all signatures in memory.')

	def __init__(self,sp):

		names = ['game_state',
			 'timers',
			 'gold_count',
			 'player_data',
			 'pent_container']

		'''
		'ctrl_size',
		'run_switch_offs',
		'menu_data',
		'gfx_options',
		'level_flags',
		'entity_data']
		'''

		masks = [	[ 'xxxxxxxx.xx.xx.xxxxxx.x',
				  'xxx.....xxxxx.x.x.....x',
				  'xx....xx.xx....xx....xx....xx....',
				  'x.x.x......xxxxx......x......x',
				  'x.....x.x.x......x.x....x']]

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
				0x80 ]]

		self._signatures = list(zip(names,masks,sigs))
		self._pointers = {}

		self.search(sp.handle)

		def find_pattern(buf, data_size, mask, find):
			pos = 0
			size = len(mask)
			for i in range(0,data_size):
				if mask[pos] == '.' or buf[i] == find[pos]:
					pos += 1
					if pos == size:
						return byref(buf)+(i-pos+1)*c.c_size_t
				else:
					i -= pos
					pos = 0
			return None


	def __iter__(self):
		return self

	def __next__(self):
		return next(self._signatures)
		
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

