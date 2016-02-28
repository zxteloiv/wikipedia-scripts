#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re
from itertools import permutations
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

parser.add_argument('--wiki-redirect-file')

parser.add_argument('--single-entity-output-file', required=True,
        help='output file each line with an entity and the sentence where it appears')

parser.add_argument('--entity-pair-output-file', required=True,
        help='output file each line with an entity pair and its dependency route')

from wiki_doc import wikiobj_to_doc
from utils import charset_wrapper, init_corenlp
from entity_wikilink import build_entity_wikilink_map, build_redirect_wikilink_map
from entity_wikilink import href_to_wikilink, href_to_entity
from entity_mentions import get_plain_text, get_plain_text_mention_info
from depparse import depparse_paragraph, vertices_route_to_deproute
from depparse import get_token_id_list_by_mention, restore_sentence_from_tokens
from depparse import find_sentence_by_offset, get_sentence_id
from dijkstra import dijkstra_path_for_regions

def process_paragraph_single_entity(sentences, mentions,
        wikilink_to_entity, entity_to_wikilink, redirect_map,
        outfile):
    # formatted output each entity mention
    syslog = xuxian.log.system_logger
    Dict = xuxian.log.LogDict
    for (mstart, mend, href, string) in mentions:
        entity = href_to_entity(href, wikilink_to_entity, redirect_map)
        if not entity: continue

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
                entity, href,
                mstart - sentence_offset, mend - sentence_offset,
                find_sentence_by_offset(sentences, mstart, mend)
                ))

def build_sentence_to_mention_table(sentences, mentions):
    # prepare the lookup structure
    sentence_to_mention = [[] for i in xrange(len(sentences))]
    for mention in mentions:
        (mstart, mend, href, _) = mention
        sentence_id = get_sentence_id(sentences, mstart, mend)
        token_list = get_token_id_list_by_mention(sentences[sentence_id],
                mstart, mend)
        sentence_to_mention[sentence_id].append((mention, token_list))

    return sentence_to_mention

def mention_pairs(mentions):
    processed = set()
    for ((m1, t1), (m2, t2)) in permutations(mentions, 2):
        if m1 == m2 or (m1, m2) in processed or (m2, m1) in processed:
            continue

        processed.add((m1, m2))
        yield ((m1, t1), (m2, t2))

def process_paragraph_multiple_entity(sentences, mentions,
        wikilink_to_entity, entity_to_wikilink, redirect_map,
        outfile):
    """
    To produce a deproute between any two of the entities in a sentence.
    Produce each line: entity1, entity2, deproute, and sentence separated by tab
    """
    syslog = xuxian.log.system_logger

    sentence_to_mention = build_sentence_to_mention_table(sentences, mentions)
    syslog.debug('sentence_to_mention=' + (
        " ".join(str(i) + '=>' + str(x) for (i, x) in enumerate(sentence_to_mention))
        ))

    # edge set for every sentence
    sentence_edges = [dict(((e['governor'] - 1, e['dependent'] - 1, 1), i) 
        for i, e in enumerate(sentence['basic-dependencies']) if e['dep'] != 'ROOT')
        for sentence in sentences]

    for sentence_id in xrange(len(sentence_to_mention)):
        mentions = sentence_to_mention[sentence_id]
        if len(mentions) <= 1:
            continue

        sentence = sentences[sentence_id]
        tokens = sentence[u'tokens']
        sentence_offset = tokens[0]['characterOffsetBegin']
        syslog.debug('sentence=%d ' % sentence_id +
                'mentions=' + str(mentions))

        for ((m1, t1), (m2, t2)) in mention_pairs(mentions):
            e1 = href_to_entity(m1[2], wikilink_to_entity, redirect_map)
            e2 = href_to_entity(m2[2], wikilink_to_entity, redirect_map)
            if not e1 or not e2: continue

            mindist, minroute = dijkstra_path_for_regions(t1, t2,
                    tokens, sentence_edges[sentence_id].keys())

            syslog.debug('----------------------------------------------------')
            syslog.debug('mindist=' + str(mindist) + ';minroute=' + str(minroute)
                    + ';src=' + tokens[minroute[0]]['originalText'].encode('utf-8')
                    + ';dest=' + tokens[minroute[-1]]['originalText'].encode('utf-8')
                    + ';tokens=' + ' '.join(t['originalText'].encode('utf-8')
                        for t in tokens)
                    )

            deproute_string = vertices_route_to_deproute(minroute, 
                    sentence_edges[sentence_id], tokens,
                    sentence['basic-dependencies'])

            syslog.debug('deproute_string=====>\t' + deproute_string.encode('utf-8'))
            syslog.debug('----------------------------------------------------')

            outfile.info(u"{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}".format(
                e1, m1[2], m1[0] - sentence_offset, m1[1] - sentence_offset,
                e2, m2[2], m2[0] - sentence_offset, m2[1] - sentence_offset,
                deproute_string, restore_sentence_from_tokens(tokens)
                ).encode('utf-8'))
    pass

def main(args):
    recovery_state = xuxian.recall(args.task_id)
    syslog = xuxian.log.system_logger
    Dict = xuxian.log.LogDict

    # init global object
    docs = wikiobj_to_doc(charset_wrapper(open(args.wiki_file)))
    nlp = init_corenlp(args.nlp_server, args.nlp_port)
    syslog.info('loading wikiline2entity file....')
    wikilink_to_entity, entity_to_wikilink = build_entity_wikilink_map(
            charset_wrapper(open(args.entity_wiki_file)))
    syslog.info('loading redirect file....')
    redirect_map = build_redirect_wikilink_map(
            charset_wrapper(open(args.wiki_redirect_file)))
    syslog.info('finished init global object')

    # init output dump file
    entity_outfile = xuxian.apply_dump_file('entity',
            args.single_entity_output_file)
    entity_pair_outfile = xuxian.apply_dump_file('entity-pair',
            args.entity_pair_output_file)

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
            syslog.debug(Dict({'plaintext' : plaintext[:100].encode('utf-8'),
                'mention':str(mentions)}))

            depparsed_output = depparse_paragraph(plaintext, nlp)
            if u'sentences' not in depparsed_output:
                # TODO: empty ?
                continue

            sentences = depparsed_output[u'sentences']

            process_paragraph_single_entity(sentences, mentions,
                    wikilink_to_entity, entity_to_wikilink, redirect_map,
                    entity_outfile)

            process_paragraph_multiple_entity(sentences, mentions,
                    wikilink_to_entity, entity_to_wikilink, redirect_map,
                    entity_pair_outfile)

            xuxian.remember(args.task_id, doc['id'] + str(lineno))

        break

if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

