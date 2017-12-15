# coding: utf-8

from __future__ import absolute_import
import pymongo
import logging
from utils.reader import reader


def main(filename):
    conn = pymongo.MongoClient()
    db = conn.wikidata
    col = db.wikidata

    logging.getLogger().setLevel(logging.INFO)

    for obj in reader(filename):
        try:
            col.insert_one(obj)
            logging.info('inserted id=%s' % str(obj['id']))
        except DuplicateKeyError:
            logging.info('duplicated id=%s' % str(obj['id']))
            continue
        except Exception:
            logging.warning('exception when writing obj %s' % str(obj['id']))


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
