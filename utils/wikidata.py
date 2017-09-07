# coding: utf-8

import json
import logging, datetime

from .cirrus import openfile

def query_redis_idx(qid, r):
    qid_t = type(qid)
    if qid_t == type(u'unicode'):
        qid = qid.encode('utf-8')
    target = r.get('WIKIDATA_QID_' + qid)
    if target is not None and qid_t == type(u'unicode'):
        target = target.decode('utf-8')
    return target

def mquery_redis_idx(qids, r, elemtype=type(u'unicode')):
    logging.info("redis mget %d records" % len(qids))
    qids = ['WIKIDATA_QID_' + (qid.encode('utf-8') if elemtype == type(u'unicode') else qid) for qid in qids]
    logging.info("built up keys %d records, to do mget ... %s" % (len(qids), datetime.datetime.now().strftime('%H:%M:%S')))
    target = r.mget(qids)
    logging.info("end up mget. %s" % datetime.datetime.now().strftime('%H:%M:%S'))
    if target is None:
        logging.warning("got None target, redis may be down")
        return []

    target = [x.decode('utf-8') if elemtype == type(u'unicode') else x for x in target if x is not None]
    logging.info("got %d elems after filtered" % len(target))
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

def get_neighbor_entity(snak):
    try:
        mainsnak = snak['mainsnak']
        snaktype = mainsnak['snaktype']
        if snaktype != 'value':
            return None

        datavalue = mainsnak['datavalue']
        datatype = mainsnak['datatype']
        if datatype == 'wikibase-item':
            value = u'Q' + unicode(datavalue['value']['numeric-id'])
            return value

    except KeyError:
        return None

    return None


