# coding: utf-8

from __future__ import absolute_import

from utils.reader import reader, claim_value
import argparse, logging, json, datetime

import opencc
cc = opencc.OpenCC()

def collect_categories(args):
    categories = set()
    for i, entity in enumerate(reader(args.input)):
        if i % 20000 == 0:
            logging.info("%d data (first) processed: %s" %(i, datetime.datetime.now().strftime('%m%d-%H:%M:%S')))
            if args.debug and i / 20000 == 1:
                break

        try:
            subclass_claims = entity['claims']['P279']
            values = filter(None, (claim_value(claim) for claim in subclass_claims))

            # An entity with a non-empty 'subclass_of' property is itself a class.
            # The parent entities indicated by the 'subclass_of' property are all classes.
            # If the class is an 'instance_of' another entity, the other one must also be a class.
            if values:
                categories.add(entity['id'])

                categories.update(values)
                instance_claims = entity['claims']['P31']
                values = filter(None, (claim_value(claim) for claim in instance_claims))
                categories.update(values)

        except:
            continue

    return categories

def extract(args):
    categories = collect_categories(args)

    logging.info('got all categories, count %d' % len(categories))
    logging.debug('first 100 categories repr: ' + ','.join(repr(x) for x in list(categories)[:100]))
    
    output = open(args.output, 'w')
    for i, entity in enumerate(reader(args.input)):
        if i % 20000 == 0:
            logging.info("%d data (first) processed: %s" %(i, datetime.datetime.now().strftime('%m%d-%H:%M:%S')))
            if args.debug and i / 20000 == 1:
                break

        try:
            qid = entity['id']
        except:
            continue

        if qid not in categories: continue

        if 'claims' not in entity: continue
        claims = entity['claims']
        subclass_claims = claims['P279'] if 'P279' in claims else [] # subclass_of
        instance_claims = claims['P31'] if 'P31' in claims else [] # instance_of
        if len(subclass_claims) + len(instance_claims) == 0: continue

        subclass_values = filter(None, (claim_value(claim) for claim in subclass_claims))
        instance_values = filter(None, (claim_value(claim) for claim in instance_claims))

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
        new_entity['pids'] = subclass_values + instance_values

        output.write(json.dumps(new_entity) + "\n")

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
