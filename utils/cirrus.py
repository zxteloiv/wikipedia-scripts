# coding: utf-8

import json
from .conversion import cc

def openfile(f, opt='r'):
    if type(f) == 'file':
        return f
    elif type(f) in ('str', 'unicode'):
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
    return redir

def load_idx_mapping(idxfile):
    title_idx = {}
    for l in openfile(idxfile):
        title, filename, lineno = l.rstrip().decode('utf-8').split('\t')
        title_idx[title] = filename
    return title_idx

def redirect(redir, title):
    if type(title) == 'str':
        title = title.decode('utf-8')
    target = redir_idx.get(title)
    return title if target is None else target

