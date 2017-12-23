# coding: utf-8

from __future__ import absolute_import
import pymongo
import logging
from utils.reader import reader


def main(filename, dbname, colname):
    conn = pymongo.MongoClient()
    db = conn.get_database(dbname)
    col = db.get_collection(colname)

    logging.getLogger().setLevel(logging.INFO)

    for obj in reader(filename):
        try:
            col.insert_one(obj)
            logging.info('inserted id=%s' % str(obj['id']))
        except pymongo.errors.DuplicateKeyError:
            logging.info('duplicated id=%s' % str(obj['id']))
            continue
        except Exception:
            logging.warning('exception when writing obj %s' % str(obj['id']))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print "Usage: %s filename db collection"
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
