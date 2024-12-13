## write new yz profile from dictionary to profile.def
import re
import json
import sys

#area = sys.argv[2]
#catch = sys.argv[3]

# read modified yz-profile from script 3
with open("B_PROFILE_yz_edited.json") as f:
    data = f.read()
    tdict = json.loads(data)

# make list of keys ('ID' in DEF file) from modified yz-profile dictionary
tkeys = list(tdict.keys())

# read original DEF profile
f1 = open("PROFILE.DEF", 'r')
lines = f1.readlines()
# make new DEF profile, fill with modified yz-profile
with open("B_PROFILE_edited.DEF", 'w') as f:
    prev = "" # check whether this cross section is modified or not, if yes then prev = True
    # iterate per line, then write based on conditions
    for line in lines:
        # check whether line matches with key (ID of modified yz-profile)
        p1 = re.search(r"\b(%s)\b" % "|".join(tkeys), line)
        # check whether line contains the yz-profile
        p2 = re.search('TBLE|tble|crds', line)
        if p1: # if line matches with key
            prev = True
            # count will update after encountering a line with yz-profile
            count = 0
            # get which item in key matches with current line
            m = p1.group(0)
            # write current line into new DEF profile
            f.write(line)
        elif p2: # if line does not contain yz-profile
            f.write(line)
        else:
            if len(line.split(' '))<4 and prev==False: # if line contains yz-profile BUT this cross section is NOT modified
                # write current line, no change
                f.write(line)
            elif len(line.split(' '))<4 and prev==True: # if line contains yz-profile AND this cross section is modified
                    if count<len(tdict.get(m)): # if count (current line containing yz-profile) is within the length of modified cross section
                        f.write(str(tdict.get(m)[count][0])) # write the Y part of modified yz-profile 
                        f.write(' ')
                        f.write(str(tdict.get(m)[count][1])) # write the Z part of modified yz-profile
                        f.write(' ')
                        f.write("<\n")
                        count+=1 # update count
            else: # if line does not contain yz-profile AND does not match with key
                prev = False # this cross section is not modified
                count = 0
                f.write(line)
