import re
import requests
import config

api = f'http://{config.NETBOX_ADDRESS}:{config.NETBOX_PORT}/api/'
# returns which elements of list_ pass the check in format 1-4,5,7-9
# supports setting offset to output numbers bigger than actual indexes
def list_to_nums(list_, check, offset=0):
    nums = ''
    state = 0
    for i in range(0,len(list_)):
        if state == 0: # empty
            if check(list_[i]):
                nums += str(i+offset)
                state = 1
        elif state == 1: # just after number
            if check(list_[i]):
                nums += '~'
                state = 2
            else:
                state = 3
        elif state == 2: # after -
            if not check(list_[i]):
                nums += str(i+offset-1)
                state = 3
            elif i == len(list_)-1:
                nums += str(i+offset)
        elif state == 3: # after sequence
            if check(list_[i]):
                nums += ','+str(i+offset)
                state = 1
    return nums

# converts list of numbers, i.e. 1-4,5,7-9, to index list
# supports setting offset
def nums_expand(nums,offset=0):
    curpos = 0
    numslist = []
    while True:
        comma = nums[curpos:].find(',')
        if comma != -1:
            comma += curpos
        if comma == -1:
            substr = nums[curpos:]
        else:
            substr = nums[curpos:comma]
        if '~' in substr:
            edges = re.findall(r'\d+', substr)
            for i in range(int(edges[0]),int(edges[1])+1):
                numslist.append(i-offset)
        else:
            numslist.append(int(substr)-offset)
        if comma == -1:
            break
        else:
            curpos = comma+1
    return numslist

def get_VLAN_name(vid):
    search_response = requests.get(f'{api}ipam/vlans/?vid={vid}', headers={
        'Authorization': f'Token {config.API_TOKEN}'
    }).json()
    if search_response['count'] == 0:
        return None
    elif search_response['count'] == 1:
        return search_response['results'][0]['name']
    else:
        vlans = search_response['results']
        print('\navailable VLANs with this VID:')
        for i in range(0, search_response['count']):
            if vlans[i]['site'] is None:
                if vlans[i]['group'] is None:
                    print(f"{i+1}. {vlans[i]['name']} (no site or group assignment)")
                else:
                    print(f"{i+1}. {vlans[i]['name']} (group {vlans[i]['group']['name']})")
            else:
                if vlans[i]['group'] is None:
                    print(f"{i+1}. {vlans[i]['name']} (site {vlans[i]['site']['name']})")
                else:
                    print(f"{i+1}. {vlans[i]['name']} (site {vlans[i]['site']['name']}, group {vlans[i]['group']['name']})")
        selection = input(f"entry number ({1}-{search_response['count']}): ")
        return vlans[int(selection)-1]['name']
