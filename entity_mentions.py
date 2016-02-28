#!/usr/bin/env python2
# coding: utf-8

import re

ENTITY_MENTION_RE = re.compile('<a href="(.*?)">(.*?)</a>')

def get_entity_mentions(text, offset=0):
    """
    Generate the <entity, mention, line_no> pair
    :param text: a string that contains the line to process
    :param offset: an offset for text searching, and will be subtracted from the
                    matching object offset

    :return generator of tuple (match_start, match_end, entity_link, mention)
    """

    matches = ENTITY_MENTION_RE.finditer(text, offset)

    for m in matches:
        yield (m.start() - offset, m.end() - offset, m.group(1), m.group(2))

def get_entity_mentions_in_lines(lines):
    return ((i, mention) for (i, line) in enumerate(lines)
            for mention in get_entity_mentions(line))

def get_plain_text(text):
    return re.sub('<.*?>', '', text).strip()

def get_plain_text_mention_info(text, offset=0):
    """
    Get mention info in plain text
    :param text: raw line string
    :param offset: the returned start and end position will be based on the offset
    :return list of mentions: (start, ends, entity_href, mention_repr)
    """

    mentions = list(get_entity_mentions(text, offset))
    if not mentions:
        return []

    # Mentions Figure:
    #
    # --- preceding 1 --- mention 1 --- preceding 2 --- mention 2 --- tail |

    cursor = 0
    plain_mentions = []
    plain_mention_cursor = 0

    for mention in mentions:
        pat_start, pat_end, entity, mention_repr = mention

        preceding_len = pat_start - cursor
        cursor += preceding_len
        plain_mention_cursor += preceding_len

        # append new plain mention info, only when mention is not empty
        # but the cursor computation is still necessary
        if len(mention_repr) > 0:
            plain_mentions.append((plain_mention_cursor, # plain mention start
                plain_mention_cursor + len(mention_repr), # plain mention end
                entity, mention_repr)) # entity link and entity mention

        mention_len = pat_end - pat_start
        cursor += mention_len
        plain_mention_cursor += len(mention_repr)

    # no more mention in tail, cursor info is trival now

    return plain_mentions

if __name__ == "__main__":
    from utils import charset_wrapper
    from wiki_doc import wikiobj_to_doc
    from entity_mentions import get_entity_mentions, get_entity_mentions_in_lines
    from entity_mentions import get_plain_text, get_plain_text_mention_info
    import sys

    doc = wikiobj_to_doc(charset_wrapper(open(sys.argv[1], 'r'))).next()

    # unit test for get_entity_mentions and get_entity_mentions_in_lines
    print "\n".join("%3d" % i + "\t" + str(mention) + "\t====>\t" + 
            ", ".join(x.encode('utf-8') for x in (mention[2], mention[3]))
            for (i, mention) in get_entity_mentions_in_lines(doc['text']))

    # unit test for get_plain_text and get_plain_text_mention_info
    for line in doc['text']:
        plain_line = get_plain_text(line)
        mentions = get_plain_text_mention_info(line)

        if not mentions:
            continue

        print "\nplain_line:\t" + plain_line.encode('utf-8').rstrip()
        for mention in mentions:
            print str(mention) + "\t==mentionrepr==>\t" + plain_line[mention[0]:mention[1]].encode('utf-8')





