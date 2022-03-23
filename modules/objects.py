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
    def __init__(self, vid, device):
        self.vid = vid
        self.interfaces = []
        print("""which ports have this VLAN as primary?
format: <type> <list> (example: ether 1~7,14,17~20), one per line
enter "." to end""")
        while True:
            line = input('> ')
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
                nums = nums_expand(line[1])
                for i in nums:
                    device.interfaces[type_][i-1] = vid
                    self.interfaces.append(type_+str(i))
