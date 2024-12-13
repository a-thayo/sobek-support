## modify yz profile in pandas and rewrite it into dictionary
import json
import re
import numpy
import pandas
import sys

#area = sys.argv[2]
#catch = sys.argv[3]

# read input (JSON >> processed DEF from script 1, DAT >> from SOBEK, CSV >> from CPG)
profile_json = "B_PROFILE_yz.json"
profile_dat = "PROFILE.DAT"
network_csv = r"B1_network_JC.csv"
finalyz = "B_PROFILE_yz_edited.json"

# read JSON file
with open(profile_json) as f:
    data = f.read()
    csdef = json.loads(data)

# transpose profile into 1 Y-array & 1 Z-array > update dictionary
for key in csdef:
    prof = csdef.get(key)
    proft = numpy.transpose([item for item in prof])
    csdef.update({key:proft})

# read DAT file
file = open(profile_dat, 'r')
Lines = file.readlines()
csdat = {}

# make a dictionary of {id : di} from DAT
for line in Lines:
    text = line.strip()
    pattern1 = re.compile(r"CRSN id '(.*?)' di")
    pattern2 = re.compile(r"di '(.*?)' rl")
    match1 = pattern1.findall(text)
    match2 = pattern2.findall(text)
    csdat.update({match1[0]:match2[0]})
    
# make 1 dataframe from JSON
pddef = pandas.DataFrame(csdef.items(), columns=['csid', 'table'])
# make 1 dataframe from DAT
pddat = pandas.DataFrame(csdat.items(), columns=['csname', 'csid'])
# merge both dataframes on 'csid' column >> 'ID'/'NM' in DEF (JSON), 'DI' in DAT
merged1 = pddat.merge(pddef, on='csid')

# read CSV file into 1 dataframe > rename ID column into 'csname'
pdshp = pandas.read_csv(network_csv, usecols=['ID', 'shape', 'init_width', 'init_depth', 'prop_width', 'prop_depth']).rename(columns={"ID":"csname"})

# replace 0 values in 'prop_width' or 'prop_depth' with 'init_width' or 'init_depth'
pdshp['prop_width'] = numpy.where(pdshp['prop_width']==0, pdshp['init_width'], pdshp['prop_width'])
pdshp['prop_depth'] = numpy.where(pdshp['prop_depth']==0, pdshp['init_depth'], pdshp['prop_depth'])

# merge CSV dataframe with merged JSON & DAT dataframe on 'csname' column >> 'ID' in CSV, 'DI' in DEF
merged2 = merged1.merge(pdshp, on='csname')

# get scaling factor for width
merged2['scale_w'] = merged2['prop_width']/merged2['init_width']
# get deepening
merged2['deepening'] = merged2['prop_depth'] - merged2['init_depth']

# define function to modify the profile based on shape, scaling factor, deepening
def modyz(table, shape, scale_w, deepening):
    if shape==0:
        y1 = table[0]
        z1 = table[1]
    elif shape==1:
        y1 = [min(table[0]), min(table[0]), 0, max(table[0]), max(table[0])]
        z1 = [max(table[1]), min(table[1]), min(table[1]), min(table[1]), max(table[1])]
    elif shape==2:
        y1 = [min(table[0]), min(table[0]), 0, max(table[0]), max(table[0]), min(table[0])]
        z1 = [max(table[1]), min(table[1]), min(table[1]), min(table[1]), max(table[1]), max(table[1])]
    y = [x*scale_w if x!=0 else x for x in y1]
    z = [x if x==z1[0] or x==z1[-1] else x-deepening for x in z1]
    return y,z

# apply the function
merged2['table'] = merged2.apply(lambda x: modyz(x['table'], x['shape'], x['scale_w'], x['deepening']), axis=1)

# make nested list containing the Y-array & Z-array for each cross section
ft = [x for x in merged2['table']]
# transpose Y-array & Z-array into normal yz-profile
ft2 = [list(map(list, zip(*x))) for x in ft]
# make dictionary of key = ID (in DEF), value = normal yz-profile
csfinal = dict(zip(merged2['csid'], ft2))

# write dictionary into another JSON
with open(finalyz, 'w') as f:
    json.dump(csfinal, f)
