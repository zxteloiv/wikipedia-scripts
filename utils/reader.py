# coding: utf-8

import json
import bz2

import logging

def reader_for_list(filelist):
    """
    a generator to read from multiple json dump files
    """

    for filename in open(filelist):
        filename = filename.rstrip()
        logging.info(str(filename))
    
        for x in reader(filename):
            yield x

def reader(filename):
    """
    a generator to read json data file,
    e.g. wikidata dump file or cirrus page file
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
        except ValueError:
            # error occured when invalid data and json
            # first and last line in the original full file are [ and ] respectively
            continue

    f.close()
            

