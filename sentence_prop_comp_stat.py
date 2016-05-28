# count the num of each composition of the first N properties, ordered by the occurence ratio itself

import json, sys

# item in properties statistics:
# [ (prop1, num1), (prop2, num2), ... ], ordered by num
props_stat = {}
for line in open(sys.argv[1]):
    evtype, prop, count = line.rstrip().split()
    if evtype == prop: continue

    if evtype not in props_stat:
        props_stat[evtype] = []

    props_stat[evtype].append((prop, int(count)))

for evtype in props_stat:
    props_stat[evtype] = sorted(props_stat[evtype], key=lambda x: x[1], reverse=True)

# init the composition of the properties, which should be like
# for every property A, B, C, D, E in evtype T
# compositions is a dict { T => [(T.A), (T.A, T.B), (T.A, T.B, T.C)], ... for all T }
compositions = {}
for evtype in props_stat:
    if evtype not in  compositions:
        compositions[evtype] = []

    for length in xrange(1, len(props_stat[evtype]) + 1):
        props = props_stat[evtype][0:length]
        compositions[evtype].append([x[0] for x in props])


"""
Every item in data is:

(u'm.0ztvt6j',
 [u'sports.sports_team_roster',
   u'sports.sports_team_roster.position\tPower forward',
     u'sports.sports_team_roster.player\tRyan Perryman'])
"""

comp_stat = {}

for line in open(sys.argv[2]):
    props = [prop.split(',')[0] for prop in line.rstrip().split('\t')[4:]]
    evtype = ".".join(props[0].split(".")[:2])

    for comp in compositions[evtype]:
        comp = tuple(comp)

        if all(part in props for part in comp):
            if comp not in comp_stat:
                comp_stat[comp] = 0

            comp_stat[comp] += 1


for k in sorted(comp_stat.keys()):
    print " ".join(k), comp_stat[k]

    




