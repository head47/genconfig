import re

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
                nums += '-'
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
        if '-' in substr:
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
