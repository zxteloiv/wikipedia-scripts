#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re
import xuxian
from itertools import permutations

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
from depparse import depparse_paragraph, vertices_route_to_deproute
from depparse import get_token_id_list_by_mention, restore_sentence_from_tokens
from depparse import find_sentence_by_offset, get_sentence_id
from dijkstra import dijkstra_path_for_regions

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

        # Finally, the output offset of a mention should be based on the
        # sentence itself rather than the whole line paragraph.
        outfile.info(u"{0}\t{1}\t{2}\t{3}\t{4}".format(
                wikilink_to_entity[wikilink],
                href,
                mstart - sentence_offset, mend - sentence_offset,
                find_sentence_by_offset(sentences, mstart, mend)
                ))

def process_paragraph_multiple_entity(sentences, mentions,
        wikilink_to_entity, entity_to_wikilink, outfile):
    """
    To produce a deproute between any two of the entities in a sentence.
    Produce each line: entity1, entity2, deproute, and sentence separated by tab

    :param sentences:
    :param mentions: 

    """
    syslog = xuxian.log.system_logger

    # prepare the lookup structure
    sentence_to_mention = [[] for i in xrange(len(sentences))]
    for mention in mentions:
        (mstart, mend, href, _) = mention
        sentence_id = get_sentence_id(sentences, mstart, mend)
        token_list = get_token_id_list_by_mention(sentences[sentence_id],
                mstart, mend)
        sentence_to_mention[sentence_id].append((mention, token_list))

    syslog.debug('sentence_to_mention=' + (
        " ".join(str(i) + '=>' + str(x) for (i, x) in enumerate(sentence_to_mention))
        ))

    # edge set for every sentence
    sentence_edges = [dict(((e['governor'] - 1, e['dependent'] - 1, 1), i) 
        for i, e in enumerate(sentence['basic-dependencies']) if e['dep'] != 'ROOT')
        for sentence in sentences]

    for sentence_id in xrange(len(sentence_to_mention)):
        sentence = sentences[sentence_id]
        tokens = sentence[u'tokens']
        sentence_mentions = sentence_to_mention[sentence_id]

        syslog.debug('sentence=%d ' % sentence_id +
                'mentions=' + str(sentence_mentions))

        for ((m1, t1), (m2, t2)) in permutations(sentence_mentions, 2):
            mindist, minroute = dijkstra_path_for_regions(t1, t2,
                    tokens, sentence_edges[sentence_id].keys())

            deproute_string = vertices_route_to_deproute(minroute, 
                    sentence_edges[sentence_id], tokens,
                    sentence['basic-dependencies'])

            outfile.info(u"{0}\t{1}\t{2}\t{3}".format(
                wikilink_to_entity[href_to_wikilink(m1[3])],
                wikilink_to_entity[href_to_wikilink(m2[3])],
                deproute_string,
                restore_sentence_from_tokens(tokens)
                ).encode('utf-8'))
    pass

def main(args):
    recovery_state = xuxian.recall(args.task_id)
    syslog = xuxian.log.system_logger

    # init global object
    docs = wikiobj_to_doc(charset_wrapper(open(args.wiki_file)))
    nlp = init_corenlp(args.nlp_server, args.nlp_port)
    syslog.info('loading wikiline2entity file....')
    wikilink_to_entity, entity_to_wikilink = build_entity_wikilink_map(
            charset_wrapper(open(args.entity_wiki_file)))
    syslog.info('finished loading wikiline2entity file')

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
            syslog.debug('plaintext=' + plaintext[:100].encode('utf-8'))
            mentions = get_plain_text_mention_info(line)
            syslog.debug('mention= ' + str(mentions))

            depparsed_output = depparse_paragraph(plaintext, nlp)
            if u'sentences' not in depparsed_output:
                # TODO: empty ?
                continue

            sentences = depparsed_output[u'sentences']

            """
            process_paragraph_single_entity(sentences, mentions,
                    wikilink_to_entity, entity_to_wikilink,
                    entity_sentence_outfile)
            """

            process_paragraph_multiple_entity(sentences, mentions,
                    wikilink_to_entity, entity_to_wikilink,
                    entity_sentence_outfile)

            xuxian.remember(args.task_id, doc['id'] + str(lineno))

        break

if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

