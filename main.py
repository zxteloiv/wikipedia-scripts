#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re
import xuxian

parser = xuxian.get_parser()
parser.add_argument('--task-id', required=True, help='execution id')
parser.add_argument('--wiki-file', required=True,
        help='the /path/to/name of the wiki file to process')
parser.add_argument('--nlp-server', default='127.0.0.1')
parser.add_argument('--nlp-port', default=9000)

parser.add_argument('--entity-wiki-file', required=True,
        help='freebase node and wikipedia map file, first column is '
        'freebase node and second collumn is wikipedia links.'
        )

parser.add_argument('--entity-sentence-output-file', required=True,
        help='output file each line with an entity and the sentence where it appears')

from wiki_doc import wikiobj_to_doc
from utils import charset_wrapper, init_corenlp
from entity_wikilink import build_entity_wikilink_map, href_to_wikilink
from entity_mentions import get_plain_text, get_plain_text_mention_info
from depparse import depparse_paragraph
from depparse import find_sentence_by_offset, get_sentence_id

def process_paragraph_single_entity(sentences, mentions,
        wikilink_to_entity, entity_to_wikilink, outfile):
    # formatted output each entity mention
    for (mstart, mend, href, string) in mentions:
        wikilink = href_to_wikilink(href)
        if wikilink not in wikilink_to_entity:
            # TODO: print error
            continue

        # get the sentence id and its offset in the paragraph line
        sentence_id = get_sentence_id(sentences, mstart, mend)
        if sentence_id >= len(sentences):
            # TODO: print error
            continue
        tokens = sentences[sentence_id][u'tokens']
        sentence_offset = tokens[0]['characterOffsetBegin']

        outfile.info(u"{0}\t{1}\t{2}\t{3}\t{4}".format(
                wikilink_to_entity[wikilink],
                href,
                mstart - sentence_offset, mend - sentence_offset,
                find_sentence_by_offset(sentences, mstart, mend)
                ))

def main(args):
    recovery_state = xuxian.recall(args.task_id)

    # init global object
    docs = wikiobj_to_doc(charset_wrapper(open(args.wiki_file)))
    nlp = init_corenlp(args.nlp_server, args.nlp_port)
    wikilink_to_entity, entity_to_wikilink = build_entity_wikilink_map(
            charset_wrapper(open(args.entity_wiki_file)))

    # init output dump file
    entity_sentence_outfile = xuxian.apply_dump_file('entity-sentence',
            args.entity_sentence_output_file)

    # iterate over data input
    for doc in docs:
        for (lineno, line) in enumerate(doc['text']):
            # at the correct time point, clear the recovery state
            if recovery_state == doc['id'] + str(lineno):
                recovery_state = None
            if recovery_state is not None:
                continue

            # every line is a paragraph in wikipedia
            line = line.rstrip()
            if not line:
                continue

            plaintext = get_plain_text(line)
            mentions = get_plain_text_mention_info(line)

            depparsed_output = depparse_paragraph(plaintext, nlp)
            if u'sentences' not in depparsed_output:
                # TODO: empty ?
                continue

            sentences = depparsed_output[u'sentences']

            process_paragraph_single_entity(sentences, mentions,
                    wikilink_to_entity, entity_to_wikilink,
                    entity_sentence_outfile)

            xuxian.remember(args.task_id, doc['id'] + str(lineno))

        break


if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

