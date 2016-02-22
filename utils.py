# coding: utf-8

def charset_wrapper(fileobj, charset='utf-8'):
    return (line.decode(charset) for line in fileobj)

from pycorenlp import StanfordCoreNLP as CoreNLP

def init_corenlp(server='127.0.0.1', port=9000):
    return CoreNLP('http://' + server + ':' + str(port))


