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

def find_sentence_by_offset(sentences, start, end):

    sentence_id = get_sentence_id(sentences, start, end)
    if sentence_id >= len(sentences):
        return None

    sentence = restore_sentence_from_tokens(sentences[sentence_id][u'tokens'])
    
    return sentence

def vertices_route_to_deproute(route, edges, tokens, dependencies):
    if len(route) <= 1:
        return ""

    import xuxian
    syslog = xuxian.log.system_logger

    result = tokens[route[0]]['originalText']
    for i in xrange(len(route) - 1):
        if (route[i], route[i + 1], 1) in edges:
            dep = dependencies[edges[(route[i], route[i + 1], 1)]]
            direction = u'>'
            next_token = tokens[dep['dependent'] - 1]['originalText']
        elif (route[i + 1], route[i], 1) in edges:
            dep = dependencies[edges[(route[i + 1], route[i], 1)]]
            direction = u'<'
            next_token = tokens[dep['governor'] - 1]['originalText']
        else:
            raise ValueError("Route %s not found" % str(route[i], route[i + 1]))

        if dep['dep'] == u'root':
            syslog.debug("======root dep>>>>>>>>" + str(dep) + ';string=' +
                ' '.join(t['originalText'].encode('utf-8') for t in tokens))

        result = (u' ' + direction + u' ').join((result, dep['dep'], next_token))

    return result

def get_sentence_id(sentences, start, end):
    """ Find the sentence id to which the start-end span belongs """
    for (i, sentence) in enumerate(sentences):
        tokens = sentence[u'tokens']
        if start < tokens[0][u'characterOffsetBegin']:
            return i - 1

    return i

def get_token_id_list_by_mention(sentence, mstart, mend):
    """ Given a mention, find all the tokens with its span """
    if u'tokens' not in sentence:
        raise ValueError('empty sentence should not be parsed')
    tokens = sentence[u'tokens']

    token_id_list = []
    for (i, token) in enumerate(tokens):
        tstart, tend = token['characterOffsetBegin'], token['characterOffsetEnd']
        # tokens is inside a mention span
        if mstart <= tstart and tend <= mend:
            token_id_list.append(i)

        # token is iterated beyond the current mention, quickly break
        # ----(mention)---(tokens)----
        if mend < tstart:
            break

    return token_id_list

if __name__ == "__main__":
    import sys

    sys.path.insert(1, './lib/py-corenlp')

    from utils import charset_wrapper, init_corenlp
    from wiki_doc import wikiobj_to_doc
    from entity_mentions import get_entity_mentions, get_entity_mentions_in_lines
    from entity_mentions import get_plain_text, get_plain_text_mention_info
    doc = wikiobj_to_doc(charset_wrapper(open(sys.argv[1], 'r'))).next()
    nlp = init_corenlp('localhost', 9000)

    for line in doc['text']:
        line = line.rstrip()
        if not line: continue

        plaintext = get_plain_text(line)
        mentions = get_plain_text_mention_info(line)
        if not mentions: continue

        depparsed_output = depparse_paragraph(plaintext, nlp)
        if u'sentences' not in depparsed_output: continue

        sentences = depparsed_output[u'sentences']

        print "\n===============================================\n"
        print line
        print "\n-----------------------------------------------\n"

        for mention in mentions:
            (mstart, mend, href, _) = mention
            sentence_id = get_sentence_id(sentences, mstart, mend)

            tokens = sentences[sentence_id]['tokens']
            token_id_list = get_token_id_list_by_mention(sentences[sentence_id],
                    mstart, mend)
            print "XXX- - new mention - ->", token_id_list, str(list(tokens[i]['originalText'] for i in token_id_list))

