# coding: utf-8

import re
import redis
import redis_importer

def href_to_wikilink(href):
    return upper_first_letter(href.replace(u' ', u'_'))

def upper_first_letter(text):
    return text[0].upper() + text[1:] if text else ""

def href_to_entity(href, use_redirect=True, redis_obj=None):
    link = href_to_wikilink(href)
    if use_redirect:
        res = redis_obj.get('redir' + link.encode('utf-8'))
        if res is not None:
            link = res.decode('utf-8')

    res = redis_obj.get('wiki2mid' + link.encode('utf-8'))
    if res is not None:
        entity = res.decode('utf-8')
    else:
        entity = None

    return entity

