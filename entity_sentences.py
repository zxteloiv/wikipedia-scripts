#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re
import xuxian

parser = xuxian.get_parser()
parser.add_argument('--wiki-file', required=True)
parser.add_argument('--nlp-server', default='127.0.0.1')
parser.add_argument('--nlp-port', default=9000)

parser.add_argument('--entity-wiki-file', required=True)

from wiki_doc import wikiobj_to_doc
from utils import charset_wrapper

def main(args):
    docs = wikiobj_to_doc(charset_wrapper(open(args.wiki_file)))
    nlp = init_corenlp(args.nlp_server, args.nlp_port)
    for doc in docs:
        for line in doc['text']:
            # every line is a paragraph in wikipedia
            plaintext = get_plain_text(line)
            mentions = get_plain_text_mention_info(line)

            pass


if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

