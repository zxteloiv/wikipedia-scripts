# coding: utf-8

from __future__ import absolute_import
import argparse, logging, json, datetime, re
from .find_neighbor import bulk_query_wikidata
from utils.redis_importer import get_redis_wikidata

def main():
    parser = argparse.ArgumentParser(description="find entities given a file list of dataid")
    parser.add_argument("entities", help="input entity file")
    parser.add_argument("-o", "--output", help="output neighbor file")
    parser.add_argument("--quiet", action="store_true", help="mute the log")
    parser.add_argument("--debug", action="store_true", help="open debug log")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    find_entities(args)

def find_entities(args):
    wikidata_idx = get_redis_wikidata()
    qids = set(filter(lambda v: v is not None and re.match('^Q\d+$', v),
        (l.rstrip() for l in open(args.entities))))
    entities = bulk_query_wikidata(qids, wikidata_idx)
    output = open(args.output, 'w')
    for e in entities.itervalues():
        output.write(json.dumps(e) + '\n')
    output.close()

if __name__ == "__main__":
    main()


