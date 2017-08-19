# coding: utf-8

import sys, re

keysets = set(x.strip().decode('utf-8') for x in open(sys.argv[1]) if re.match(r"^\t", x))

def reader(fileobj):
    sentence, mid, props = None, None, []
    for line in fileobj:
        parts = line.rstrip().split("\t")
        if parts[0] == u"s":
            if sentence != None and len(props) > 0:
                yield sentence, mid, props
            sentence = parts[1]
            props = []
        else:
            mid = parts[0]
            props = [x.split(",") for x in parts[1:]]

    yield sentence, mid, props

alldata = {}

for f in sys.argv[2:-1]:
    print >> sys.stderr, "processing file %s..." % f
    for sentence, mid, props in reader(x.decode('utf-8') for x in open(f)):
        keyprops = [x for x in props if x[0] in keysets]

        uniq_id = tuple(x[1] for x in sorted(keyprops))
        if uniq_id not in alldata:
            alldata[uniq_id] = []

        alldata[uniq_id].append((sentence, mid, props))

fout = open(sys.argv[-1], "w")
print >> sys.stderr, "writing file %s..." % sys.argv[-1]

for ((ent1, ent2), sentence_list) in alldata.iteritems():
    for (sentence, mid, props) in sentence_list:
        keyprops = sorted([x for x in props if x[0] in keysets], key=lambda x: x[0])
        nonkeyprops = sorted([x for x in props if x not in keyprops], key=lambda x: x[0])
        propsrepr = u"\t".join(u",".join(x) for x in keyprops + nonkeyprops)
        fout.write(u"\t".join((ent1, ent2, mid, sentence, propsrepr)).encode("utf-8") + '\n')

fout.close()

