
from win32com.client import GetObject
import ctypes as c
from ctypes import wintypes
import win32api, win32con, struct, binascii


def get_spelunky_pid():

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
		return spelunky_candidates[0][0]


def i_hate_snakes():
	'''
	ReadProcessMemory = c.windll.kernel32.ReadProcessMemory
	WriteProcessMemory = c.windll.kernel32.WriteProcessMemory
	'''

	ReadProcessMemory = c.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
	ReadProcessMemory.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,c.c_size_t,c.POINTER(c.c_size_t)]
	ReadProcessMemory.restype = wintypes.BOOL

	spelunky_pid = get_spelunky_pid()

	print('spelunky_pid:',spelunky_pid)
	
	'''
	spelunky_process = win32api.OpenProcess(win32con.PROCESS_CREATE_THREAD|
				win32con.PROCESS_QUERY_INFORMATION|
				win32con.PROCESS_SET_INFORMATION|
				win32con.PROCESS_SET_QUOTA|
				win32con.PROCESS_TERMINATE|
				win32con.PROCESS_VM_OPERATION|
				win32con.PROCESS_VM_READ|
				win32con.PROCESS_VM_WRITE,
				True,spelunky_pid)
	'''

	spelunky_process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,True,spelunky_pid)

	if not spelunky_process:
		raise RuntimeError('Couldn\'t open the spelunky process.')

		
	# this won't work unless you find the offset in your process space 
	# (this is the problem i'm figuring out)
	
	gold_address = 0x0B3D894C 
	
	# gold is stored in a short int (2 bytes)
	gold_data = c.create_string_buffer(2)

	# for 64-bit python this should be count = c.c_ulongong(0)
	# for 32-bit python this should be count = c.c_ulong(0)
	count = c.c_ulonglong(0)

	while True:
		input('Hit enter to read gold')
		valid = ReadProcessMemory(spelunky_process.handle, gold_address, gold_data, 2, c.byref(count))
		print('\tReadProcessMemory(...) returns',valid,'bytes')
		if valid == 0:
			print('\tReadProcessMemory error code:', c.GetLastError())
		print('\tGold:',gold_data.value)
		print('\tGold:',struct.unpack('H',gold_data.value))




if __name__ == "__main__":
	i_hate_snakes()


