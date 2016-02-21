#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re
import xuxian

parser = xuxian.get_parser()
parser.add_argument('--wiki-file', required=True)

def foo(args):
    pass

if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(foo)

