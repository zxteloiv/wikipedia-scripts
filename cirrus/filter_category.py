# coding: utf-8

import sqlite3
import json
import argparse
import re, sys, os.path
import logging
import opencc

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
        for line in stream:
            parts = line.split(sep)
            assert (len(parts) == 2)

            try:
                self.cur.execute(ins_template, (parts[0], parts[1]))
            except:
                continue

    def query_category_redirect(self, category):
        self.cur.execute('select c_to from category_redirect where c_from=?', (category, ))
        res = self.cur.fetchone()
        if res is not None:
            res = res[0]
        return res

    def query_category_uplevel(self, category):
        self.cur.execute('select c_from, c_to from category_kinship where c_from=?', (category, ))
        res = [x[1] for x in self.cur.fetchall()]
        return res

def traceroute(cr, categories, domain):
    """
    Find a possible route from any of the categories to the domain.
    Code is copied and modified from the filter_category_kinship_by_domain function.
    """
    visited = set()
    domain = opencc.convert(domain)

    def redirect(c):
        target = cr.query_category_redirect(c)
        if target is None:
            target = c
        return target

    buf = [[redirect(opencc.convert(c))] for c in categories]
    while len(buf) > 0:
        for path in buf:
            if domain == path[-1]:
                return path

        visited.update(path[-1] for path in buf)
        next_buf = []

        for path in buf:
            category = path[-1]
            category = opencc.convert(category)
            category = redirect(category)
            uplevel_categories = cr.query_category_uplevel(category)
            next_buf.extend(path + [c] for c in uplevel_categories if c not in visited)

        buf = next_buf

    return None

def filter_category_kinship_by_domain(cr, categories, domain):
    visited = set()
    domain = opencc.convert(domain)

    def redirect(c):
        target = cr.query_category_redirect(c)
        if target is None:
            target = c
        return target

    buf = set(redirect(opencc.convert(x)) for x in categories)
    while len(buf) > 0:
        if domain in buf: return True
        visited.update(buf)
        next_buf = set()

        #logging.debug('visited:' + repr(visited).decode('unicode_escape').encode('utf-8'))
        logging.debug('buf:' + u','.join(buf).encode('utf-8'))

        for category in buf:
            category = opencc.convert(category)
            category = redirect(category)
            uplevel_categories = cr.query_category_uplevel(category)
            next_buf.update(x for x in uplevel_categories if x not in visited)

        buf = next_buf

    return False

def test():
    parser = argparse.ArgumentParser(description="read json and filter items by domain")

    parser.add_argument("input", help="input file")
    parser.add_argument("-r", "--category_redir_map", type=file, help="redirect map for category, a tsv file")
    parser.add_argument("-c", "--category_parent_map", type=file, help="category parent lookup, a tsv file")
    parser.add_argument("-d", "--domain", help="the required domain to filter docs, e.g. Botany")
    parser.add_argument("-q", "--quiet", help="mute the log")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    cr = CategoryResources(rfile=args.category_redir_map, cfile=args.category_parent_map)

    print 'redirect: Fatty_acids ->', cr.query_category_redirect(u'Fatty acids')
    print 'level up: 海岸山脉 ->', repr(cr.query_category_uplevel(u'海岸山脉')).decode('unicode_escape')

    if filter_category_kinship_by_domain(cr, [u'海岸山脉'], u'宗教'):
        print u'->'.join(traceroute(cr, [u'海岸山脉'], u'宗教')).encode('utf-8')

    if filter_category_kinship_by_domain(cr, [u'海岸山脉'], u'加拿大'):
        print u'->'.join(traceroute(cr, [u'海岸山脉'], u'加拿大')).encode('utf-8')

    print filter_category_kinship_by_domain(cr, [u'各国墓葬'], u'宗教場所'), '各国墓葬 belongs to 宗教場所' 
    print filter_category_kinship_by_domain(cr, [u'各国墓葬'], u'宗教场所'), '各国墓葬 belongs to 宗教场所' 

if __name__ == "__main__":
    test()

