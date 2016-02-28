# coding: utf-8

import re

def build_entity_wikilink_map(obj):
    wikilink_to_entity = {} # one wikilink is to exactly one entity id
    entity_to_wikilink = {} # one entity id may have several wikilink
    for line in obj:
        entity, wikilink = line.strip().split('\t')
        wikilink = upper_first_letter(wikilink)

        wikilink_to_entity[wikilink] = entity
        
        if entity not in entity_to_wikilink:
            entity_to_wikilink[entity] = []

        if wikilink not in entity_to_wikilink[entity]:
            entity_to_wikilink[entity].append(wikilink)

    return (wikilink_to_entity, entity_to_wikilink)

def href_to_wikilink(href):
    return upper_first_letter(href.replace(u' ', u'_'))

def upper_first_letter(text):
    return text[0].upper() + text[1:]

def build_redirect_wikilink_map(obj):
    redirect = dict()
    if not obj:
        return redirect

    for line in obj:
        link1, link2 = line.rstrip().split('\t')
        link1, link2 = upper_first_letter(link1), upper_first_letter(link2)
        redirect[link1] = link2

    return redirect

def href_to_entity(href, wikilink_to_entity, redirect=None):
    link = href_to_wikilink(href)
    if isinstance(redirect, dict) and link in redirect:
        link = redirect[link]

    entity = wikilink_to_entity[link] if link in wikilink_to_entity else None

    return entity

