# coding: utf-8

import re
import redis

def build_entity_wikilink_map(obj, r):
    syslog = xuxian.log.system_logger
    for line in obj:
        entity, wikilink = line.strip().split('\t')
        wikilink = upper_first_letter(wikilink)

        if r:
            rtn = r.set('wiki2mid' + wikilink.encode('utf-8'), entity.encode('utf-8'))
            syslog.debug('add key=' + wikilink.encode('utf-8') + '\tval=' + entity.encode('utf-8'))

def href_to_wikilink(href):
    return upper_first_letter(href.replace(u' ', u'_'))

def upper_first_letter(text):
    return text[0].upper() + text[1:] if text else ""

def build_redirect_wikilink_map(obj, r):
    for line in obj:
        link1, link2 = line.rstrip().split('\t')
        link1, link2 = upper_first_letter(link1), upper_first_letter(link2)

        if r:
            r.set('redir' + link1.encode('utf-8'), link2.encode('utf-8'))

def href_to_entity(href, robj=None):
    link = href_to_wikilink(href)

    res = robj.get('redir' + link.encode('utf-8'))
    if res is not None:
        link = res.decode('utf-8')

    res = robj.get('wiki2mid' + link.encode('utf-8'))
    if res is not None:
        entity = res.decode('utf-8')
    else:
        entity = None

    return entity

if __name__ == "__main__":
    import sys
    sys.path.insert(1, 'lib/py-xuxian')
    def main(args):
        """ Read and write data into remote redis server """
        from utils import charset_wrapper
        import redis
        r = redis.StrictRedis(host='172.18.28.118')
        syslog = xuxian.log.system_logger
        syslog.info('loading wikiline2entity file....')
        build_entity_wikilink_map(charset_wrapper(open(args.mid2wiki)), r)
        syslog.info('loading redirect file....')
        build_redirect_wikilink_map(charset_wrapper(open(args.redirect)), r)
        syslog.info('finished init global object')

    def test(args):
        """ check for all key if they still exist in remote redis server """
        from utils import charset_wrapper
        import redis
        r = redis.StrictRedis(host='172.18.28.118')
        syslog = xuxian.log.system_logger

        for entity, wikilink in (line.strip().split('\t') for line in charset_wrapper(open(args.mid2wiki))):
            wikilink = upper_first_letter(wikilink)
            res = r.get('wiki2mid' + wikilink.encode('utf-8'))
            if res != entity.encode('utf-8'):
                syslog.info((u'err_wiki2mid\tkey=' + wikilink + u'\tval=' + entity).encode('utf-8'))
            else:
                syslog.info('ok_wiki2mid\tkey=' + wikilink.encode('utf-8'))

        for link1, link2 in (line.rstrip().split('\t') for line in charset_wrapper(open(args.redirect))):
            link1, link2 = upper_first_letter(link1), upper_first_letter(link2)

            res = r.get('redir' + link1.encode('utf-8'))
            if res != link2.encode('utf-8'):
                syslog.info((u'err_redir\tkey=' + link1 + u'\tval=' + link2).encode('utf-8'))
            else:
                syslog.info('ok_redir\tkey=' + link1.encode('utf-8'))

    import xuxian
    parser = xuxian.get_parser()
    parser.add_argument('--mid2wiki')
    parser.add_argument('--redirect')
    xuxian.parse_args()
    xuxian.run(test)

