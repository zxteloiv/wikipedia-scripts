# coding: utf-8

def depparse_paragraph(para, nlp, response_encoding=None):
    return nlp.annotate(para.encode('utf-8'),
            properties={'outputFormat':'json', 'annotators':'depparse'},
            response_encoding=response_encoding)

def restore_sentence_from_tokens(tokens):
    sentence = ''

    if not tokens:
        return sentence

    # for the sake of sentence offset to be accurate, character before the first
    # token will be ignored (e.g. a space between consequent sentences of a paragraph)
    #if len(tokens[0]['before']) > 0:
    #    sentence += tokens[0]['before']

    sentence += u"".join(x['originalText'] + x['after'] for x in tokens)

    # a trick that make the encoding works correctly with CoreNLP Server 3.6.0
    #sentence = sentence.encode('iso-8859-1').decode('utf-8')
    return sentence

def find_entity_deproute(tokens, depparse, entity_a, entity_b):
    pass

def find_sentence_by_offset(sentences, start, end):

    sentence_id = get_sentence_id(sentences, start, end)
    if sentence_id >= len(sentences):
        return None

    sentence = restore_sentence_from_tokens(sentences[sentence_id][u'tokens'])
    
    return sentence

def get_sentence_id(sentences, start, end):
    """ Find the sentence id to which the start-end span belongs """
    for (i, sentence) in enumerate(sentences):
        tokens = sentence[u'tokens']
        if start < tokens[0][u'characterOffsetBegin']:
            return i - 1

    return i

if __name__ == "__main__":
    pass
