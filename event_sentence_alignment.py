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
parser.add_argument('--redis-db', default=1)

parser.add_argument('--key-schema-file', help='file of keys in event schema')
parser.add_argument('--event-file', help='event instance file')
parser.add_argument('--mid-entity-file', help='the mid \\t entity file to load')

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

def build_string_mid_table(mid_to_entity_file):
    """ Turn a tab-separated file <mid, string> into a dict <string, mid> """
    return dict((s.strip(), m) for (m, s) in (line.rstrip().split('\t')
        for line in charset_wrapper(open(mid_to_entity_file, 'r'))
        ))

def make_rkey(evtype, keyprops):
    rkey = evtype + u''.join(sorted(keyprops))
    return rkey.encode('utf-8')

def build_event_index(robj, event_schema, string_to_mid, event_file):
    """
    Read every event instance in the event_file, if it is valid by referring to 
    the event schema, write it into redis as:
        key = evtype + key_prop_1 + key_prop_2
        val = event { id:ev_id, type:evtype, properties: [(p1, v1), (p2, v2), ...]}
    """
    events = json.loads(open(event_file).read())
    syslog = xuxian.log.system_logger
    for (ev_id, ev_data) in events.iteritems():
        if len(ev_data) <= 1:
            continue
        evtype = ev_data[0]
        if evtype not in event_schema: continue
        try:
            # get the list of key properties contained in the event instance
            """
            keyprops = list((k, string_to_mid[v] if v in string_to_mid else v)
                    for (k, v) in (item.split(u'\t') for item in ev_data[1:])
                    if evtype in event_schema and k in event_schema[evtype])
                    """
            keyprops = list((k, v)
                    for (k, v) in (item.split(u'\t') for item in ev_data[1:])
                    if k in event_schema[evtype] and v.startswith(u'm.'))
        except Exception:
            syslog.debug(ev_id.encode('utf-8') + "\tkeypropsfailure")
            continue

        if len(keyprops) < 2: # key properties must be at least 2
            syslog.debug(ev_id.encode('utf-8') + "\tlessthan2")
            continue

        event = {u'id': ev_id, u'type': evtype}
        event[u'properties'] = [kvpair.split(u'\t') for kvpair in ev_data[1:]]

        rkey = make_rkey(evtype, list(x[1] for x in keyprops))
        rval = json.dumps(event)

        rtn = robj.set(rkey, rval)
        print str(rtn) + '\t' + rkey + '\t' + rval

def enumerate_rkeys(types, mentions):
    processed = set()
    for m1, m2 in permutations(mentions, 2):
        if m1[0] == m2[0] or (m1[0], m2[0]) in processed or (m2[0], m1[0]) in processed:
            continue

        processed.add((m1[0], m2[0]))
        for evtype in types:
            yield evtype, m1, m2

def sentence_reader(fileobj):
    sentence, mentions = None, []
    for line in fileobj:
        parts = line.rstrip().split(u'\t')
        if len(parts) <= 1:
            continue

        if parts[0] == u's':
            if sentence is not None and len(mentions) > 0:
                yield (sentence, mentions)
            sentence = parts[1]
            mentions = []
        elif parts[0] == u'm' and parts[1] != u'':
            mentions = [tuple(m.split(u',')) for m in parts[1:]]

    yield (sentence, mentions)

def output_ev_context(outfile, sentence, mention_pos, event):
    outfile.info('s\t' + sentence.encode('utf-8'))
    outfile.info((event[u'id'] + u'\t' + u'\t'.join(
        u",".join(
            (prop, val, mention_pos[val][0], mention_pos[val][1])
            if val in mention_pos
            else (prop, val, str(sentence.find(val)), str(sentence.find(val) + len(val)))
            )
        for prop, val in event[u'properties']
        if val in mention_pos or val in sentence
        )).encode('utf-8'))

def find_context_sentence_for_events(robj, outfile, event_schema, string_to_mid, sentence_entity_file):
    evtypes = event_schema.keys()
    for sentence, mentions in sentence_reader(charset_wrapper(open(sentence_entity_file))):

        mention_pos = dict((m[0], (m[1], m[2])) for m in mentions)

        rkeys = [make_rkey(evtype, (m1[0], m2[0])) for evtype, m1, m2 in enumerate_rkeys(evtypes, mentions)]
        for rkey in rkeys:
            data = robj.get(rkey)
            if data is None:
                continue

            evdata = json.loads(data)
            output_ev_context(outfile, sentence, mention_pos, evdata)

def main(args):
    recovery_state = xuxian.recall(args.task_id)
    syslog = xuxian.log.system_logger

    # init global object
    syslog.info('init redis object...')
    robj = redis.StrictRedis(host=args.redis_server, port=args.redis_port,
            db=args.redis_db)

    # init output dump file
    syslog.info('init output object...')
    outfile = xuxian.apply_dump_file('entity', args.output_file)

    syslog.info('init key properties...')
    event_schema = build_key_properties_table(args.key_schema_file)
    syslog.info('init string to mid table....')
    string_to_mid = build_string_mid_table(args.mid_entity_file)
    #syslog.info('write to redis....')
    #build_event_index(robj, event_schema, string_to_mid, args.event_file)

    syslog.info('init completed, now iterate over data...')

    # iterate over data input
    find_context_sentence_for_events(robj, outfile, event_schema, string_to_mid, args.sentence_entity)

if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

