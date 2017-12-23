# coding: utf-8

from __future__ import absolute_import
import pymongo
import logging
from utils.reader import reader_for_list


def main(subsite, filelist):
    conn = pymongo.MongoClient()
    db = conn.wikipedia
    col = db.get_collection(subsite)

    logging.getLogger().setLevel(logging.INFO)

    for obj in reader_for_list(filelist):
        try:
            col.insert_one(obj)
            logging.info('inserted id=%s, title=%s' % (str(obj['id']), obj['title'].encode('utf-8')))
        except pymongo.errors.DuplicateKeyError:
            logging.info('duplicated id=%s, title=%s' % (str(obj['id']), obj['title'].encode('utf-8')))
            continue
        except Exception:
            logging.warning('exception when writing id=%s, title=%s' % (str(obj['id']), obj['title'].encode('utf-8')))


if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2])
