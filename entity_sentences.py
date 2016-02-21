#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re
import xuxian

parser = xuxian.get_parser()
parser.add_argument('--wiki-file', required=True)

from wiki_doc import charset_wrapper, wikiobj_to_doc

def main(args):
    docs = wikiobj_to_doc(charset_wrapper(open(args.wiki_file)))
    for doc in docs:
        for line in doc['text']:
            # every line is a paragraph in wikipedia
            plaintext = get_plain_text(line)
            mentions = get_plain_text_mention_info(line)

            pass


if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

