# coding: utf-8

from __future__ import absolute_import

import sys, os.path, re
import argparse
import json
import logging

def main():
    parser = argparse.ArgumentParser(description="Build redirects map and category hierarchy at the same time")
    parser.add_argument("input", help="input file")
    parser.add_argument("-r", "--redir_output", default="disable", help="redirects output filename")
    parser.add_argument("-c", "--category_output", default="disable", help="category hierarchy output filename")
    args = parser.parse_args()

    infile = open(args.input)
    rfile = open(args.redir_output, "w") if args.redir_output != "disable" else None
    cfile = open(args.category_output, "w") if args.category_output != "disable" else None

    process_file(infile, rfile, cfile)

    infile.close()
    if rfile: rfile.close()
    if cfile: cfile.close()

def process_file(infile, rfile, cfile):
    if rfile is None and cfile is None: return
    for line in infile:
        page = json.loads(line)

        if rfile:
            for x in page['redirects']:
                rfile.write(x.encode('utf-8') + '\n')

        # ns=14 is the namespace for Category, for more information,
        # refer to: https://www.mediawiki.org/wiki/Manual:Namespace
        if cfile and page['namespace'] == 14:
            for x in page['categories']:
                cfile.write((page['title'] + u'\t' + x).encode('utf-8') + '\n')

if __name__ == "__main__":
    main()
