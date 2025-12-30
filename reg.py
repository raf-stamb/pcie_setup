#!/usr/bin/python3
from dataclasses import field

from pcie_setup import Color as c

import bitvector as b

line_symb = 0x5f
line_len = 30

class Reg:

	def __init__(self, name, addr):
		self.name = name
		self.fields = {}
		self.fields_order = []
		self.field_id = 0
		self.addr = addr

	def add_field(self, name, size, value = 0, is_rw = 0):
		#adding from Most to least
		self.fields[name] = b.BitVector(self.field_id, name, size, value, is_rw)
		self.fields_order.append(name)
		self.field_id += 1

	def set_field(self, name, val):
		f = self.fields[name]
		f.set_int(val)

	def get_field_by_id(self, id: int):
		for f_name in self.fields:
			f = self.fields[f_name]
			if f.id == id:
				return f.get()

	def set_field_by_id(self, id: int, val):
		for f_name in self.fields:
			f = self.fields[f_name]
			if f.id == id:
				f.set_int(val)

	def get_field_obj_by_id(self, id: int) -> b.BitVector:
		for f_name in self.fields.keys():
			f = self.fields[f_name]
			if f.id == id:
				return f
		return None

	def get_field_name_by_id(self, id: int) -> str:
		for f_name in self.fields.keys():
			f = self.fields[f_name]
			if f.id == id:
				return f.name

	def get_field(self, name) -> int:
		f = self.fields[name]
		return f.get()

	def pack(self) -> int:
		total = 0
		position = 0
		reversed_order = self.fields_order[::-1]
		#going from least to most
		for f_name in reversed_order:
			field = self.fields[f_name]
			total |= field.get() << position
			position += field.size
		return total

	def unpack(self, val: int):
		reversed_order = self.fields_order[::-1]
		position = 0
		# going from least to most
		for f_name in reversed_order:
			val_shifted = val >> position
			field = self.fields[f_name]
			field.set_int(val_shifted)
			position += field.size

	def set_field_from_int(self, val: int):
		pass

	def get_name(self):
		return self.name

	def print(self):
		if len(self.name) > line_len:
			my_line_len = len(self.name) + 4
		else:
			my_line_len = line_len
		print(chr(line_symb) * my_line_len)
		print(self.name)
		print(chr(line_symb) * my_line_len + "\n")
		for f_name in self.fields_order:
			field = self.fields[f_name]
			f_str = str(field)
			if "Reserved" in f_str:
				continue
			elif field.is_rw:
				print(c.GREEN + f_str + c.RESET )
			else:
				print(f_str)
			str(self.fields[f_name])
