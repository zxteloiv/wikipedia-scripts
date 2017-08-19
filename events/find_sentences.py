# coding: utf-8

import sys, re

def wiki_reader(fileobj):
    sentence = None
    for line in fileobj:
        parts = line.rstrip().split("\t")
        if parts[0] == u"s":
            if sentence != None:
                yield sentence, entities
            sentence = parts[1]
            entities = []
        else:
            entities = parts[1:]

    yield sentence, entities

print >> sys.stderr, "loading event sentences from %s... " % sys.argv[1]
ev_sen = set(line.decode('utf-8').split(u'\t')[3] for line in open(sys.argv[1]))

fout = open(sys.argv[-1], "w")
print >> sys.stderr, "writing file set to %s." % sys.argv[-1]

for f in sys.argv[2:-1]:
    print >> sys.stderr, "processing file %s..." % f
    for sentence, entities in wiki_reader(x.decode('utf-8') for x in open(f)):
        if len(entities) < 2:
            continue

        if sentence not in ev_sen:
            fout.write((sentence + u"\t" + u"\t".join(sorted(entities))).encode('utf-8') + "\n")

fout.close()

