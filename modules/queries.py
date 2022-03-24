import os
import re
from modules.functions import *

def target(mydir):
    while True:
        inp = input("target device: ")
        while inp == '?':
            print("\navailable device templates:")
            for t in os.listdir(mydir / 'templates'):
                if t.endswith(".rsc.template"):
                    print(t[:-13])
            inp = input("target device: ")
        if os.path.isfile(mydir / 'templates' / (inp+'.rsc.template')):
            if os.path.isfile(mydir / 'templates' / (inp+'.json')):
                return inp
            else:
                print("ERROR: JSON template info not found.")
        else:
            print("ERROR: Template not found.")

def username():
    while True:
        inp = input("username [admin]: ")
        while inp == '?':
            print('no help available')
            inp = input("username [admin]: ")
        if inp == '':
            return 'admin'
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9*_.@]*$',inp):
            print('ERROR: Invalid characters in username.')
        else:
            return inp

def password():
    while True:
        inp = input("password []: ")
        while inp == '?':
            print('no help available')
            inp = input("password []: ")
        if not re.match(r'^[a-zA-Z0-9*_]*$',inp):
            print('ERROR: Invalid characters in password.')
        else:
            return inp

def identity():
    while True:
        inp = input("identity [MikroTik]: ")
        while inp == '?':
            print('no help available')
            inp = input("identity [MikroTik]: ")
        if inp == '':
            return 'MikroTik'
        if not re.match(r'^[a-zA-Z0-9_-]*$',inp):
            print('ERROR: Invalid characters in identity.')
        else:
            return inp

def output():
    while True:
        inp = input("output path [output.rsc]: ")
        while inp == '?':
            print('no help available')
            inp = input("output path [output.rsc]: ")
        if inp == '':
            return 'output.rsc'
        try:
            open(inp,'w')
        except:
            print('ERROR: Output path is not writable.')
        else:
            if not inp.endswith('.rsc'):
                return inp+'.rsc'
            else:
                return inp

def uplink(device):
    while True:
        uplink = input("uplink []: ")
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
        if uplink == '':
            return ''
        try:
            uplink = list(re.match(r"([a-z]+)(.*)", uplink).groups())
        except AttributeError:
            print('ERROR: Unable to parse input.')
            continue
        if uplink[0] == 'qsfp':
            try:
                uplink[1] = list(map(lambda x: int(x)-1,re.match(r"([0-9]+)-([0-9]+)", uplink[1]).groups()))
            except AttributeError:
                print('ERROR: Unable to parse interface number.')
                continue
            try:
                if device.interfaces['qsfp'][uplink[1][0]][uplink[1][1]] == 'reserved':
                    response = input(f'ERROR: qsfp{uplink[1][0]+1}-{uplink[1][1]+1} is a reserved interface.')
                    continue
            except (KeyError,IndexError):
                print(f'ERROR: Interface qsfp{uplink[1][0]+1}-{uplink[1][1]+1} does not exist.')
                continue
        else:
            try:
                uplink[1] = int(uplink[1])-1
            except ValueError:
                print('ERROR: Unable to parse interface number.')
                continue
            try:
                if device.interfaces[uplink[0]][uplink[1]] == 'reserved':
                    response = input(f'ERROR: {uplink[0]}{uplink[1]+1} is a reserved interface.')
                    continue
            except (KeyError,IndexError):
                print(f'ERROR: Interface {uplink[0]}{uplink[1]+1} does not exist.')
                continue
        return uplink
