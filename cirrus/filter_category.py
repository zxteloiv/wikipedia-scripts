# coding: utf-8

import sqlite3
import json
import argparse
import re, sys, os.path
import logging

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

def main():
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

    print cr.query_category_redirect(u'Fatty acids')
    print repr(cr.query_category_uplevel(u'海岸山脉')).decode('unicode_escape')

if __name__ == "__main__":
    main()

