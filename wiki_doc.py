#!/usr/bin/env python2
# coding: utf-8

import re

DOC_START_PATTERN = re.compile('<doc id="(\d+)" url="([^"]+)" title="([^"]+)"')
DOC_END_PATTERN = re.compile('</doc>')

def charset_wrapper(fileobj, charset='utf-8'):
    return (line.decode(charset) for line in fileobj)

def wikiobj_to_doc(wikiobj):

    # state could only be out of or inside a doc
    state_out_of_doc = True
    doc_obj = {}

    for line in wikiobj:

        if state_out_of_doc:
            m = DOC_START_PATTERN.match(line)
            if m:
                state_out_of_doc = False
                doc_obj = {}
                doc_obj['id'] = m.group(1)
                doc_obj['url'] = m.group(2)
                doc_obj['title'] = m.group(3)
                doc_obj['text'] = []
                continue

        if not state_out_of_doc and DOC_END_PATTERN.match(line):
            state_out_of_doc = True
            yield doc_obj
            continue

        if not state_out_of_doc:
            doc_obj['text'].append(line)
            continue

        raise ValueError('failed with: state_out_of_doc=%s line=%s' %
                (state_out_of_doc, line))

if __name__ == "__main__":
    import sys

    class PrettyDoc(dict):
        def __str__(self):
            return ("id:\t" + str(self['id']) + "\n" +
                    "url:\t" + str(self['url']) + "\n" +
                    "title:\t" + str(self['title']) + "\n" + 
                    "\n".join(self['text'][:5]))

    doc = wikiobj_to_doc(charset_wrapper(open(sys.argv[1], 'r'))).next()
    print PrettyDoc(doc)
