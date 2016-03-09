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

parser.add_argument('--entity-output-file', required=True,
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

def process_paragraph(sentences, mentions,
        wikilink_to_entity, entity_to_wikilink, redirect_map,
        outfile):
    """
    To produce a deproute between any two of the entities in a sentence.
    Produce each line: entity1, entity2, deproute, and sentence separated by tab
    """
    syslog = xuxian.log.system_logger

    sentence_to_mention = build_sentence_to_mention_table(sentences, mentions)
    syslog.debug("-=-=-=-=-=-=-=-= sentence tokens =-=-=-=-=-=-=-=-\n" + "\n".join(
            "{0}\t{1}\t{2}\t{3}\t{4}".format(
                sid, tid, t['characterOffsetBegin'], t['characterOffsetEnd'],
                t['originalText'].encode('utf-8')
                ) for sid in xrange(len(sentences))
            for tid, t in enumerate(sentences[sid]['tokens'])
            ))
    syslog.debug('-=-=-=-=-=-=-=-= mentions =-=-=-=-=-=-=-=-=-\n' + '\n'.join(
        "{0}\t{1}\t{2}\t{3}".format(
            m[0], m[1], m[2].encode('utf-8'), m[3].encode('utf-8')
            ) for m in mentions
        ))
    syslog.debug('sentence_to_mention=' + (
        " ".join(str(i) + '=>' + str(x) for (i, x) in enumerate(sentence_to_mention))
        ))

    for sentence_id in xrange(len(sentence_to_mention)):
        mentions = sentence_to_mention[sentence_id]
        if len(mentions) <= 1:
            continue

        sentence = sentences[sentence_id]
        tokens = sentence[u'tokens']
        sentence_offset = tokens[0]['characterOffsetBegin']
        sentence_content = restore_sentence_from_tokens(tokens)
        syslog.debug('sentence=%d ' % sentence_id +
                'mentions=' + str(mentions))

        outfile.info((u"s\t" + sentence_content).encode('utf-8'))

        outfile.info((u"m\t" + u"\t".join(
            x[0], x[1] - sentence_offset, x[2] - sentence_offset
            for x in get_output_entity_mention_token(mentions)
            )).encode('utf-8'))

def get_output_entity_mention_token(mentions):
    for mention, token_list in mentions:
        entity = href_to_entity(mention, wikilink_to_entity, redirect_map)
        if not entity: continue

        yield entity, mention[0], mention[1]

def tokenize_paragraph(para, nlp, response_encoding=None):
    return nlp.annotate(para.encode('utf-8'),
            properties={'outputFormat':'json', 'annotators':'tokenize,ssplit'},
            response_encoding=response_encoding)

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

    # iterate over data input
    for doc in docs:
        syslog.info('to process doc_title=' + doc['title'].encode('utf-8'))
        for (lineno, line) in enumerate(doc['text']):
            # at the correct time point, clear the recovery state
            if recovery_state == doc['title'] + str(lineno):
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

            tokenized = tokenize_paragraph(plaintext, nlp)
            if u'sentences' not in tokenized:
                # TODO: empty ?
                continue

            sentences = tokenized[u'sentences']

            syslog.debug('to process doc_title=' + doc['title'].encode('utf-8')
                    + '\tdoc_line=' + plaintext[:80].encode('utf-8'))

            process_paragraph(sentences, mentions,
                    wikilink_to_entity, entity_to_wikilink, redirect_map,
                    entity_pair_outfile)

            xuxian.remember(args.task_id, (doc['title'] + unicode(lineno)).encode('utf-8'))

if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

