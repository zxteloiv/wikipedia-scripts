# coding: utf-8

from __future__ import absolute_import
import datetime
import argparse, logging, json
import opencc

cc = opencc.OpenCC()

def main():
    parser = argparse.ArgumentParser(description="build qid to filename, lineno index")
    parser.add_argument("-l", "--filelist", help='input of entity files', required=True)
    parser.add_argument("-r", "--redir_file", type=file, help="the redirect mapping tsv file")

    parser.add_argument("-o", "--output", help='output index, tsv file: Qid, filename and lineno', required=True)

    parser.add_argument("-q", "--quiet", action="store_true", help="mute the log")
    parser.add_argument("--debug", action="store_true", help="open debug log")
    args = parser.parse_args()

    if not args.quiet:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    build_index(args)

def build_redir_mapping(rfile):
    if rfile is None: return {}
    redir = {}
    for l in rfile:
        parts = l.rstrip().split('\t')
        redir[parts[0]] = parts[1]

    return redir

def build_index(args):
    redir = build_redir_mapping(args.redir_file)

    def dataextractor(filelist):
        for f in open(filelist):
            f = f.rstrip()
            for i, line in enumerate(open(f)):
                entity = json.loads(line)
                title = entity['title']
                target = redir.get(title)
                title = target if target is not None else title
                title = cc.convert(title)
                yield title.encode('utf-8'), f, str(i + 1)

    output = open(args.output, 'w')
    for i, data in enumerate(dataextractor(args.filelist)):
        output.write('\t'.join(data) + '\n')

        if i % 100 == 0:
            output.flush()
        if i % 1000 == 0:
            logging.info(("%d pages written" % i) + datetime.datetime.now().strftime('%m%d%-H%M%S'))

if __name__ == "__main__":
    main()


