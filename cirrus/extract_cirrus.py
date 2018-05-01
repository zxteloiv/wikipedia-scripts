# coding: utf-8

from __future__ import absolute_import

import sys, os.path, re
import logging
import json
import argparse
import gzip

from .cirrus_extract import NextFile, OutputSplitter

def main():
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
            description="Select the useful fields from cirrussearch dump of wikipedia")

    parser.add_argument("input", help="Cirrus json wiki dump file in gzip format")

    parser.add_argument("-o", "--output", default="text",
                        help="directory for extracted files")
    parser.add_argument("-b", "--bytes", default="10M",
                        help="maximum bytes per output file (default %(default)s)",
                        metavar="n[KMG]")

    # file size 
    args = parser.parse_args()
    MIN_FILE_SIZE = 200 * 1024
    try:
        power = 'kmg'.find(args.bytes[-1].lower()) + 1
        file_size = int(args.bytes[:-1]) * 1024 ** power
        if file_size < MIN_FILE_SIZE:
            raise ValueError()
    except ValueError:
        logging.error('Insufficient or invalid size: %s', args.bytes)
        return

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    input_file = args.input
    output_path = args.output
    if not os.path.isdir(output_path):
        try:
            os.makedirs(output_path)
        except:
            logging.error('Could not create: %s', output_path)
            return

    process_dump(input_file, output_path, file_size)

def process_dump(input_file, output_path, file_size):
    unziped_input = gzip.open(input_file)
    output = OutputSplitter(NextFile(output_path), file_size, compress=False)

    while True:
        line = unziped_input.readline()
        if not line: break

        index = json.loads(line)
        content = json.loads(unziped_input.readline())

        # output.write(some utf-8 buf)
        try:
            page = {}
            page['id'] = index['index']['_id']
            page['type'] = index['index']['_type']
            page['namespace'] = content['namespace']
            page['categories'] = content['category']
            page['score'] = content['score'] if 'score' in content else 0
            page['popularity_score'] = content['popularity_score'] if 'popularity_score' in content else 0
            page['text'] = content['text']
            page['title'] = content['title']
            page['redirects'] = [r['title'] for r in content['redirect']]
        except:
            logging.warning("invalid id=%s\t%s" % (index['index']['_id'], json.dumps(content)))
            continue

        output.write(json.dumps(page) + '\n')
        logging.info((u"INFO:\t%s\t%s" % (page['id'], page['title'])).encode('utf-8'))


if __name__ == "__main__":
    main()

