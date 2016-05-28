# count the num of occurence of each property of each type in event file(in json)

import json, sys

props_stat = {}
for line in open(sys.argv[1]):
    props = [prop.split(',')[0] for prop in line.rstrip().split('\t')[4:]]
    evtype = ".".join(props[0].split(".")[:2])
    if evtype not in props_stat:
        props_stat[evtype] = 0

    props_stat[evtype] += 1


    for prop in props:
        prop = prop.split('\t')[0]

        if prop not in props_stat:
            props_stat[prop] = 0

        props_stat[prop] += 1

for k in sorted(props_stat.keys()):
    print '.'.join(k.split('.')[0:2]), k, props_stat[k]

