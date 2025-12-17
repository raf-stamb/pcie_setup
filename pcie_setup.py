#!/usr/bin/python3

import os.path
import os
import sys
import subprocess
import time
import threading as t
from enum import Enum

import reg

import regs_list as r

host_id = ""
dev_id = ""

DEBUG = 0

class Color:
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	RESET = '\033[0m'

line_symb = 0x5f
line_len = 82

index = 0
reg_dict = {}

class Menu(Enum):
	check_sudo = 0
	get_dev_ids = 1
	main_menu = 2

def main():
	menu = Menu.check_sudo
	try:
		while True:
			if menu == Menu.check_sudo:
				menu = check_sudo(menu)
			if menu == Menu.get_dev_ids:
				menu = get_id(menu)
			elif menu == Menu.main_menu:
				menu = main_menu(menu)
			else:
				pass
	except KeyboardInterrupt:
		exit()

def main_menu(menu: Menu):
	try:
		while True:
			print_main_menu()
			print("\nselect command or press")
			char = input(Color.BOLD + Color.UNDERLINE + "B" + Color.RESET + "ack to main menu: ")
			if char == 'b' or char == 'B':
				return Menu.main_menu
			if char == '1':
				conf_common_speed()
			if char == '2':
				show_dev_status()
			if char == '3':
				conf_common_max_pld()
			if char == '4':
				manual_regs_setup()
	except KeyboardInterrupt:
		exit()

def manual_regs_setup():
	global reg_dict
	_id = get_dev_selection()
	reg_dict = fill_up_regs_avail(_id)
	while True:
		print_regs_avail(reg_dict)
		char = get_reg_selection()
		print(char)
		if char == 'b' or char == 'B':
			return
		try:
			index = int(char, base=10)
		except ValueError:
			continue
		key = find_key_by_index(reg_dict, index)
		if key is None:
			print("Register %s is not found" % key)
		else:
			conf_reg(_id, reg_dict[key])

def find_key_by_index(_dict, index_to_search: int):
	for key, value in _dict.items():
		_index, _reg, i_rw, is_32bit = value
		if _index == index_to_search:
			return key
	return None

def conf_reg(id: str, reg_entry):
	_index, _reg, is_rw, is_32bit = reg_entry
	if is_rw:
		conf_common_reg(id, _reg, is_32bit)
	else:
		conf_rd_only_common_reg(id, _reg, is_32bit)

def print_regs_avail(dict):
	print("\nRegisters available: \n")
	for key, value in dict.items():
		index, _reg, i_rw, is_32bit = value
		index_str = str(index)
		if len(index_str) < 2:
			index_str += " "
		str_res = " " + Color.BOLD + index_str + Color.RESET + " - " + _reg.name
		str_res = str_res.ljust(40)
		print(str_res + "\t\t" + _reg.addr)

def get_reg_selection() -> str:
	print("\nSelect reg or ")
	print(Color.BOLD + Color.UNDERLINE + "B" + Color.RESET + "ack to main menu: ")
	return input()

def get_dev_selection() -> str:
	os.system('clear')
	print("Select device:\n")
	print(Color.BOLD + "1" + Color.RESET + " - Host")
	print(Color.BOLD + "2" + Color.RESET + " - EP device")
	char = input("\n")
	if char == '1':
		id = host_id
	else:
		id = dev_id
	return id

def print_main_menu():
	os.system("clear")
	print(chr(line_symb) * line_len)
	print("[Host]:")
	print(chr(line_symb) * line_len)
	print_dev_status(host_id)

	print("\n" + chr(line_symb) * line_len)
	print("[Device]:")
	print(chr(line_symb) * line_len)
	print_dev_status(dev_id)
	print(chr(line_symb)* line_len)
	print("\nCommand available:\n")
	print(Color.BOLD + " 1" + Color.RESET + " - configure speed")
	print(Color.BOLD + " 2" + Color.RESET + " - show devs status")
	print(Color.BOLD + " 3" + Color.RESET + " - configure max pld")
	print(Color.BOLD + " 4" + Color.RESET + " - manual register setup")

def check_sudo(menu: Menu):
	if os.geteuid() != 0:
		print("file %s needs root privileges, exiting..." % os.path.basename(__file__))
		sys.exit(1)
	return Menu.get_dev_ids

def get_id(menu: Menu):
	global host_id
	global dev_id
	while True:
		os.system("clear")
		os.system("lspci")
		host_id = get_dev_ids("host")
		dev_id = get_dev_ids("device")
		if host_id == dev_id:
			print("host and device id's can't be identical")
			input()
			continue
		return Menu.main_menu

def get_dev_ids(dev_name: str) -> str:
	while True:
		dev_id = input("\nEnter %s id, for example: 00:00.0 " % dev_name)
		dev_id.strip()
		if len(dev_id) < 7:
			continue
		if check_dev_exist(dev_id) != 0:
			print("device %s not found" % dev_id)
			continue
		if check_dev_id_format(dev_id) != 0:
			print("invalid format %s" % dev_id)
			continue
		return dev_id

def check_dev_exist(id: str):
	result = subprocess.run(["lspci", "-s", id], capture_output=True, text=True)
	output = result.stdout
	if output == "":
		return 1
	else:
		return 0

def check_dev_id_format(id: str):
	if len(id) < 6 or (id[2] != ":") or (id[5] != "."):
		print("dot error")
		return 1
	try:
		int(id[0:1], 16)
		int(id[3:4], 16)
		int(id[6], 16)
	except ValueError:
		print("ValueError")
		return 1
	return 0

def print_command_reg(id: str):
	result = read_reg(id, r.COMMAND)
	result_bin = bin(result)
	result_bin = result_bin[2:] #delete 0b prefix
	result_bin = result_bin[::-1] #reverse bit order
	while len(result_bin) < 16:
		result_bin += "0"
	print(chr(line_symb) * line_len)
	print("Command reg")
	print(chr(line_symb) * line_len)
	print("value: " + hex(result))
	print()
	print(Color.GREEN + "1 - Interrupt Disable: " + Color.RESET + result_bin[10])
	print("2 - Fast Back-to-Back Enable: " + result_bin[9])
	print(Color.GREEN + "3 - SERR# Enable: " + Color.RESET + result_bin[8])
	print(Color.GREEN + "4 - Parity Error Response: " + Color.RESET + result_bin[6])
	print("5 - VGA Palette Snoop: " + result_bin[5])
	print("6 - Memory Write and Invalidate Enable: " + result_bin[4])
	print("7 - Special Cycles: " + result_bin[3])
	print(Color.GREEN + "8 - Bus Master: " + Color.RESET + result_bin[2])
	print(Color.GREEN + "9 - Memory Space: " + Color.RESET + result_bin[1])
	print(Color.GREEN + "10 - I/O Space: " + Color.RESET + result_bin[0])

def show_dev_status():
	event = t.Event()
	t1 = t.Thread(target=wait_any_key, args=(event,))
	t1.start()
	t2 = t.Thread(target=print_status_loop, args=(event,))
	t2.start()
	t1.join()
	t2.join()

def print_status_loop(event):
	while not event.is_set():
		os.system("clear")
		print_dev_status(host_id)
		print_dev_status(dev_id)
		print("\npress Enter to stop")
#		time.sleep(0.5)
		time.sleep(0.5)

def wait_any_key(event):
	input()
	event.set()

def conf_common_max_pld():
	os.system("clear")
	print("Supported max payloads: ")
	print_dev_max_pld_supp(host_id)
	print_dev_max_pld_supp(dev_id)
	print("\nCurrent max payload and read request size: ")
	print_dev_max_pld_n_rd(host_id)
	print_dev_max_pld_n_rd(dev_id)
	max_pld = get_user_max_pld("Enter max payload value:")
	conf_dev_max_pld(host_id, max_pld)
	conf_dev_max_pld(dev_id, max_pld)
	max_rd = get_user_max_pld("Enter max read request value:")
	conf_dev_max_rd(host_id, max_rd)
	conf_dev_max_rd(dev_id, max_rd)
	print("Current:")
	print_dev_max_pld_n_rd(host_id)
	print_dev_max_pld_n_rd(dev_id)

def get_user_max_pld(text: str) -> int:
	while True:
		try:
			max_pld = get_user_value(text, 10)
			return encode_max_pld(max_pld)
		except ValueError:
			continue


def encode_max_pld(pld: int) -> int:
	print("pld: %s" % pld)
	if pld == 128:
			return 0
	elif pld == 256:
			print("return 1")
			return 1
	elif pld == 512:
			return 2
	elif pld == 1024:
			return 3
	elif pld == 2048:
			return 4
	elif pld == 4096:
			return 5
	else:
			raise ValueError

def conf_dev_max_pld(id: str, val: int):
	result = read_reg(id, r.DEV_CTRL)
	result &= 0xff1f
	result |= (0x7 & val) << 5
	write_reg(id, r.DEV_CTRL, result)

def conf_dev_max_rd(id: str, val: int):
	result = read_reg(id, r.DEV_CTRL)
	result &= 0x8fff
	result |= (0x7 & val) << 12
	write_reg(id, r.DEV_CTRL, result)

def get_user_value(text: str, _base = 16) -> int:
	while True:
		try:
			print(text)
			val = int(input(""), base=_base)
			break
		except ValueError:
			print("Invalid value")
	return val

def print_dev_max_pld_n_rd(id: str):
	term_dev_id_cmd(id, "lspci -s " + id + " -vv | grep -E 'MaxPayload.*bytes\\, MaxReadReq.*bytes' -o")

def term_dev_id_cmd(id: str, cmd: str, output_result = 1):
	with os.popen(cmd, 'r') as pipe:
		output = pipe.read()
		output.strip()
		if output_result:
			print(id + "\n\t\t" + output)
		return output


def print_dev_max_pld_supp(id: str):
	term_dev_id_cmd(id, "lspci -s " + id + " -vv | grep 'DevCap:.*MaxPayload .*bytes' -o")

def wait_main():
	try:
		while True:
			print("\nPress " + Color.BOLD + Color.UNDERLINE + "Ctrl+C" + Color.RESET + " to exit or")
			char = input(Color.BOLD + Color.UNDERLINE + "B" + Color.RESET + "ack to main menu: ")
			if(char == 'b' or char == 'B'):
				return
	except KeyboardInterrupt:
		exit()

def conf_common_speed():
	os.system("clear")
	print_dev_link_cap_spd(host_id)
	print_dev_link_cap_spd(dev_id)
	spd = get_user_value("Enter common speed 1 - 2.5GT/s, 2 - 5.0GT/s, 3 - 8.0GT/s, 4 - 16.0GT/s, 5 - 32GT/s", 10)
	conf_dev_speed(host_id, spd)
	conf_dev_speed(dev_id, spd)
	link_retrain(host_id)
	print_dev_status(host_id)
	print_dev_status(dev_id)

def conf_dev_speed(id: str, spd: int):
	result = read_reg(id, r.LINK_CTRL2)
	result &= 0xfff0
	result |= (0xf & spd)
	write_reg(id, r.LINK_CTRL2, result)

def print_dev_link_cap_spd(id: str):
	term_dev_id_cmd(id, "lspci -s " + id + " -vv | grep 'LnkCap2:.* Supported Link Speeds:.*/.' -o")

def print_dev_status(id: str):
	term_dev_id_cmd(id, "lspci -s " + id + " -vv | grep 'LnkSta:'")

def link_retrain(id: str):
	result = read_reg(id, r.LINK_CTRL)
	result |= 1<<5
	write_reg(id, r.LINK_CTRL, result)

def conf_rd_only_common_reg(id: str, _reg: reg, is_32bit: int):
	os.system("clear")
	data = read_reg(id, _reg.addr, is_32bit)
	print("data: %x" % data)
	_reg.unpack(data)
	_reg.print()
	wait_main()

def conf_common_reg(id: str, _reg: reg, is_32bit: int):
	os.system("clear")
	data = read_reg(id, _reg.addr, is_32bit)
	print("read: %x" % data)#
	_reg.unpack(data)
	iterate_fields_setup(id, _reg, is_32bit)

def print_fields_legend():
	print("\n Green fields is " + Color.GREEN + "RW" + Color.RESET + ", white fields is  "
		  + "RD only/HwInit" + Color.RESET)

def iterate_fields_setup(id, _reg, is_32bit: int):
	while True:
		os.system("clear")
		_reg.print()
		print_fields_legend()
		field_id = wait_field_select(id, _reg)
		if field_id == 'b':
			return
		f_name = _reg.get_field_name_by_id(field_id)
		val = get_user_value("enter " + f_name + " value: ", 10)
		write_reg_field(id, _reg, field_id, val, is_32bit)
		data = read_reg(id, _reg.addr)
		_reg.unpack(data)

def write_reg_field(id: str, _reg , field_id: int, val: int, is_32bit: int):
	field = _reg.get_field_obj_by_id(field_id)
	if field == None:
		print("Non existing field index: %d" % field_id)
		input()
	assert field.is_rw
	_reg.set_field_by_id(field_id, val)
	data = _reg.pack()
	write_reg(id, _reg.addr, data, is_32bit)

def wait_field_select(id, reg):
	while True:
		print("\nselect field to write or")
		print(Color.BOLD + Color.UNDERLINE + "B" + Color.RESET + "ack to main menu: ")
		char = input()
		try:
			field_id = int(char.strip())
			field = reg.get_field_obj_by_id(field_id)
			if field == None:
				print("Non existing field index: %d" % field_id)
				input("Enter to proceed")
			if field.is_rw == 0:
				continue
			return field_id
		except ValueError:
			if (char == 'b' or char == 'B'):
				return 'b'
			continue

def fill_up_regs_avail(id: str):
	global index
	index = 0
	dict = {}
	add_reg(dict, get_next_index(), conf_command_reg()			, 1, 0)
	add_reg(dict, get_next_index(), conf_status_reg()			, 1, 0)
	add_reg(dict, get_next_index(), conf_dev_cap_reg()         	, 0, 1)
	add_reg(dict, get_next_index(), conf_dev_ctrl_reg()      	, 1, 0)
	add_reg(dict, get_next_index(), conf_dev_status_reg()      	, 1, 0)
	add_reg(dict, get_next_index(), conf_link_cap_reg()        	, 0, 1)
	add_reg(dict, get_next_index(), conf_link_ctrl_reg()       	, 1, 0)
	add_reg(dict, get_next_index(), conf_link_status_reg()     	, 1, 0)
	add_reg(dict, get_next_index(), conf_dev_slot_cap_reg()    	, 0, 1)
	add_reg(dict, get_next_index(), conf_dev_slot_ctrl_reg()   	, 1, 0)
	add_reg(dict, get_next_index(), conf_dev_slot_status_reg()	, 1, 0)
	add_reg(dict, get_next_index(), conf_root_ctrl_reg()       	, 1, 0)
	add_reg(dict, get_next_index(), conf_root_cap_reg()        	, 0, 0)
	add_reg(dict, get_next_index(), conf_root_status_reg()     	, 1, 1)
	add_reg(dict, get_next_index(), conf_dev_ctrl2_reg()       	, 1, 0)
	add_reg(dict, get_next_index(), conf_link_ctrl2_reg()      	, 1, 0)
	add_reg(dict, get_next_index(), conf_link_status2_reg()    	, 1, 0)
	if pm_discovered(id):
		add_reg(dict, get_next_index(), conf_pm_cap()			, 0, 0)
		add_reg(dict, get_next_index(), conf_pm_csr()			, 1, 0)
		add_reg(dict, get_next_index(), conf_pm_bse_data()		, 0, 0)
	if msi_discovered(id):
		add_reg(dict, get_next_index(), conf_msi_msg_ctrl()		, 1, 0)
	if msix_discovered(id):
		add_reg(dict, get_next_index(), conf_msix_msg_ctrl()	,1, 0)
		add_reg(dict, get_next_index(), conf_msix_tbl_offset()	,0, 1)
		add_reg(dict, get_next_index(), conf_msix_pba_offset()	,0, 1)
	return dict

def msix_discovered(id: str):
	_str = term_dev_id_cmd(id, "lspci -s " + id + " -vv | grep -E 'Capabilities: \\[.*\\] MSIX' -o", 0)
	if "MSIX" in _str:
		return True
	else:
		return False

def msi_discovered(id: str):
	_str = term_dev_id_cmd(id, "lspci -s " + id + " -vv | grep -E 'Capabilities: \\[.*\\] MSI' -o", 0)
	if "MSI" in _str:
		return True
	else:
		return False

def pm_discovered(id: str):
	_str = term_dev_id_cmd(id, "lspci -s " + id + " -vv | grep -E 'Capabilities: \\[.*\\] Power Management' -o",0)
	if "Power Management" in _str:
		return True
	else:
		return False

def get_next_index():
	global index
	index += 1
	return index

def add_reg(dict, index, reg, is_rw, is_32bit):
	dict[reg.addr] = [index, reg, is_rw, is_32bit]

def conf_msix_tbl_offset():
	_reg = reg.Reg("MSI-X Table Offset/Table BIR", r.MSIX_TBL_OFFSET)
	_reg.add_field("Table Offset", 29, 0, 0)
	_reg.add_field("Table BIR", 3, 0, 0)
	return _reg

def conf_msix_pba_offset():
	_reg = reg.Reg("MSI-X PBA Offset/PBA BIR", r.MSIX_PBA_OFFSET)
	_reg.add_field("PBA Offset", 29, 0, 0)
	_reg.add_field("PBA BIR", 3, 0, 0)
	return _reg

def conf_msix_msg_ctrl():
	_reg = reg.Reg("MSI-X Message Control", r.MSIX_MSG_CTRL)
	_reg.add_field("MSI-X Enable", 1, 0, 1)
	_reg.add_field("Function Mask", 1, 0, 1)
	_reg.add_field("Reserved", 3, 0, 0)
	_reg.add_field("Table Size", 11, 0, 0)
	return _reg

def conf_msi_msg_ctrl():
	_reg = reg.Reg("MSI Message Control", r.MSI_MSG_CTRL)
	_reg.add_field("Reserved0", 7, 0, 0)
	_reg.add_field("Per-vector masking capable", 1, 0, 0)
	_reg.add_field("64 bit address capable", 1, 0, 0)
	_reg.add_field("Multiple Message Enable", 3, 0, 1)
	_reg.add_field("Multiple Message Capable", 3, 0, 0)
	_reg.add_field("MSI Enable", 1, 0, 1)
	return _reg

def conf_root_ctrl_reg():
	_reg = reg.Reg("Root Control", r.ROOT_CTRL)
	_reg.add_field("Reserved0", 11, 0, 0)
	_reg.add_field("CRS Software Visibility Enable", 1, 0, 1)
	_reg.add_field("PME Interrupt Enable", 1, 0, 1)
	_reg.add_field("System Error on Fatal Error Enable", 1, 0, 1)
	_reg.add_field("System Error on Non-Fatal Error Enable", 1, 0, 1)
	_reg.add_field("System Error on Correctable Error Enable", 1, 0, 1)
	return _reg

def conf_root_cap_reg():
	_reg = reg.Reg("Root Capability", r.ROOT_CAP)
	_reg.add_field("Reserved0", 15, 0, 0)
	_reg.add_field("CRS Software Visibility", 1, 0, 0)
	return _reg

def conf_root_status_reg():
	_reg = reg.Reg("Root Status", r.ROOT_STATUS)
	_reg.add_field("Reserved0", 14, 0, 0)
	_reg.add_field("PME Pending", 1, 0, 0)
	_reg.add_field("PME Status", 1, 0, 1)
	_reg.add_field("PME Requester ID", 16, 0, 0)
	return _reg

def conf_dev_slot_cap_reg():
	_reg = reg.Reg("Slot Capabilities", r.SLOT_CAP)
	_reg.add_field("Physical Slot Number", 13, 0, 0)
	_reg.add_field("No Command Completed Support", 1, 0, 0)
	_reg.add_field("Electromechanical Interlock Present", 1, 0, 0)
	_reg.add_field("Slot Power Limit Scale", 2, 0, 0)
	_reg.add_field("Slot Power Limit Value", 8, 0, 0)
	_reg.add_field("Hot-Plug Capable", 1, 0, 0)
	_reg.add_field("Hot-Plug Surprise", 1, 0, 0)
	_reg.add_field("Power Indicator Present", 1, 0, 0)
	_reg.add_field("Attention Indicator Preset", 1, 0, 0)
	_reg.add_field("MRL sensor Present", 1, 0, 0)
	_reg.add_field("Power Controller Present", 1, 0, 0)
	_reg.add_field("Attention Button Present", 1, 0, 0)
	return _reg

def conf_dev_slot_ctrl_reg():
	_reg = reg.Reg("Slot Control", r.SLOT_CTRL)
	_reg.add_field("Reserved0", 3, 0, 0)
	_reg.add_field("Data Link Layer State Changed Enable", 1, 0, 1)
	_reg.add_field("Electromechanical interlock Control", 1, 0, 1)
	_reg.add_field("Power Controller Control", 1, 0, 1)
	_reg.add_field("Power indication Control", 2, 0, 1)
	_reg.add_field("Attention Indicator Control", 2, 0, 1)
	_reg.add_field("Hot-Plug Interrupt Enable", 1, 0, 1)
	_reg.add_field("Command Completed Interrupt Enable", 1, 0, 1)
	_reg.add_field("Presence Detect CHanged Enable", 1, 0, 1)
	_reg.add_field("MRL Sensor Changed Enable", 1, 0, 1)
	_reg.add_field("Power Fault Detected Enable", 1, 0, 1)
	_reg.add_field("Attention Button Pressed Enabled", 1, 0, 1)
	return _reg
def conf_dev_slot_status_reg():
	_reg = reg.Reg("Slot Status", r.SLOT_STATUS)
	_reg.add_field("Reserved0", 7, 0, 1)
	_reg.add_field("Data Link Layer State Changed", 1, 0, 1)
	_reg.add_field("Electromechanical Interlock Status", 1, 0, 0)
	_reg.add_field("Presence Detect State", 1, 0, 0)
	_reg.add_field("MRL sensor State", 1, 0, 0)
	_reg.add_field("Command Completed", 1, 0, 1)
	_reg.add_field("Presence Detect Changed", 1, 0, 1)
	_reg.add_field("MRL Sensor Changed", 1, 0, 1)
	_reg.add_field("Power Fault Detected", 1, 0, 1)
	_reg.add_field("Attention Button Pressed", 1, 0, 1)
	return _reg

def conf_link_status2_reg():
	_reg = reg.Reg("Link Status 2", r.LINK_STATUS2)
	_reg.add_field("Reserved0", 10, 0, 0)
	_reg.add_field("Link Equalization Request", 1, 0, 1)
	_reg.add_field("Equalization Phase 3 Successful", 1, 0, 0)
	_reg.add_field("Equalization Phase 2 Successful", 1, 0, 0)
	_reg.add_field("Equalization Phase 1 Successful", 1, 0, 0)
	_reg.add_field("Equalization Complete", 1, 0, 0)
	_reg.add_field("Current De-emphasis Level", 1, 0, 0)
	return _reg

def conf_link_ctrl2_reg():
	_reg = reg.Reg("Link Control 2", r.LINK_CTRL2)
	_reg.add_field("Compliance Preset/De-emphasis", 4, 0, 1)
	_reg.add_field("Compliance SOS", 1, 0, 1)
	_reg.add_field("Enter Modified Compliance", 1, 0, 1)
	_reg.add_field("Transmit Margin", 3, 0, 1)
	_reg.add_field("Selectable De-emphasis", 1, 0, 0)
	_reg.add_field("Hardware Autonomous Speed Disable", 1, 0, 1)
	_reg.add_field("Enter Compliance", 1, 0, 1)
	_reg.add_field("Target Link Speed", 4, 0, 1)
	return _reg

def conf_dev_ctrl2_reg():
	_reg = reg.Reg("Device Control 2", r.DEV_CTRL2)
	_reg.add_field("End-End TLP Prefix Blocking", 1, 0, 1)
	_reg.add_field("OBFF Enable", 2, 0, 1)
	_reg.add_field("Reserved0", 2)
	_reg.add_field("LTR Mechanism Enable", 1, 0, 1)
	_reg.add_field("IDO Completion Enable", 1, 0, 1)
	_reg.add_field("IDO Request Enable", 1, 0, 1)
	_reg.add_field("AtomicIp Requester Enable", 1, 0, 1)
	_reg.add_field("ARI Forwarding Enable", 1, 0, 1)
	_reg.add_field("Completion Timeout Disable", 1, 0, 1)
	_reg.add_field("Completion Timeout Value", 4, 0, 1)
	return _reg

def conf_link_status_reg():
	_reg = reg.Reg("Link Status", r.LINK_STATUS)
	_reg.add_field("Link Autonomous Bandwidth Status", 1, 0, 1)
	_reg.add_field("Link Bandwidth Management Status", 1, 0, 1)
	_reg.add_field("Data Link Layer Link Active", 1)
	_reg.add_field("Slot Clock Configuration", 1)
	_reg.add_field("Link Training", 1)
	_reg.add_field("Undefined", 1)
	_reg.add_field("Negotiated Link Width", 6)
	_reg.add_field("Current Link Speed", 4)
	return _reg

def conf_link_ctrl_reg():
	_reg = reg.Reg("Link Control", r.LINK_CTRL)
	_reg.add_field("Reserved0", 										4)
	_reg.add_field("Link Autonomous Bandwidth", 						1, 0, 1)
	_reg.add_field("Link Bandwidth Management Interrupt Enable", 	1, 0, 1)
	_reg.add_field("Hardware Autonomous Width Disable", 				1, 0, 1)
	_reg.add_field("Enable Clock Power Management", 					1, 0, 1)
	_reg.add_field("Extended Sync", 									1, 0, 1)
	_reg.add_field("Common Clock Configuration", 					1, 0, 1)
	_reg.add_field("Retrain Link", 									1, 0, 1)
	_reg.add_field("Link Disable", 									1, 0, 1)
	_reg.add_field("Read Completion Boundary (RCB)", 				1, 0, 1)
	_reg.add_field("Reserved1", 										1)
	_reg.add_field("Active State Power Management (ASPM) Control", 	2, 0, 1)
	return _reg

def conf_link_cap_reg():
	_reg = reg.Reg("Link Capabilities", r.LINK_CAP)
	_reg.add_field("Port Number", 							8)
	_reg.add_field("Reserved0", 								1)
	_reg.add_field("ASPM Optional Compliance", 				1)
	_reg.add_field("Link Bandwith Notification Capability", 	1)
	_reg.add_field("Data Link Layer Active Report Capable", 	1)
	_reg.add_field("Surprise Down Error Reporting Capable", 	1)
	_reg.add_field("Clock Power Management", 				1)
	_reg.add_field("L1 Exit Latency", 						3)
	_reg.add_field("L0 Exit Latency", 						3)
	_reg.add_field("ASPM Support", 							2)
	_reg.add_field("Maximum Link Width", 					6)
	_reg.add_field("Max Link Speed", 						4)
	return _reg

def conf_dev_status_reg():
	_reg = reg.Reg("Device Status", r.DEV_STAT)
	_reg.add_field("Reserved0", 						10)
	_reg.add_field("Transactions Pending", 			1)
	_reg.add_field("AUX Power Detected", 			1)
	_reg.add_field("Unsupported Request Detected", 	1, 0, 1)
	_reg.add_field("Fatal Error Detected", 			1, 0, 1)
	_reg.add_field("Non-Fatal Error Detected", 		1, 0, 1)
	_reg.add_field("Correctable Error Detected", 	1, 0, 1)
	return _reg

def conf_dev_ctrl_reg():
	_reg = reg.Reg("Device Control", r.DEV_CTRL)
	_reg.add_field("Bridge Configuration Retry Enable \n     / Initiate Function Level Reset", 1, 0, 1)
	_reg.add_field("Max_Read_Request_Size", 					3 , 0, 1)
	_reg.add_field("Enable No Snoop", 						1 , 0, 1)
	_reg.add_field("Aux Power PM Enable", 					1 , 0, 1)
	_reg.add_field("Phantom Functions Enable", 				1 , 0, 1)
	_reg.add_field("Extended Tag Field Enable", 				1 , 0, 1)
	_reg.add_field("Max_Payload_Size", 						3 , 0, 1)
	_reg.add_field("Enabled Relaxed Ordering", 				1 , 0, 1)
	_reg.add_field("Unsupported Request Reporting Enabled", 	1 , 0, 1)
	_reg.add_field("Fatal Error Reporting Enable", 			1 , 0, 1)
	_reg.add_field("Non-Fatal Error Reporting Enable", 		1 , 0, 1)
	_reg.add_field("Correctable Error Reporting Enable", 	1 , 0, 1)
	return _reg

def conf_dev_cap_reg():
	_reg = reg.Reg("Device Capabilities", r.DEV_CAP)
	_reg.add_field("Reserved0", 							3)
	_reg.add_field("Function Level Reset Capability", 	1)
	_reg.add_field("Captured Slot Power Limit Scale", 	2)
	_reg.add_field("Captured Slot Power Limit Value", 	8)
	_reg.add_field("Reserved1", 							2)
	_reg.add_field("Role-Based Error Reporting", 		1)
	_reg.add_field("Undefined", 							3)
	_reg.add_field("Endpoint L1 Acceptable Latency", 	3)
	_reg.add_field("Endpoint L0s Acceptable Latency", 	3)
	_reg.add_field("Extended tag field Supported", 		1)
	_reg.add_field("Phantom Functions Supported", 		2)
	_reg.add_field("Max_Payload_Size Supported", 		3)
	return _reg

def conf_command_reg():
	_reg = reg.Reg("Command", r.COMMAND)
	_reg.add_field("Reserved0", 							5)
	_reg.add_field("Interrupt Disable", 					1, 0, 1)
	_reg.add_field("Fast Back-to-Back Enable", 			1)
	_reg.add_field("SERR# Enable", 						1, 0, 1)
	_reg.add_field("Reserved1", 							1)
	_reg.add_field("Parity Error Response", 				1, 0, 1)
	_reg.add_field("VGA Palette Snoop", 					1)
	_reg.add_field("Memory Write and Invalidate Enable",	1)
	_reg.add_field("Special Cycles", 					1)
	_reg.add_field("Bus Master", 						1, 0, 1)
	_reg.add_field("Memory Space", 						1, 0, 1)
	_reg.add_field("I/O Space", 							1, 0, 1)
	return _reg

def conf_status_reg():
	_reg = reg.Reg("Status", r.STATUS)
	_reg.add_field("Detect Parity Error",   		1, 0, 1)
	_reg.add_field("Signaled System Error", 		1, 0, 1)
	_reg.add_field("Received Master Abort", 		1, 0, 1)
	_reg.add_field("Received Target Abort", 		1, 0, 1)
	_reg.add_field("DEVSEL Timing",         		2)
	_reg.add_field("Master Data Parity Error",    1, 0, 1)
	_reg.add_field("Fast Back-to-Back Capable", 	1)
	_reg.add_field("Reserved0", 					1, 0, 0)
	_reg.add_field("66 MHz Capable", 			1, 0, 0)
	_reg.add_field("Capabilities List", 			1, 0, 0)
	_reg.add_field("Interrupt Status", 			1, 0, 0)
	_reg.add_field("Reserved1", 					3, 0, 0)
	return _reg

def conf_pm_cap():
	_reg = reg.Reg("Power Management Capability", r.PM_CAP)
	_reg.add_field("PME Support", 5, 0, 0)
	_reg.add_field("D2 Support", 1, 0, 0)
	_reg.add_field("D1 Support", 1, 0, 0)
	_reg.add_field("AUX Current", 3, 0, 0)
	_reg.add_field("DSI", 1, 0, 0)
	_reg.add_field("Reserved0", 1, 0, 0)
	_reg.add_field("PME Clock", 1, 0, 0)
	_reg.add_field("Version", 3, 0, 0)
	return _reg

def conf_pm_csr():
	_reg = reg.Reg("Power Management Control/Status", r.PM_CSR)
	_reg.add_field("PME Status", 1, 0, 1)
	_reg.add_field("Data Scale", 2, 0, 0)
	_reg.add_field("Data Select", 4, 0, 1)
	_reg.add_field("PME En", 1, 0, 1)
	_reg.add_field("Reserved0", 4, 0, 0)
	_reg.add_field("No Soft Reset", 1, 0, 0)
	_reg.add_field("Reserved1", 1, 0, 0)
	_reg.add_field("PowerState", 2, 0, 1)
	return _reg

def conf_pm_bse_data():
	_reg = reg.Reg("Power Management Bridge Support Extension (BSE) and Data", r.PM_CSR_BSE_DATA)
	_reg.add_field("Data", 8, 0, 0)
	_reg.add_field("Bus Power/Clock Control Enable", 1, 0, 0)
	_reg.add_field("B2/B3 support for D3hot", 1, 0, 0)
	_reg.add_field("Reserved0", 6, 0, 0)
	return _reg

def read_reg(id: str, reg: str, _32bit = 0) -> int:
	if _32bit:
		size = ".l"
	else:
		size = ".w"
	cmd = "setpci -s " + id + " " + reg + size
	with os.popen(cmd, 'r') as pipe:
		print("[RD] " + cmd)
		output = pipe.read()
	try:
		return int(output, base=16)
	except ValueError:
		print("ERR Can't read dev: " + id + " reg: " + reg)
		sys.exit(1)

def write_reg(id: str, reg: str, data: int, _32bit = 0):
	if _32bit:
		size = ".l"
	else:
		size = ".w"
	cmd = "setpci -s " + id + " " + reg + size + "=" + hex(data)
	print("[WR] " + cmd)
	os.system(cmd)
	if DEBUG:
		input()

if __name__ == "__main__":
	main()