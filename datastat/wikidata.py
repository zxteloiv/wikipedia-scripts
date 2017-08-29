# coding: utf-8

from __future__ import absolute_import

from utils.reader import reader
import logging, argparse, json

def stat(args):
    for i, entity in enumerate(reader(args.entity_file)):
        if i / 50000 == 1:
            break
        
        for claims in entity['claims'].itervalues():
            for c in claims:
                # datatype, datavalue.type, datavalue.value
                x = extract_kv(c)
                print entity['id'].encode('utf-8') + '\t' + u'\t'.join(x).encode('utf-8')

def extract_kv(claim):
    try:
        mainsnak = claim['mainsnak']
        datavalue = mainsnak['datavalue']
        datatype = mainsnak['datatype']
        datavaluetype = datavalue['type']

        if datavaluetype == 'wikibase-entityid':
            value = u'Q' + unicode(datavalue['value']['numeric-id'])
        elif datavaluetype == 'string':
            value = datavalue['value']
        else:
            value = u"None\t" + json.dumps(datavalue).decode('utf-8')

        return datatype, datavaluetype, value

    except KeyError:
        return ["None"] * 3

def main():
    parser = argparse.ArgumentParser(description="find neighbors for a file list of wikidata")
    parser.add_argument("entity_file", help="input entity file")
    args = parser.parse_args()
    
    stat(args)

if __name__ == "__main__":
    main()
