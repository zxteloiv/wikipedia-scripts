# coding: utf-8

from __future__ import absolute_import
import pymongo
import logging
import json
from utils.reader import reader
import gzip


def main(filename, subsite):
    conn = pymongo.MongoClient()
    db = conn.wikipedia
    col = db.get_collection(subsite)

    logging.getLogger().setLevel(logging.INFO)

    unzipped_input = gzip.open(filename)
    while True:
        line = unzipped_input.readline()
        if not line: break

        index = json.loads(line)
        content = json.loads(unzipped_input.readline())

        try:
            page = {}
            page['id'] = index['index']['_id']
            page['type'] = index['index']['_type']
            page['namespace'] = content['namespace']
            page['categories'] = content['category']
            page['score'] = content['score'] if 'score' in content else 0
            page['popularity_score'] = content['popularity_score'] if 'popularity_score' in content else 0
            page['text'] = content['text']
            page['opening_text'] = content['opening_text'] if 'opening_text' in content else ''
            page['source_text'] = content['source_text'] if 'source_text' in content else ''
            page['title'] = content['title']
            page['language'] = content['language']
            page['redirects'] = [r['title'] for r in content['redirect']]
        except:
            logging.warning("invalid id=%s\t%s" % (index['index']['_id'],
                                                   json.dumps(content)))
            continue

        try:
            col.insert_one(page)
            logging.info('inserted id=%s, title=%s' % (
                         str(page['id']), page['title'].encode('utf-8')))
        except pymongo.errors.DuplicateKeyError:
            logging.info('duplicated id=%s, title=%s' % (
                         str(page['id']), page['title'].encode('utf-8')))
            continue
        except Exception:
            logging.warning('exception when writing id=%s, title=%s' % (
                            str(page['id']), page['title'].encode('utf-8')))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print "Usage: %s filename enwiki/zhwiki"
    else:
        main(sys.argv[1], sys.argv[2])
