# coding: utf-8

import json
import bz2

def reader(filename):
    """
    a generator to read wikidata dump file
    format:
        [
            {entity obj},
            ...
        ]
    """
    with bz2.BZ2File(filename) as f:
        f.readline() # escape the first line of '['
        for l in f:
            try:
                yield json.loads(l.rstrip()[:-1])
            except:
                continue
            

