# coding: utf-8

import json
import bz2

import logging

def reader_for_list(filelist):
    """
    a generator to read from multiple wikidata dump files
    """

    for filename in open(filelist):
        filename = filename.rstrip()
        logging.info(str(filename))
    
        for x in reader(filename):
            yield x

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
        except ValueError:
            # error occured when invalid data and json
            # first and last line in the original full file are [ and ] respectively
            continue

    f.close()
            
def claim_value(claim):
    if 'mainsnak' not in claim: return None
    mainsnak = claim['mainsnak']
    if 'datavalue' not in mainsnak: return None
    datavalue = mainsnak['datavalue']
    if 'type' not in datavalue: return None
    datavaluetype = datavalue['type']
    if datavaluetype == 'wikibase-entityid':
        value = datavalue['value']['numeric-id']
        return u'Q' + unicode(value)
    elif datavaluetype == "string":
        value = datavalue['value']
        return u'Q' + value if value[0] != u'Q' else unicode(value)

    return None


