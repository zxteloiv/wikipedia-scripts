# coding: utf-8

import sys, re

keysets = set(x.strip().decode('utf-8') for x in open(sys.argv[1]) if re.match(r"^\t", x))

# parse event positive file
# yield sentence as string, evmid as string, props is a list of string "keytype,mid,start,end"
def reader(fileobj):
    for line in fileobj:
        parts = line.rstrip().split("\t")
        evmid, sentence = parts[2], parts[3]
        props = parts[4:]

        yield sentence, evmid, props

# parse wiki-entities file
# yield sentence as string, entities is a list of string "mid,start,end"
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

# read event sentence line from event file argv[1]
print >> sys.stderr, "indexing file %s..." % sys.argv[1]
sentences = dict()
for sentence, evmid, props in reader(x.decode('utf-8') for x in open(sys.argv[1])):
    if sentence not in sentences:
        sentences[sentence] = {'evmid':evmid, 'props':props}

# iterate file to find entities according to the sentences in event file
for f in sys.argv[2:-1]:
    print >> sys.stderr, "iterating over file %s..." % f
    for sentence, entities in wiki_reader(x.decode('utf-8') for x in open(f)):
        if sentence not in sentences:
            continue

        if 'negatives' not in sentences[sentence]:
            sentences[sentence]['negatives'] = set()

        prop_mids = set(prop.split(u',')[1] for prop in sentences[sentence]['props'])

        negatives = (entity for entity in entities if entity.split(',')[0] not in prop_mids)

        sentences[sentence]['negatives'] = sentences[sentence]['negatives'].union(negatives)

# write output data to file
fout = open(sys.argv[-1], "w")
print >> sys.stderr, "writing output file %s..." % sys.argv[-1]
for sentence in sentences:
    data = sentences[sentence]
    evmid, props = data['evmid'], data['props']
    negatives = data['negatives'] if 'negatives' in data else []
    props.extend(u"negative," + neg for neg in negatives)

    if 'negatives' in data and len(data['negatives']) > 0:
        print evmid

    output = u"{0}\t{1}\t{2}".format(
            evmid, sentence, u"\t".join(props)
            )

    fout.write(output.encode('utf-8') + "\n")

fout.close()

