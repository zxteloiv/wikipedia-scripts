# coding: utf-8

from __future__ import absolute_import
import argparse, logging, json, datetime, re

from utils.reader import reader
from utils.redis_importer import get_redis_wikidata
from utils.wikidata import query_redis_idx as query_entity, claim_value

def bulk_query_wikidata(qids, wikidata_idx):
    filelist = sorted(set(filter(None, (query_entity(idx, wikidata_idx) for idx in qids))))
    logging.info('there are %d files to read for %d entities' % (len(filelist), len(qids)))
    entities = {}
    for f in filelist:
        logging.info("reading file %s ..." % f)
        for i, entity in enumerate(reader(f)):
            try:
                qid = entity['id']
            except KeyError:
                continue

            if qid in qids and qid not in entities:
                entities[qid] = entity

            if i % 10000 == 0:
                logging.info("%d items processed, current %s" % (i, qid))

        logging.info("%d items cumulated after reading file %s" % (len(entities), f))
    return entities

def find_neighbor(args):
    wikidata_idx = get_redis_wikidata()
    es = list(x for x in reader(args.entities))
    logging.info('read %d input entities' % len(es))
    output = open(args.output, 'w')
    for l in xrange(args.depth):
        if len(es) == 0 and l < args.depth:
            logging.info("early breaking at layer %d because of empty entities" % l)
            break

        logging.info('find %d-hop neighbors for %d inputs' % (l, len(es)))
        qids = set(filter(lambda v: v is not None and re.match('^Q\d+$', v),
            (claim_value(c) for e in es for _, cs in e['claims'].iteritems() for c in cs)))
        logging.debug('qids: %s' % u','.join(qids).encode('utf-8'))
        logging.info('there\'re %d neighbors to read' % len(qids))
        es_d = bulk_query_wikidata(qids, wikidata_idx)
        es = [x for x in es_d.itervalues()]

        for e in es:
            output.write(json.dumps(e) + '\n')

def main():
    parser = argparse.ArgumentParser(description="find neighbors for a file list of wikidata")
    parser.add_argument("-e", "--entities", help="input entity file")
    parser.add_argument("-o", "--output", help="output neighbor file")
    parser.add_argument("-d", "--depth", type=int, default=2, help="choose neighbors with depth")
    parser.add_argument("--quiet", action="store_true", help="mute the log")
    parser.add_argument("--debug", action="store_true", help="open debug log")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    find_neighbor(args)

if __name__ == "__main__":
    main()

