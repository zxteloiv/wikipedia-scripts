# coding: utf-8

from __future__ import absolute_import

from .reader import reader
import argparse, logging, json

import opencc
cc = opencc.OpenCC()

def extract(args):
    output = open(args.output, 'w')
    for entity in reader(args.input):

        if 'claims' not in entity: continue
        claims = entity['claims']
        if u'P279' not in claims: continue
        subclass_claim = claims['P279']

        entity = arrange(entity)
        output.write(json.dumps(entity) + "\n")

def arrange(entity):
    new_entity = {}
    new_entity['id'] = entity['id']
    try:
        new_entity['enlabel'] = entity['labels']['en']['value']
    except:
        new_entity['enlabel'] = ""
    try:
        new_entity['zhlabel'] = entity['labels']['zh']['value']
    except:
        new_entity['zhlabel'] = ""

    new_entity['pids'] = []
    for claim in entity['claims']['P279']:
        if 'mainsnak' not in claim: continue
        mainsnak = claim['mainsnak']
        if 'datavalue' not in mainsnak: continue
        datavalue = mainsnak['datavalue']
        if 'type' not in datavalue: continue
        datavaluetype = datavalue['type']
        if datavaluetype == 'wikibase-entityid':
            value = datavalue['value']['numeric-id']
            new_entity['pids'].append('Q' + str(value))
        elif datavaluetype == "string":
            value = datavalue['value']
            new_entity['pids'].append('Q' + value if value[0] != 'Q' else value)

    return new_entity

def main():
    parser = argparse.ArgumentParser(description="extract class entity and subclass relation")
    parser.add_argument("-i", "--input", help="input file name")
    parser.add_argument("-o", "--output", help="output filename")
    parser.add_argument("-q", "--quiet", action="store_true", help="mute the log")
    parser.add_argument("--debug", action="store_true", help="open debug log")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    extract(args)

if __name__ == "__main__":
    main()
