# coding: utf-8

import json
import logging

from .cirrus import openfile

def query_redis_idx(qid, r):
    qid_t = type(qid)
    if qid_t == type(u'unicode'):
        qid = qid.encode('utf-8')
    target = idx.get('CIRRUS_TITLE_' + qid)
    if target is not None and qid_t == type(u'unicode'):
        target = target.decode('utf-8')
    return target

