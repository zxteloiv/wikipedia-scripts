#!/usr/bin/env python2
# coding: utf-8

import re

def get_entity_mentions(text):
    """
    Generate the <entity, mention, line_no> pair
    :param text, a string that contains the line to process

    :return generator of tuple (match_start, match_end, entity_link, mention)
    """

    matches = re.finditer('<a href="([^"]+)">(.*?)</a>', text)

    for m in matches:
        yield (m.start(), m.end(), m.group(1), m.group(2))

def get_entity_mentions_in_lines(lines):
    return ((i, mention) for (i, line) in enumerate(lines) for mention in get_entity_mentions(line))

if __name__ == "__main__":
    from wiki_doc import wikiobj_to_doc
    import sys

    doc = wikiobj_to_doc(open(sys.argv[1], 'r')).next()
    print "\n".join("%3d" % i + "\t" + str(mention) + "\t====>\t" + 
            ", ".join(x.encode('utf-8') for x in (mention[2], mention[3]))
            for (i, mention) in get_entity_mentions_in_lines(doc['text']))

