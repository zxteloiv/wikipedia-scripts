# coding: utf-8

from __future__ import absolute_import
import argparse, logging, json, datetime, re, os, os.path

from utils.reader import reader
from utils.redis_importer import get_redis_wikidata
from utils.wikidata import get_neighbor_entity

def find_neighbor(args):

    filelist = [l.rstrip() for l in args.filelist]
    
    qids = set(v for _, _, v in next_neighbor_id(reader(args.entities)))

    written_qids = set()
    output = open(args.output, 'w')
    for d in xrange(args.depth):
        logging.info('========> %d-hop neighbors amount: %d' % (d + 1, len(qids)))

        if args.debug:
            logging.debug(u','.join(qids).encode('utf-8'))
            break

        next_qids = set()
        for i, e in enumerate(next_required_entity_from_files(qids, filelist)):
            if e['id'] not in written_qids:
                output.write(json.dumps(e) + '\n')
                written_qids.add(e['id'])

                for v in next_neighbor_of_entity(e):
                    next_qids.add(v)

            if i % 1000 == 0:
                logging.info("found %d neighbors so far by reading files, %d have been written" % (i, len(written_qids)))
                output.flush()

        qids = next_qids

    output.close()
    

def next_neighbor_id(iterable):
    for i, e in enumerate(iterable):
        if i % 10000 == 0:
            logging.info('read %d input entities for neighbors' % i)

        for v in next_neighbor_of_entity(e):
            yield e, e['id'], v
    logging.info('read %d input entities for neighbors' % i)

def next_neighbor_of_entity(e):
    for c in e['claims'].itervalues():
        for snak in c:
            v = get_neighbor_entity(snak)
            if v is not None:
                yield v

def next_required_entity_from_files(qids, filelist):
    i = 0
    for f in filelist:
        logging.info("reading file %s ..." % f)
        for e in reader(f):
            if i % 10000 == 0:
                logging.info('read %d input entities in file' % i)

            i += 1
            qid = e['id']
            if qid in qids:
                yield e

def main():
    parser = argparse.ArgumentParser(description="find neighbors for a file list of wikidata")
    parser.add_argument("-e", "--entities", help="input entity file")
    parser.add_argument("-o", "--output", help="output neighbor file")
    parser.add_argument("-l", "--filelist", type=file, help="")
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

