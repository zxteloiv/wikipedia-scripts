# coding: utf-8

from __future__ import absolute_import
import argparse, logging, json, datetime, re
from .find_neighbor import bulk_query_wikidata
from utils.reader import reader, reader_for_list
from utils.redis_importer import get_redis_wikidata

def main():
    parser = argparse.ArgumentParser(description="find entities given a file list of dataid")
    parser.add_argument("-l", "--filelist", help='input of entity files')
    parser.add_argument("-o", "--output", help="output neighbor file")
    parser.add_argument("--quiet", action="store_true", help="mute the log")
    parser.add_argument("--debug", action="store_true", help="open debug log")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    find_properties(args)

def find_properties(args):
    output = open(args.output, 'w')
    for i, e in enumerate(reader_for_list(args.filelist)):
        t = e.get('type')
        if t == 'property':
            output.write(json.dumps(e) + '\n')

        if i % 10000 == 0:
            logging.info("%d item processed @ %s" % (i, datetime.datetime.now().strftime('%m-%d %H:%M:%S')))
            output.flush()

    output.close()

if __name__ == "__main__":
    main()

