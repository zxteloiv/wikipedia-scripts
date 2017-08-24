# coding: utf-8

import json
from .conversion import cc
import logging

def openfile(f, opt='r'):
    logging.debug('type of given %s: %s' % (str(f), type(f)))
    if type(f) == 'file':
        return f
    elif type(f) in (type('str'), type(u'unicode')):
        logging.debug('open file %s' % f)
        return open(f, opt)
    
    # an empty generator
    def nothing_handle():
        raise StopIteration
        yield None
    return nothing_handle()

def load_redir_mapping(rfile):
    redir = {}
    for l in openfile(rfile):
        arr = l.decode('utf-8').rstrip().split('\t')
        redir[arr[0]] = arr[1]
    logging.debug('redirect contains %d entries' % len(redir))
    return redir

def load_idx_mapping(idxfile):
    title_idx = {}
    for l in openfile(idxfile):
        title, filename, lineno = l.rstrip().decode('utf-8').split('\t')
        title_idx[title] = filename
    logging.debug('title index contains %d entries' % len(title_idx))
    return title_idx

def redirect(redir_idx, title):
    if type(title) == 'str':
        title = title.decode('utf-8')
    target = redir_idx.get(title)
    return title if target is None else target

