#!/usr/bin/env python3
import os
import pathlib
import shutil
import re
import config
import readline
from modules.objects import *
from modules.functions import *
import modules.queries as queries

print("genconfig v1.0")
print("press ? at any time to get help")
mypath = pathlib.PurePath(os.path.realpath(__file__))
mydir = mypath.parent

target = queries.target(mydir)
with open(mydir / 'templates' / (target+'.json')) as tjson:
	device = Device(tjson.read())

username = queries.username()
password = queries.password()
identity = queries.identity()
output = queries.output()

uplink = queries.uplink(device)
if uplink == '':
	pass
elif uplink[0] == 'qsfp': # weird numbering scheme screws stuff up
	device.interfaces[uplink[0]][uplink[1][0]][uplink[1][1]] = 'uplink'
else:
	device.interfaces[uplink[0]][uplink[1]] = 'uplink'

vlans = {}
for vid in config.DEFAULT_VLANS:
	print('Setting up VLAN',vid)
	name = get_VLAN_name(vid)
	if name is None:
		response = flushed_input("WARNING: Couldn't fetch VLAN info from NetBox. Still add it? [y/N] ")
		if response.lower() == 'y':
			name = flushed_input('VLAN name []: ')
			while not re.match(r'^[a-zA-Z0-9-_]*$',name):
				print('ERROR: Invalid characters in VLAN name.')
				name = flushed_input('VLAN name []: ')
			vlans[vid] = VLAN(vid,device,name)
	else:
		vlans[vid] = VLAN(vid,device,name)
while True:
	action = flushed_input('Type [V] to add a VLAN or [E] to save changes: ')
	if action == 'V':
		vid = flushed_input('vid: ')
		name = get_VLAN_name(vid)
		if name is None:
			response = flushed_input("WARNING: Couldn't fetch VLAN info from NetBox. Still add it? [y/N] ")
			if response.lower() == 'y':
				name = flushed_input('VLAN name []: ')
				while not re.match(r'^[a-zA-Z0-9-_]*$',name):
					print('ERROR: Invalid characters in VLAN name.')
					name = flushed_input('VLAN name []: ')
				vlans[vid] = VLAN(vid,device,name)
		else:
			vlans[vid] = VLAN(vid,device,name)
	elif action == 'E':
		break
	else:
		print('ERROR: Unrecognized input.')

cfg = shutil.copy(str(mydir / 'templates' / target)+".rsc.template", output)
with open(cfg, 'a') as c:
	c.write( "\n# --- genconfig config start ---"
			f"\n/system identity set name={identity}")
	if username != 'admin':
		c.write(f"\n/user add name={username} group=full password={password}"
				 "\n/user disable admin")
	else:
		c.write(f"\n/user set admin password={password}")

	c.write('\n/interface bridge port')
	uplinks = []
	for type_ in device.interfaces:
		if type_ == 'qsfp':
			for i in range(0,len(device.interfaces['qsfp'])):
				for j in range(0,len(device.interfaces['qsfp'][i])):
					if device.interfaces['qsfp'][i][j] == 'uplink':
						c.write(f'\nadd bridge=BR-Switch frame-types=admit-only-vlan-tagged interface=qsfp{i+1}-{j+1} pvid=4094')
						uplinks.append(f'qsfp{i+1}-{j+1}')
					elif device.interfaces['qsfp'][i][j] is None:
						c.write(f'\nadd bpdu-guard=yes bridge=BR-Switch interface=qsfp{i+1}-{j+1} pvid=4094')
					elif device.interfaces['qsfp'][i][j].startswith('vlan'):
						pvid = device.interfaces['qsfp'][i][j][4:]
						c.write(f'\nadd bpdu-guard=yes bridge=BR-Switch interface=qsfp{i+1}-{j+1} pvid={pvid}')
		else:
			for i in range(0,len(device.interfaces[type_])):
				if device.interfaces[type_][i] == 'uplink':
					c.write(f'\nadd bridge=BR-Switch frame-types=admit-only-vlan-tagged interface={type_}{i+1} pvid=4094')
					uplinks.append(f'{type_}{i+1}')
				elif device.interfaces[type_][i] is None:
					c.write(f'\nadd bpdu-guard=yes bridge=BR-Switch interface={type_}{i+1} pvid=4094')
				elif device.interfaces[type_][i].startswith('vlan'):
					pvid = device.interfaces[type_][i][4:]
					c.write(f'\nadd bpdu-guard=yes bridge=BR-Switch interface={type_}{i+1} pvid={pvid}')

	c.write('\n/interface bridge vlan')
	tagged = ','.join(uplinks)
	for vid in vlans:
		if vid == config.MANAGEMENT_VLAN:
			c.write(f'\nadd bridge=BR-Switch tagged={tagged},BR-Switch vlan-ids={vid} comment={vlans[vid].name}')
		else:
			c.write(f'\nadd bridge=BR-Switch tagged={tagged} vlan-ids={vid} comment={vlans[vid].name}')

	c.write("\n# --- genconfig config end ---")
