##isolate yz profile and convert to profile dictionary 
import re
import json
import sys

#area = sys.argv[2] # only accept {area}_PROFILE

file1 = open(r"Area_B/PROFILE.DEF", "r") #where file 1 is profile.def
Lines = file1.readlines()

data = {}

for line in Lines:
    text = line.strip()
    pattern1 = re.compile(r"nm '(.*?)' ty 10", re.DOTALL)
    pattern2 = re.compile(r"tble", re.DOTALL)
    matches1 = pattern1.findall(text)
    matches2 = pattern2.findall(text)
    if len(matches1):
        key = matches1[0]
        value = []
    if not matches2:
        string_list = text.split(' ')
        if len(string_list)==3:
            numbers = [float(v) for v in string_list[:-1]]
            value.append(numbers)
            data.update({key:value})
    else:
        continue

with open("Area_B/B_PROFILE_yz.json", "w") as outfile:
    json.dump(data, outfile)
                
