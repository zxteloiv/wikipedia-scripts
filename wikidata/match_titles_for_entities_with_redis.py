# coding: utf-8
from __future__ import absolute_import
from .reader import reader, reader_for_list as listreader
import argparse, logging, json, datetime

import opencc
cc = opencc.OpenCC()

from utils.redis_importer import get_redis_redir, get_redis_title
from utils.cirrus import redis_redirect as redirect
from utils.cirrus import redis_canonicalize as canonicalize
from utils.cirrus import query_redis_idx as query_idx

def bulk_query_wikipage(title_idx, titles, redir_idx):
    filelist = sorted(set(filter(None, (query_idx(t, title_idx) for t in titles))))
    logging.info('there are %d files to read, given these %d titles' % (len(filelist), len(titles)))
    texts = {}
    # scan all filelist
    for f in filelist:
        logging.info("reading file %s .." % f)
        for page in reader(f):
            try:
                title = canonicalize(page['title'], redir_idx)
                if title in titles:
                    texts[title] = page['text']
            except:
                continue
    return texts

def process_entities(args):
    wikisite = args.wikisite
    if wikisite == "zhwiki":
        title_db, redir_db = 1, 3
    elif wikisite == "enwiki":
        title_db, redir_db = 4, 5

    title_idx = get_redis_title(title_db)
    redir_idx = get_redis_redir(redir_db)

    logging.info('collect titles for entities...')

    # thousands level
    title_bulk = set()
    for i, entity in enumerate(reader(args.entities)):
        try:
            title = entity['sitelinks'][wikisite]['title']
        except:
            continue
        title = canonicalize(title, redir_idx)
        title_bulk.add(title)
    logging.info("got %d title out of %d entities" % (len(title_bulk), i))

    logging.debug('====================')
    logging.debug('required: ' + u','.join(title_bulk).encode('utf-8'))

    title_text = bulk_query_wikipage(title_idx, title_bulk, redir_idx)
    logging.info("found page amount: %d" % len(title_text))

    logging.debug('====================')
    logging.debug('got text: ' + u','.join(title_text.keys()).encode('utf-8'))

    output = open(args.output, 'w')
    for i, entity in enumerate(reader(args.entities)):
        try:
            title = entity['sitelinks'][wikisite]['title']
        except:
            title = ""

        title = canonicalize(title, redir_idx)
        text = title_text.get(title)
        if text is None:
            if title:
                logging.warning("specified title %s not found" % title.encode('utf-8'))
            text = ""
        else:
            logging.debug("title %s found" % title.encode('utf-8'))

        entity[wikisite] = text
        output.write(json.dumps(entity) + '\n')

        if i % 500 == 0:
            logging.info("%d entities processed" % i)
            output.flush()
    output.close()

def main():
    parser = argparse.ArgumentParser(description="match entities with the corresponding wikipedia text")
    parser.add_argument("-e", "--entities", help="input entity file")
    parser.add_argument("-w", "--wikisite", choices=['enwiki', 'zhwiki'],
            help="the wiki site needed, e.g. enwiki, zhwiki")
    parser.add_argument("-o", "--output", help="output entity file decorated by wikipedia text")
    parser.add_argument("-q", "--quiet", action="store_true", help="mute the log")
    parser.add_argument("--debug", action="store_true", help="open debug log")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    process_entities(args)

if __name__ == "__main__":
    main()

