#!/usr/bin/env python3
import os
import pathlib
import shutil
import re
from config import API_TOKEN
from modules.objects import *
from modules.functions import *

print("genconfig v0.015")
print("press ? at any time to get help")
mypath = pathlib.PurePath(os.path.realpath(__file__))
mydir = mypath.parent

target = input("target device: ")
while target == '?':
	print("\navailable device templates:")
	for t in os.listdir(mydir / 'templates'):
		if t.endswith(".rsc.template"):
			print(t[:-13])
	target = input("target device: ")
with open(mydir / 'templates' / (target+'.json')) as tjson:
	device = Device(tjson.read())

username = input("username: ")
while username == '?':
	print('no help available')
	username = input("username: ")
password = input("password: ")
while password == '?':
	print('no help available')
	password = input("password: ")

identity = input("identity: ")
while identity == '?':
	print('no help available')
	identity = input("identity: ")

output = input("output path: ")
while output == '?':
	print('no help available')
	output = input("output path: ")

uplink = input("uplink: ")
while uplink == '?':
	print('\navailable interfaces:')
	for type_ in device.interfaces:
		if type_ == 'qsfp':
			for i in range(0,len(device.interfaces['qsfp'])):
				for j in range(0,len(device.interfaces['qsfp'][i])):
					print('qsfp'+str(i+1)+'-'+str(j+1))
		else:
			available = list_to_nums(device.interfaces[type_], lambda x: (x is None) or (x == "uplink"), 1)
			if available != '':
				print(type_+available)
	uplink = input("uplink: ")
uplink = list(re.match(r"([a-z]+)(.*)", uplink).groups())
if uplink[0] == 'qsfp': # weird numbering scheme screws stuff up
	uplink[1] = re.match(r"([0-9]+)-([0-9]+)", uplink[1]).groups()
	device.interfaces[uplink[0]][uplink[1][0]][uplink[1][1]] = 'uplink'
else:
	uplink[1] = int(uplink[1])-1
	device.interfaces[uplink[0]][uplink[1]] = 'uplink'

vlans = []
while True:
	action = input('Type [V] to add a VLAN or [E] to save changes: ')
	if action == 'V':
		vid = input('vid: ')
		vlans.append(VLAN(vid,device))
	elif action == 'E':
		break
	else:
		print('ERROR: Unrecognized input.')

config = shutil.copy(str(mydir / 'templates' / target)+".rsc.template", output+".rsc")
with open(config, 'a') as c:
	c.write( "\n# --- genconfig config start ---"
			f"\n/system identity set name={identity}")
	if username != 'admin':
		c.write(f"\n/user add name={username} group=full password={password}"
				 "\n/user disable admin")
	else:
		c.write(f"\n/user set admin password={password}")
	c.write("\n# --- genconfig config end ---")
