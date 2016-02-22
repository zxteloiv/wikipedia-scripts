# coding: utf-8

def depparse_paragraph(para, nlp):
    return nlp.annotate(para,
            properties={'outputFormat':'json', 'annotators':'depparse'})

def restore_sentence_from_tokens(tokens):
    sentence = ''
    for i, token in enumerate(tokens):
        if i == 0:
            sentence += token['originalText']
        else:
            sentence += token['before'] + token['originalText']

    return sentence

def find_entity_deproute(tokens, depparse, entity_a, entity_b):
    pass

if __name__ == "__main__":
    pass
