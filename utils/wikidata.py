# coding: utf-8

import json
import logging

from .cirrus import openfile

def query_redis_idx(qid, r):
    qid_t = type(qid)
    if qid_t == type(u'unicode'):
        qid = qid.encode('utf-8')
    target = r.get('WIKIDATA_QID_' + qid)
    if target is not None and qid_t == type(u'unicode'):
        target = target.decode('utf-8')
    return target

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
        return value #u'Q' + value if value[0] != u'Q' else unicode(value)

    return None

