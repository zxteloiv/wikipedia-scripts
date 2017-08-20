# coding: utf-8

import sqlite3
import json
import argparse
import re, sys, os.path
import logging

def main():
    parser = argparse.ArgumentParser(description="read json and filter items by domain")

    parser.add_argument("input", help="input file")
    parser.add_argument("-r", "--category_redir_map", type=file, help="redirect map for category, a tsv file")
    parser.add_argument("-c", "--category_parent_map", type=file, help="category parent lookup, a tsv file")
    parser.add_argument("-d", "--domain", help="the required domain to filter docs, e.g. Botany")
    args = parser.parse_args()

    conn = sqlite3.connect(':memory:')
    logging.getLogger().setLevel(logging.INFO)
    build_redir_map(args.category_redir_map, conn)
    build_category_kinship_map(args.category_parent_map, conn)

    cur = conn.cursor()
    print query_category_redirect(cur, u'Fatty acids')
    print repr(query_category_uplevel(cur, u'海岸山脉')).decode('unicode_escape')

    pass

def query_category_redirect(cur, category):
    cur.execute('select c_to from category_redirect where c_from=?', (category, ))
    res = cur.fetchone()
    if res is not None:
        res = res[0]
    return res

def query_category_uplevel(cur, category):
    cur.execute('select c_from, c_to from category_kinship where c_from=?', (category, ))
    res = [x[1] for x in cur.fetchall()]
    return res

def build_redir_map(mapfile, conn):
    c = conn.cursor()
    c.execute('create table category_redirect ('
            'c_from text,'
            'c_to text,'
            'primary key (c_from, c_to)'
            ')')

    for line in mapfile:
        parts = line.rstrip().decode('utf-8').split('\t')
        try:
            c.execute('insert into category_redirect values (?, ?)', (parts[0], parts[1]))
        except:
            continue

    c.execute('select count(1) from category_redirect')
    logging.info("inserted records amount: %d" % c.fetchone())

    conn.commit()

def build_category_kinship_map(mapfile, conn):
    c = conn.cursor()
    c.execute("""
        create table category_kinship (
            id integer primary key autoincrement,
            c_from text,
            c_to text
        )
        """)
    c.execute('create index c_from_index on category_kinship(c_from)')

    for line in mapfile:
        parts = line.rstrip().decode('utf-8').split('\t')
        try:
            c.execute('insert into category_kinship(c_from, c_to) values (?, ?)', (parts[0], parts[1]))
        except:
            continue

    c.execute('select count(1) from category_kinship')
    logging.info("inserted records amount: %d" % c.fetchone())

    conn.commit()

if __name__ == "__main__":
    main()

