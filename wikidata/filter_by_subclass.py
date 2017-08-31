# coding: utf-8

from __future__ import absolute_import

from utils.reader import reader, reader_for_list
from utils.wikidata import claim_value
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

def build_kinship_by_domain(args):

    logging.info('loading category file ' + args.category_file)
    ck = CategoryKinship(args.category_file)
    domain = args.domain
    kinships = set()

    logging.info('now building kinship set...')
    # find a kinship category map, and dump it to file when necessary
    category_output = open(args.category_sheet, 'w') if args.category_sheet else None
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

    logging.info('all category kinships found: %d' % len(kinships))

    return kinships

def find_entities_by_kinships(args, kinships):
    logging.info('now filtering entities by kinships...')

    # iterate over the outputs
    output = open(args.output, 'w')
    dataset = reader_for_list(args.input_filelist) if args.input_filelist else reader(args.input)
    for i, entity in enumerate(dataset):
        if 'claims' not in entity: continue
        claims = entity['claims']

        subclass_claims = claims['P279'] if 'P279' in claims else [] # subclass_of
        instance_claims = claims['P31'] if 'P31' in claims else [] # instance_of
        if len(subclass_claims) + len(instance_claims) == 0: continue

        categories = filter(lambda x: x is not None, (claim_value(claim) for claim in subclass_claims))
        classes = filter(lambda x: x is not None, (claim_value(claim) for claim in instance_claims))

        if any(x in kinships for x in categories + classes):
            output.write(json.dumps(entity) + '\n')

        if i % 20000 == 0:
            logging.info('categories: %s, classes: %s' % (repr(categories), repr(classes)))
            logging.info('%d entities iterated over: %s' % (i, datetime.datetime.now().strftime('%Y%m%d%H%M%S')))

def filter_category_by_domain(args):

    if args.only == "category":

        kinships = build_kinship_by_domain(args)
        logging.info('Done. Skipping the entity finding step.')
        return

    elif args.only == "entity":

        kinships = set(json.loads(l)['id'] for l in open(args.category_sheet))
        logging.info('loaded kinships from %s, count %d' % (args.category_sheet, len(kinships)))
        find_entities_by_kinships(args, kinships)

    else:
        kinships = build_kinship_by_domain(args)
        find_entities_by_kinships(args, kinships)


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

    print "\n====> Taiwanese opera -> physical object"
    do_unit_test(u'Q31918', u'Q223557') 

    if args.trace_from and args.trace_to:
        do_unit_test(unicode(args.trace_from), unicode(args.trace_to))


def main():
    parser = argparse.ArgumentParser(description="extract class entity and subclass relation")

    groupK = parser.add_argument_group("Extract Category Kinships", "options related to kinship function")
    groupK.add_argument("-c", "--category_file", help="input category file")
    groupK.add_argument("-d", "--domain", help="filter domain")
    groupK.add_argument("-s", "--category_sheet",
            help="category file, input when `only` is set to entity, otherwise output")

    groupE = parser.add_argument_group("Entity Extraction", "options related to entity extraction")
    groupE.add_argument("-i", "--input", help="input file name, wikidata entity file")
    groupE.add_argument("-l", "--input_filelist", help="a file containing a list of input filenames")
    groupE.add_argument("-o", "--output", help="output filename")

    groupM = parser.add_argument_group("Misc")
    parser.add_argument("--only", choices=['category', 'entity'],
            help="only build category kinship map, or only find entities by existing category kinships")
    groupM.add_argument("-q", "--quiet", action="store_true", help="mute the log")
    groupM.add_argument("--debug", action="store_true", help="open debug log")
    groupM.add_argument("--test", action="store_true", help="run test rather than main entry")
    groupM.add_argument("--trace_from", help="run test rather than main entry")
    groupM.add_argument("--trace_to", help="run test rather than main entry")

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
