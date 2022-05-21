import json
from modules.functions import *

class Device:
    def __init__(self, jsonstr):
        jsonobj = json.loads(jsonstr)
        self.interfaces = jsonobj["interfaces"]
        # if "ether" not in jsonobj["interfaces"]: -- NOT IMPLEMENTED
        self.interfaces["ether"] = [None]*(jsonobj["interfaces"]["ether"]-1)+["reserved"]
        if "sfpp" in jsonobj["interfaces"]:
            self.interfaces["sfpp"] = ["uplink"]*jsonobj["interfaces"]["sfpp"]
        else:
            self.interfaces["sfpp"] = []
        if "qsfp" in jsonobj["interfaces"]:
            self.interfaces["qsfp"] = [["uplink"]*jsonobj["interfaces"]["qsfp"][1]]*jsonobj["interfaces"]["qsfp"][0]
        else:
            self.interfaces["qsfp"] = []

class VLAN:
    def __init__(self, vid, device, name):
        self.vid = vid
        self.interfaces = []
        self.name = name
        print("""which ports have this VLAN as primary?
format: <type> <list> (example: ether 1~7,14,17~20), one per line
enter "." to end""")
        while True:
            line = flushed_input('> ')
            if line == '?':
                print('\navailable interfaces:')
                for type_ in device.interfaces:
                    available = list_to_nums(device.interfaces[type_], lambda x: x is None, 1)
                    if available != '':
                        print(type_, available)
            elif line == '.':
                break
            else:
                line = line.split()
                type_ = line[0]
                if type_ == 'qsfp':
                    print('ERROR: Including QSFP interfaces in VLANs is not implemented yet. Discarding previous line.')
                    continue
                try:
                    nums = nums_expand(line[1])
                except:
                    print('ERROR: Unable to parse input. Discarding previous line.')
                    continue
                if nums[0] <= 0:
                    print('ERROR: The specified range of interfaces is invalid. Discarding previous line.')
                    continue
                try:
                    for i in nums:
                        device.interfaces[type_][i-1]
                except KeyError:
                    print(f'ERROR: {type_} is not a valid interface type. Discarding previous line.')
                except IndexError:
                    print(f'ERROR: The specified range of interfaces is invalid. Discarding previous line.')
                else:
                    overrideflag = False
                    contflag = False
                    for i in nums:
                        if device.interfaces[type_][i-1] is not None:
                            if device.interfaces[type_][i-1] == 'reserved':
                                print(f'ERROR: {type_}{i} is a reserved port. Discarding previous line.')
                                contflag = True
                                break
                            if (not overrideflag) and (device.interfaces[type_][i-1] != 'vlan'+vid):
                                response = flushed_input(f'WARNING: {type_}{i} is registered as {device.interfaces[type_][i-1]}. Override with this VLAN? [y/N/a] ')
                                if response.lower() == 'y':
                                    continue
                                elif response.lower() == 'a':
                                    overrideflag = True
                                else:
                                    print('Discarding previous line.')
                                    contflag = True
                                    break
                    if contflag:
                        continue
                    for i in nums:
                        device.interfaces[type_][i-1] = 'vlan'+vid
                        self.interfaces.append(type_+str(i))
