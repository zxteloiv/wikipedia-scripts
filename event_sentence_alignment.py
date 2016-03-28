#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re, json
import redis
from itertools import permutations
import xuxian

parser = xuxian.get_parser()
parser.add_argument('--task-id', required=True, help='execution id')
parser.add_argument('--wiki-file', required=True,
        help='the /path/to/name of the wiki file to process')
parser.add_argument('--nlp-server', default='127.0.0.1')
parser.add_argument('--nlp-port', default=9000)

parser.add_argument('--redis-server', default='127.0.0.1')
parser.add_argument('--redis-port', default=6379)
parser.add_argument('--redis-db', default=0)

parser.add_argument('--sentence-entity', help='wiki sentence and entity')
parser.add_argument('--output-file')

from utils import charset_wrapper

def build_event_index(robj, event_schema, event_file):
    keyproperties, evtype, event = {}, None, []
    for line in charset_wrapper(open(event_schema_file)):
        line = line.rstrip()

        if line.startswith(u'\t'):
            event.append(line.lstrip())
        else:
            if evtype is not None:
                keyproperties[evtype] = event
            evtype = line
            event = []

    keyproperties[evtype] = event

    events = json.loads(open(event_file).read())

    for (ev_id, ev_data) in events.iteritems():
        if len(ev_data) <= 1:
            continue
        evtype = ev_data[0]

        if any() in (kvpair.split('\t') for kvpair in ev_data[1:]):
            pass

def mention_pairs(mentions):
    """
    processed = set()
    for ((m1, t1), (m2, t2)) in permutations(mentions, 2):
        if m1 == m2 or (m1, m2) in processed or (m2, m1) in processed:
            continue

        processed.add((m1, m2))
        yield ((m1, t1), (m2, t2))
    """
    pass

def sentence_reader(fileobj):
    pass

def process_paragraph_multiple_entity(sentences, mentions, robj, outfile):
    pass

def main(args):
    recovery_state = xuxian.recall(args.task_id)
    syslog = xuxian.log.system_logger

    # init global object
    robj = redis.StrictRedis(host=args.redis_server, port=args.redis_port,
            db=args.redis_db)

    # init output dump file
    #entity_outfile = xuxian.apply_dump_file('entity', args.single_entity_output_file)

    # iterate over data input
    pass

if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

