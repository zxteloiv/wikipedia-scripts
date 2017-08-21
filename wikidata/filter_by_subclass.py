# coding: utf-8

from __future__ import absolute_import

from .reader import reader
import argparse, logging, json, datetime

import opencc
cc = opencc.OpenCC()

class CategoryKinship(object):
    def __init__(self, cfile):
        self.cfile = cfile
        self._kinship = {}

        for c_from, c_to in self.file_reader():
            self._insert_arity_2(c_from, c_to)
            if c_from == 'Q36834':
                logging.debug('insert Q36834 with ' + c_to.encode('utf-8'))

        logging.debug('find Q36834 uplevel: ' + repr(self.query_uplevel(u'Q36834')).encode('utf-8'))
        logging.info('inserted kinship pair amount: %d' % len(self._kinship))

    def _insert_arity_2(self, c_from, c_to):
        if c_from not in self._kinship:
            self._kinship[c_from] = []
        self._kinship[c_from].append(c_to)

    def file_reader(self):
        for line in open(self.cfile):
            data = json.loads(line)
            for parent in data['pids']:
                yield data['id'], parent

    def query_uplevel(self, c):
        if c in self._kinship:
            return self._kinship[c]
        return []

def traceroute(ck, categories, domain, max_len=10):
    visited = set()
    buf, layer = [[c] for c in categories], 0

    while len(buf) > 0 and layer < max_len:
        logging.debug(str(layer) + ' ---\t' + repr(buf)[:100])
        for path in buf:
            if domain == path[-1]:
                return path
        
        visited.update(path[-1] for path in buf)
        next_buf = []

        for path in buf:
            category = path[-1]
            uplevel_categories = ck.query_uplevel(category)
            next_buf.extend(path + [c] for c in uplevel_categories if c not in visited)

        buf, layer = next_buf, layer + 1

    return None

def check_kinship_by_domain(ck, categories, domain, max_len=10):
    visited = set()
    buf, layer = set(categories), 0

    while len(buf) > 0 and layer < max_len:
        if domain in buf: return True
        visited.update(buf)
        next_buf = set()

        for category in buf:
            uplevel_categories = ck.query_uplevel(category)
            next_buf.update(x for x in uplevel_categories if x not in visited)

        buf, layer = next_buf, layer + 1

    return False

def filter_category_by_domain(args):

    ck = CategoryKinship(args.category_file)
    domain = args.domain
    kinships = set()

    logging.info('now building kinship set...')
    # find a kinship category map, and dump it to file when necessary
    category_output = open(args.category_sheet_output, 'w') if args.category_sheet_output else None
    for i, l in enumerate(open(args.category_file)):
        data = json.loads(l)
        category = data['id']

        if check_kinship_by_domain(ck, [category], domain):
            kinships.add(category)
            if category_output is not None:
                category_output.write(l)

        if i % 30000 == 0:
            logging.info('%d categories iterated over: %s' % (i, datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    if category_output is not None:
        category_output.close()

    logging.info('all kinship category found: %d' % len(kinships))

    logging.info('now filtering entities by kinships...')

    # iterate over the outputs
    output = open(args.output, 'w')
    for i, entity in enumerate(reader(args.input)):
        if 'claims' not in entity: continue
        claims = entity['claims']

        subclass_claims = claims['P279'] if 'P279' in claims else []
        instance_claims = claims['P31'] if 'P31' in claims else []
        if len(subclass_claims) + len(instance_claims) == 0: continue

        categories = filter(lambda x: x is not None, (claim_value(claim) for claim in subclass_claims))
        classes = filter(lambda x: x is not None, (claim_value(claim) for claim in instance_claims))

        if any(x in kinships for x in categories + classes):
            output.write(l)

        if i % 20000 == 0:
            logging.info('%d entities iterated over: %s' % (i, datetime.datetime.now().strftime('%Y%m%d%H%M%S')))

def claim_value(claim):
    if 'mainsnak' not in claim: return None
    mainsnak = claim['mainsnak']
    if 'datavalue' not in mainsnak: return None
    datavalue = mainsnak['datavalue']
    if 'type' not in datavalue: return None
    datavaluetype = datavalue['type']
    if datavaluetype == 'wikibase-entityid':
        value = datavalue['value']['numeric-id']
        return 'Q' + str(value)
    elif datavaluetype == "string":
        value = datavalue['value']
        return 'Q' + value if value[0] != 'Q' else value

    return None

def test(args):
    print 'before building:', datetime.datetime.now()
    ck = CategoryKinship(cfile=args.category_file)
    print 'after  building:', datetime.datetime.now()

    def do_unit_test(category, domain):
        categories = [category]
        if check_kinship_by_domain(ck, categories, domain):
            print u'->'.join(traceroute(ck, categories, domain)).encode('utf-8')
        else:
            print (u"no route within 10 steps for %s, %s" % (category, domain)).encode('utf-8')

    print "\n====> composer -> creator"
    do_unit_test(u'Q36834', u'Q2500638') # composer -> creator
    print "\n====> composer -> artist"
    do_unit_test(u'Q36834', u'Q483501') # composer -> artist
    print "\n====> composer -> agent"
    do_unit_test(u'Q36834', u'Q24229398') # composer -> agent

    print "\n====> composer -> astronaut"
    do_unit_test(u'Q36834', u'Q11631') # composer -> astronaut

def main():
    parser = argparse.ArgumentParser(description="extract class entity and subclass relation")
    parser.add_argument("-i", "--input", help="input file name")
    parser.add_argument("-c", "--category_file", help="input category file")

    parser.add_argument("-o", "--output", help="output filename")
    parser.add_argument("-s", "--category_sheet_output", help="input category file")

    parser.add_argument("-d", "--domain", help="filter domain")

    parser.add_argument("-q", "--quiet", action="store_true", help="mute the log")
    parser.add_argument("--debug", action="store_true", help="open debug log")
    parser.add_argument("--test", action="store_true", help="run test rather than main entry")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.test:
        test(args)
    else:
        filter_category_by_domain(args)

if __name__ == "__main__":
    main()
