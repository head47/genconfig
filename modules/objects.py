import json

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
