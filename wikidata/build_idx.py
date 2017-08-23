# coding: utf-8

from __future__ import absolute_import
from .reader import reader
import datetime
import argparse, logging

def main():
    parser = argparse.ArgumentParser(description="build qid to filename, lineno index")
    parser.add_argument("-l", "--filelist", help='input of entity files')
    parser.add_argument("-o", "--output", help='output index, tsv file: Qid, filename and lineno')

    parser.add_argument("-q", "--quiet", action="store_true", help="mute the log")
    parser.add_argument("--debug", action="store_true", help="open debug log")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    build_index(args)

def build_index(args):
    def dataextractor(filelist):
        for f in open(filelist):
            f = f.rstrip()
            for i, entity in enumerate(reader(f)):
                qid = entity['id']
                yield qid, f, i + 1

    output = open(args.output, 'w')
    for i, (qid, f, lineno) in enumerate(dataextractor(args.filelist)):
        output.write((u'%s\t%s\t%d' % (qid, f, lineno)).encode('utf-8') + '\n')

        if i % 100 == 0:
            output.flush()
        if i % 1000 == 0:
            logging.info(("%d entities written" % i) + datetime.datetime.now().strftime('%m%d%-H%M%S'))

if __name__ == "__main__":
    main()

