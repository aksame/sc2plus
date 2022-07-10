import os
import fileinput
import binascii
import string
from struct import unpack, pack
from shutil import copy

HUMANFILECOUNT = 0x27
MITSURUGIFILESIDX = 0x2E
NEWTABLESIZE = 0x1000

# Expands File5.olk table and adds data for two characters
def expand(base_olk_fn, mod_dir):
	mod_olk_fn = os.path.join(mod_dir,"files\\root.olk")
	base_olk = open(base_olk_fn, 'rb')
	#mod_olk = open(mod_olk_fn, 'wb')
	#print(f'{base_olk_fn} {mod_olk_fn}')

	# get root.olk size
	base_olk.seek(0x10)
	rootEntry = unpack("<III", base_olk.read(12))
	root_tSize = rootEntry[0]
	root_fSize = rootEntry[1]
	root_dt = rootEntry[2]

	# get File5.olk offset/size
	base_olk.seek(0x60)
	file5Entry = unpack("<III", base_olk.read(12))
	file5_offset = file5Entry[0]
	file5_size = file5Entry[1]
	file5_dt = file5Entry[2]
	f5_off = file5_offset + root_tSize

	# read File5 header
	base_olk.seek(f5_off)
	file5Header = unpack("<I", base_olk.read(4))
	file5_count = file5Header[0]

	base_olk.seek(f5_off + 0x10)
	file5RootEntry = unpack("<III", base_olk.read(12))
	file5_tSize = file5RootEntry[0]
	file5_fSize = file5RootEntry[1]
	file5_rDt = file5RootEntry[2]

	# get mitsurugi file offsets/sizes/datetimes
	base_olk.seek(f5_off + 0x20 + (MITSURUGIFILESIDX * 0x10))

	m_offset = []
	m_size = []
	m_dt = []
	m_offset = [0 for i in range(HUMANFILECOUNT)]
	m_size = [0 for i in range(HUMANFILECOUNT)]
	m_dt = [0 for i in range(HUMANFILECOUNT)]
	for i in range(HUMANFILECOUNT):
		fEntry = unpack("<IIII", base_olk.read(16))
		m_offset[i] = fEntry[0]
		m_size[i] = fEntry[1]
		m_dt[i] = fEntry[2]

	# add total size
	m_tsize = m_offset[0x26] - m_offset[0]

	# read all of mitsurugi's files
	m_data = []
	base_olk.seek(f5_off + file5_tSize + m_offset[0])
	m_data = base_olk.read(m_tsize)

	# write new olk
	r_data = []
	mod_olk = open(mod_olk_fn, 'wb')
	base_olk.seek(0)
	r_data = base_olk.read(0x14)
	mod_olk.write(r_data)

	# write new root size
	mod_olk.write(pack("<III", root_fSize + (m_tsize * 2) + NEWTABLESIZE, root_dt, 0))
	base_olk.seek(0x20)
	r_data = base_olk.read(0x44)
	mod_olk.write(r_data)

	# write new file5 size in root
	mod_olk.write(pack("<III", file5_size + (m_tsize * 2) + NEWTABLESIZE, file5_dt, 0))

	curpos = 0x70
	base_olk.seek(curpos)
	r_data = base_olk.read(f5_off - curpos)

	# write data up to start of file5
	mod_olk.write(r_data)

	# write file5.olk header
	new_count = file5_count + (HUMANFILECOUNT * 2)
	mod_olk.write(pack('<IIII', new_count, 0x6B6E6C6F, 0x800, 0))

	# write file5.olk root entry
	mod_olk.write(pack('<IIII', file5_tSize + NEWTABLESIZE, file5_fSize + (m_tsize * 2), file5_rDt, 0))

	# write rest of file5 table
	base_olk.seek(f5_off + 0x20)
	r_data = base_olk.read(file5_count * 0x10)
	mod_olk.write(r_data)

	# write new entries to table
	for j in range(2):
		for i in range(HUMANFILECOUNT):
			new_offset = file5_fSize + (j * m_tsize) + (m_offset[i] - m_offset[0])
			mod_olk.write(pack('<IIII', new_offset, m_size[i], m_dt[i], 0))

	# write first part of file5.olk data
	base_olk.seek(f5_off + file5_tSize)
	r_data = base_olk.read(file5_fSize)
	mod_olk.seek(f5_off + file5_tSize + NEWTABLESIZE)
	mod_olk.write(r_data)

	# write mitsurugi data for heihachi/spawn
	for j in range(2):
		mod_olk.write(m_data)

	base_olk.close()
	mod_olk.close()

def get_aligned_size(value, align_size):
	pad = align_size - (value % align_size)
	value += pad
	#print(f'size: {hex(value)}')
	return value

def pad_bytes(f, offset, size):
	f.seek(offset)
	for i in range(size):
		f.write(pack('<B', 0))
	return


olks = ['dummy', 'cpudata', 'cdata', 'stage', 'human']

def replace_file(olk, r_idx, idx, fn):

	# get root olk and sub olk size
	# root
	olk.seek(0)
	r_header = unpack('<IIIIIIII', olk.read(32))
	r_count = r_header[0]
	r_tSize = r_header[4]
	r_fSize = r_header[5]

	# sub
	olk.seek(0x20 + (r_idx * 0x10))
	s_header = unpack('<II', olk.read(8))
	s_offset = s_header[0]
	s_size = s_header[1]

	sub_olk_offset = s_offset + r_tSize

	olk_size = r_fSize + r_tSize

	# read sub olk header
	olk.seek(sub_olk_offset)
	sub_header = unpack('<IIIIIIII', olk.read(32))
	sub_count = sub_header[0]
	sub_tSize = sub_header[4]
	sub_fSize = sub_header[5]

	# read file offset/size
	olk.seek(sub_olk_offset + 0x20 + (idx * 0x10))
	f_header = unpack('<II', olk.read(8))
	f_offset = f_header[0]
	f_size = f_header[1]

	file_offset = sub_olk_offset + sub_tSize + f_offset
	
	if f_size != 0:
		file_size = get_aligned_size(f_size, 0x800)
	else:
		file_size = 0

	file_end_off = file_offset + file_size

	print(f'Replacing file #{idx} ({hex(file_offset)}) in olk #{r_idx} ({hex(sub_olk_offset)}) with {fn}')

	m_size = os.path.getsize(fn)
	m_file = open(fn, 'rb')
	m_data = m_file.read(m_size)

	add_size = 0

	if m_size < file_size: # write new file over old
		olk.seek(file_offset)
		olk.write(m_data)
		pad_bytes(olk, file_offset + m_size, file_size - m_size)
	else: # split olk and fix offsets/size in olk headers
		new_size = get_aligned_size(m_size, 0x800)
		add_size = new_size - file_size

		# read end of file entry to end of olk
		olk.seek(file_end_off)
		olk_data = olk.read(olk_size - file_end_off)

		#  write new file over old
		olk.seek(file_offset)
		olk.write(m_data)
		pad_bytes(olk, file_offset + m_size, new_size - m_size)

		# write rest of olk data
		olk.seek(file_offset + new_size)
		olk.write(olk_data)

		# fix root olk entry offsts
		for x in range(r_count - (r_idx + 1)):
			o = 0x20 + ((r_idx + 1) * 0x10) + (x * 0x10)
			olk.seek(o)
			e_header = unpack('<I', olk.read(4))
			e_offset = e_header[0] + add_size
			olk.seek(o)
			olk.write(pack('<I', e_offset))

		# fix file entry offsets
		for x in range (sub_count - (idx + 1)):
			olk.seek(sub_olk_offset + 0x20 + ((idx + 1) * 0x10) + (x * 0x10))
			e_header = unpack('<I', olk.read(4))
			e_offset = e_header[0] + add_size
			olk.seek(sub_olk_offset + 0x20 + ((idx + 1) * 0x10) + (x * 0x10))
			olk.write(pack('<I', e_offset))

		# fix sizes
		# root
		olk.seek(0x14)
		olk.write(pack('<I', r_fSize + add_size))
		# sub olk entry
		olk.seek(0x24 + (r_idx * 0x10))
		olk.write(pack('<I', s_size + add_size))
		# sub olk root
		olk.seek(sub_olk_offset + 0x14)
		olk.write(pack('<I', sub_fSize + add_size))

	# fix sizes
	# file entry
	olk.seek(sub_olk_offset + 0x24 + (idx * 0x10))
	olk.write(pack('<I', m_size))

	return


def read_flist(mod_root_dir, olk_fn, r_idx):
	olk_dir = olks[r_idx]
	olk_dir = os.path.join(mod_root_dir, olk_dir)
	flist_fn = os.path.join(olk_dir,"flist.txt")

	if os.path.exists(flist_fn) == False:
		#print(f'{flist_fn} doesn\'t exist! Skipping...')
		return

	print(f'Reading {flist_fn}')

	flist = open(flist_fn, 'r')
	lines = flist.readlines()
	flist.close()

	#print(f'Reading {olk_fn}')
	olk = open(olk_fn, 'r+b')

	line_count = 0
	for line in lines:
		line_count += 1
		#line = line.strip()
		line = line.split()
		word = list(line[0])
		if '#' not in word:
			#print(f'{line[0]} {line[1]}')
			idx = int(line[0], 16)
			fn = line[1]
			fn = os.path.join(olk_dir, fn)
			replace_file(olk, r_idx, idx, fn)
		#else:
			#print(f'Skipping comment...')
	olk.close()
	return


def replace(mod_dir):
	mod_olk_fn = os.path.join(mod_dir,"files\\root.olk")
	mod_olk_dir = os.path.join(mod_dir,"files\\root")

	r_idx = 0
	for olk_dir in olks:
		read_flist(mod_olk_dir, mod_olk_fn, r_idx)
		r_idx += 1

	print(f'Finished replacing files!')
	return

