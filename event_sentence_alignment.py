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
parser.add_argument('--task-id', default='testtask', help='execution id')
parser.add_argument('--nlp-server', default='127.0.0.1')
parser.add_argument('--nlp-port', default=9000)

parser.add_argument('--redis-server', default='127.0.0.1')
parser.add_argument('--redis-port', default=6379)
parser.add_argument('--redis-db', default=0)

parser.add_argument('--key-schema-file', help='file of keys in event schema')
parser.add_argument('--event-file', help='event instance file')
parser.add_argument('--sentence-entity', help='wiki sentence and entity')
parser.add_argument('--output-file')

from utils import charset_wrapper

def build_key_properties_table(event_schema_file):
    """
    Read the schema file, return a object as {event_type: set_of_key_properties}
    """
    keytable, evtype, event = {}, None, set()
    for line in charset_wrapper(open(event_schema_file)):
        line = line.rstrip()

        if line.startswith(u'\t'):
            event.add(line.lstrip())
        else:
            if evtype is not None:
                keytable[evtype] = event
            evtype = line
            event = set()

    keytable[evtype] = event
    return keytable

def build_event_index(robj, event_schema, event_file):
    """
    Read every event instance in the event_file, if it is valid by referring to 
    the event schema, write it into redis as:
        key = evtype + key_prop_1 + key_prop_2
        val = event { id:ev_id, type:evtype, prop1:val1, prop2:val2, ... }
    """
    events = json.loads(open(event_file).read())
    for (ev_id, ev_data) in events.iteritems():
        if len(ev_data) <= 1:
            continue
        evtype = ev_data[0]
        try:
            # get the list of key properties contained in the event instance
            keyprops = dict((k, v)
                    for (k, v) in (item.split(u'\t') for item in ev_data[1:])
                    if evtype in event_schema and k in event_schema[evtype])
        except Exception:
            continue

        if len(keyprops) < 2: # key properties must be at least 2
            continue

        event = {u'id': ev_id, u'type': evtype}
        event.update(kvpair.split(u'\t') for kvpair in ev_data[1:])

        rkey = evtype.encode('utf-8') + ''.join(x[1].encode('utf-8') for x in keyprops.items())
        rval = json.dumps(event)

        rtn = robj.set(rkey, rval)
        print str(rtn) + '\t' + rkey + '\t' + rval

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

    event_schema = build_key_properties_table(args.key_schema_file)
    build_event_index(robj, event_schema, args.event_file)

    # iterate over data input
    pass

if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

