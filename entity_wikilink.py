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

