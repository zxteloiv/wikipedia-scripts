# coding: utf-8

import json
import bz2

def reader_for_list(filelist):
    """
    a generator to read from multiple wikidata dump files
    """
    for filename in open(filelist):
        yield reader(filename)

def reader(filename):
    """
    a generator to read wikidata dump file
    format:
        [
            {entity obj},
            ...
        ]
    """
    if filename.endswith('.bz2'):
        f = bz2.BZ2File(filename)
    else:
        f = open(filename)

    for l in f:
        try:
            yield json.loads(l.rstrip().rstrip(','))
        except:
            # error occured when invalid data and json
            # first and last line in the original full file are [ and ] respectively
            continue

    f.close()
            

