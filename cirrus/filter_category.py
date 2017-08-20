# coding: utf-8

import sqlite3
import json
import argparse
import re, sys, os.path
import logging
import opencc

cc = opencc.OpenCC()

class CategoryResourcesPyNative(object):
    def __init__(self, rfile, cfile):
        self.rfile = rfile
        self.cfile = cfile

        self._redir = {}
        self._kinship = {}

        def strip_and_codec(obj, enc='utf-8'):
            for l in obj:
                yield l.rstrip().decode(enc)

        # build redirect map
        self._insert_arity_2_stream(strip_and_codec(self.rfile), self._redir)
        logging.info("inserted records amount: %d" % len(self._redir))

        # build kinship map
        self._insert_arity_2_stream(strip_and_codec(self.cfile), self._kinship)
        logging.info("inserted records amount: %d" % len(self._kinship))

    def _insert_arity_2_stream(self, stream, target, sep='\t'):
        for line in stream:
            parts = line.split(sep)
            assert (len(parts) == 2)
            if parts[0] not in target:
                target[parts[0]] = []

            target[parts[0]].append(parts[1])

    def query_category_redirect(self, category):
        if category in self._redir:
            return self._redir[category][0]
        return None

    def query_category_uplevel(self, category):
        if category in self._kinship:
            return self._kinship[category]
        return []

class CategoryResources(object):
    def __init__(self, rfile, cfile):
        self.rfile = rfile
        self.cfile = cfile
        self.conn = sqlite3.connect(':memory:')

        self._create_tables = """
            create table category_redirect (
                c_from text,
                c_to text,
                primary key (c_from, c_to)
            );

            create table category_kinship (
                id integer primary key autoincrement,
                c_from text,
                c_to text
            );

            create index c_from_index on category_kinship(c_from);
            """

        self.cur = self.conn.cursor()
        self.cur.executescript(self._create_tables)

        def strip_and_codec(obj, enc='utf-8'):
            for l in obj:
                yield l.rstrip().decode(enc)

        # build redirect map
        self._insert_arity_2_stream(strip_and_codec(self.rfile),
                'insert into category_redirect values (?, ?)')
        logging.info("inserted records amount: %d" % self._count_table('category_redirect'))

        # build kinship map
        self._insert_arity_2_stream(strip_and_codec(self.cfile),
                'insert into category_kinship(c_from, c_to) values (?, ?)')
        logging.info("inserted records amount: %d" % self._count_table('category_kinship'))

    def _count_table(self, table):
        self.cur.execute('select count(1) from ' + table)
        return self.cur.fetchone()[0]

    def _insert_arity_2_stream(self, stream, ins_template, sep='\t'):
        cur = self.conn.cursor()
        for line in stream:
            parts = line.split(sep)
            assert (len(parts) == 2)

            try:
                cur.execute(ins_template, (parts[0], parts[1]))
            except:
                continue

    def query_category_redirect(self, category):
        cur = self.conn.cursor()
        cur.execute('select c_to from category_redirect where c_from=?', (category, ))
        res = cur.fetchone()
        if res is not None:
            res = res[0]
        return res

    def query_category_uplevel(self, category):
        cur = self.conn.cursor()
        cur.execute('select c_from, c_to from category_kinship where c_from=?', (category, ))
        res = [x[1] for x in cur.fetchall()]
        return res

def redirect(c, cr):
    target = cr.query_category_redirect(c)
    if target is None:
        target = c
    return target

def traceroute(cr, categories, domain, max_len=12):
    """
    Find a possible route from any of the categories to the domain.
    Code is copied and modified from the filter_category_kinship_by_domain function.
    """
    visited = set()
    domain = cc.convert(domain)

    buf = [[redirect(cc.convert(c), cr)] for c in categories]
    layer = 0
    while len(buf) > 0 and layer < max_len:
        for path in buf:
            if domain == path[-1]:
                return path

        visited.update(path[-1] for path in buf)
        next_buf = []

        for path in buf:
            category = path[-1]
            category = cc.convert(category)
            category = redirect(category, cr)
            uplevel_categories = cr.query_category_uplevel(category)
            next_buf.extend(path + [c] for c in uplevel_categories if c not in visited)

        buf = next_buf
        layer += 1

    return None

def filter_category_kinship_by_domain(cr, categories, domain, max_len=12):
    visited = set()
    domain = cc.convert(domain)

    buf = set(redirect(cc.convert(x), cr) for x in categories)
    layer = 0
    while len(buf) > 0 and layer < max_len:
        if domain in buf: return True
        visited.update(buf)
        next_buf = set()

        for category in buf:
            category = cc.convert(category)
            category = redirect(category, cr)
            uplevel_categories = cr.query_category_uplevel(category)
            next_buf.update(x for x in uplevel_categories if x not in visited)

        buf = next_buf
        layer += 1

    return False

def filter_cirrus_category(args):
    
    cr = CategoryResources(rfile=args.category_redir_map, cfile=args.category_parent_map)
    domain = args.domain.decode('utf-8')
    output = open(args.output, 'w')
    if args.input:
        filelist = [args.input]
    else:
        filelist = open(args.filelist)

    for f in filelist:
        f = f.rstrip()
        for i, line in enumerate(open(f.rstrip())):
            page = json.loads(line.rstrip())
            if i % 1000 == 0:
                logging.info("%s\t%d" %(f.rstrip(), i))
                
            if filter_category_kinship_by_domain(cr, page['categories'], domain, max_len=10):
                output.write(line)

def test(args):
    import datetime
    print 'before:', datetime.datetime.now()
    cr = CategoryResourcesPyNative(rfile=args.category_redir_map, cfile=args.category_parent_map)
    print 'after:', datetime.datetime.now()

    print 'redirect: Fatty_acids ->', cr.query_category_redirect(u'Fatty acids')
    print 'level up: 海岸山脉 ->', repr(cr.query_category_uplevel(u'海岸山脉')).decode('unicode_escape')

    if filter_category_kinship_by_domain(cr, [u'海岸山脉'], u'宗教'):
        print u'->'.join(traceroute(cr, [u'海岸山脉'], u'宗教')).encode('utf-8')

    if filter_category_kinship_by_domain(cr, [u'海岸山脉'], u'加拿大'):
        print u'->'.join(traceroute(cr, [u'海岸山脉'], u'加拿大')).encode('utf-8')

    print filter_category_kinship_by_domain(cr, [u'各国墓葬'], u'宗教場所'), '各国墓葬 belongs to 宗教場所' 
    print filter_category_kinship_by_domain(cr, [u'各国墓葬'], u'宗教场所'), '各国墓葬 belongs to 宗教场所' 

def main():
    parser = argparse.ArgumentParser(description="read json and filter items by domain")

    parser.add_argument("-i", "--input", help="input file")
    parser.add_argument("-f", "--filelist", help="a filename sheet contains all the needed input files")
    parser.add_argument("-r", "--category_redir_map", type=file, help="redirect map for category, a tsv file")
    parser.add_argument("-c", "--category_parent_map", type=file, help="category parent lookup, a tsv file")
    parser.add_argument("-o", "--output", help="output json filename")
    parser.add_argument("-d", "--domain", help="the required domain to filter docs, e.g. Botany")
    parser.add_argument("-q", "--quiet", action="store_true", help="mute the log")
    parser.add_argument("--test", action="store_true", help="run the test entry")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.test:
        test(args)
    else:
        filter_cirrus_category(args)

if __name__ == "__main__":
    main()

