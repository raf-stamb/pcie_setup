#!/usr/bin/python3

BIG_ENDIAN = 0
LIT_ENDIAN = 1

class BitVector:

	line_width = 50

	def __init__(self, id: int, name, _size: int, _val, is_rw, _endian = BIG_ENDIAN):
		self.name = name
		self.val = _val
		self.val_s = bin(_val)
		self.val_s = self.val_s[2:] #del 0b prefix
		self.val_s = self.modify_bin_to_size(self.val_s, _size)
		self.size = _size
		self.is_rw = is_rw
		self.endianess =_endian
		self.id = id

	def modify_bin_to_size(self, val: str, size: int) -> str:
		while size > len(val):
			val = "0" + val
		while size < len(val):
			val = val[1:]
		return val

	def __str__(self) -> str:
		id_str = str(self.id)
		if(len(id_str) < 2):
			id_str += " "
		str_res = id_str + " | " + self.name + ":"
		if len(self.name) > self.line_width:
			cur_line_width = self.line_width + 20
		else:
			cur_line_width = self.line_width
		str_res = str_res.ljust(cur_line_width)
		return str_res + "\t" + hex(int(self.val_s, 2))

	def set_int(self, val: int):
		val_bin_s = bin(val)[2:]
		val_bin_s = self.modify_bin_to_size(val_bin_s, self.size)
		while self.size > len(val_bin_s):
			val_bin_s = "0" + val_bin_s
		res = ""
		for i in range(self.size-1, -1, -1):
			res = self.val_s[:i] + val_bin_s[i] + self.val_s[i+1:]
			self.val_s = res
		self.val_s = res

	def set_val(self, val: str):
		if len(val) < len(self.val_s):
			print("Internal error: can't set %s to %s", val, self.val_s)
		for i in range(len(self.val_s)):
			self.val_s[i] = val[i]

	def reverse(self):
		self.val_s = self.val_s[::-1]

	def get(self) -> int:
		return int(self.val_s, base=2)

	def get_srt(self) -> str:
		return self.val_s

	def len(self):
		return len(self.val_s)

	def get_name(self):
		return self.name