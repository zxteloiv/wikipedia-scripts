# coding: utf-8
from __future__ import absolute_import

import json, logging
import redis

host = '127.0.0.1'
port = 6379
db = 1

from utils.cirrus import openfile

def get_redis_redir(db=3):
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r

def get_redis_title(db=1):
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r

def arity_2(tsvfile, prefix=u""):
    r = redis.StrictRedis(host=host, port=port, db=db)
    fail = 0
    for i, l in enumerate(openfile(tsvfile)):
        arr = l.decode('utf-8').rstrip().split('\t')
        rtn = r.set(prefix + arr[0].encode('utf-8'), arr[1].encode('utf-8'))
        if not rtn:
            fail += 1
            logging.info('%d record inserted, failure %s%s -> %s' % (i, prefix, arr[0].encode('utf-8'), arr[1].encode('utf-8')))
        if i % 5000 == 0:
            logging.info('%d record inserted, current %s%s -> %s' % (i, prefix, arr[0].encode('utf-8'), arr[1].encode('utf-8')))
    logging.info('db %d inserted %d entries' % (db, i))

def check_2(tsvfile, prefix=u""):
    r = redis.StrictRedis(host=host, port=port, db=db)
    for i, l in enumerate(openfile(tsvfile)):
        arr = l.decode('utf-8').rstrip().split('\t')
        data = r.get(prefix + arr[0].encode('utf-8'))
        if data != arr[1].encode('utf-8'):
            logging.info('data not found: %s' % (prefix + arr[0].encode('utf-8')))
        if i % 5000 == 0:
            logging.info('%d record checked' % i)
    logging.info('db %d inserted %d entries' % (db, i))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="insert into redis")
    parser.add_argument('-i', '--input', help='tsv file', required=True)
    parser.add_argument('--db', type=int, help='db number to insert')
    parser.add_argument('--host', default='127.0.0.1', help='db file')
    parser.add_argument('--port', default=6379, help='db port')
    parser.add_argument('--prefix', help="the prefix to add before key", required=True)
    parser.add_argument('--checking', action="store_true", help="the prefix to add before key")
    args = parser.parse_args()

    global db
    global host
    global port

    if args.db:
        db = args.db
    if args.host:
        host = args.host
    if args.port:
        port = args.port
    
    logging.getLogger().setLevel(logging.INFO)
    if args.checking:
        check_2(args.input, args.prefix)
    else:
        arity_2(args.input, args.prefix)

if __name__ == "__main__":
    main()

