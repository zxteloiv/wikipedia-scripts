# count the num of occurence of each property of each type in event file(in json)

import json, sys

data = json.loads(open(sys.argv[1]).read())

props_stat = {}
"""
Every item in data is:

(u'm.0ztvt6j',
 [u'sports.sports_team_roster',
   u'sports.sports_team_roster.position\tPower forward',
     u'sports.sports_team_roster.player\tRyan Perryman'])
"""
for _, props in data.iteritems():
    for prop in props:
        prop = prop.split('\t')[0]

        if prop not in props_stat:
            props_stat[prop] = 0

        props_stat[prop] += 1

for k in sorted(props_stat.keys()):
    print '.'.join(k.split('.')[0:2]), k, props_stat[k]

