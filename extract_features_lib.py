from nltk.stem import WordNetLemmatizer
import os, re
from collections import defaultdict
wordNetLemmatizer = WordNetLemmatizer()
FACTBANK_SPLITTER='|||'

def predicate_feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict):
    """Calculate predicate feature. 
    row = a dictionary representing a row from the marneffe_data.csv file
    """
    pk=primary_key(row)
    event_index=get_event_index(pk, event_dict)
    sdp=sd_parse(pk, sdp_dict)
    t=predicate_trail(pk, event_index, sdp, pos_dict)
    f=[]
    #Only the first tuple is useful so far.
    for (predicate, pos, relation, depth) in t[:1]:
        temp_key=(predicate, pos, relation)
        if temp_key in predicate_class_dict:
            f.extend([predicate_class_dict[temp_key], lemma(predicate)])
    return ["p_"+e for e in f]

def general_feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict):
    """The lemma of the event
    The lemma of the root of the sentence
    The incoming grammatical relation to the event
    A general class feature. 
    """
    pk=primary_key(row)
    event_token=get_event_token(pk, event_dict)
    event_index=get_event_index(pk, event_dict)
    event_lemma=lemma(event_token)
    sdp=sd_parse(pk, sdp_dict)
    root_lemma=lemma(get_root(sdp))
    
    try:
        incoming_relation=get_incoming_grammatical_relation(sdp, event_token, event_index)
        return ["g_"+e for e in [event_lemma, root_lemma, incoming_relation]]
    except:
        #TOFIX
        #Currently due to a problem of incompatible tokenization some of the text gets fkcd
        return ["g_"+e for e in [event_lemma, root_lemma]]        
    

def quotation_feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict, sentence_dict):
    """Another reliable indicator of the Uu category is quotation.
    We generated a quotation feature if the sentence opened and ended
    with quotation marks, or if the root subject was we. 
    """
    pk=primary_key(row)
    sentence=get_sentence(pk, sentence_dict)
    sdp=sd_parse(pk, sdp_dict)
    sentence_has_quotation=True if (sentence[0] in ["'", '"'] or sentence[-1] in ["'", '"']) else False
    root_subjects=[e.lower() for e in get_root_subject(sdp)]
    return ["q_true" if sentence_has_quotation or "we" in root_subjects else "q_false"]


def common_template(row, event_dict, sdp_dict, predicate_class_dict, pos_dict, BIGLIST):
    pk=primary_key(row);
    sdp=sd_parse(pk, sdp_dict)
    event_token=get_event_token(pk, event_dict)
    event_index=get_event_index(pk, event_dict)
    blanket=[e.lower() for e in get_blanket_of_token(event_token, event_index, sdp)]
    elements_in_blanket=[e for e in blanket if e in BIGLIST]
    has_modal="true" if len(elements_in_blanket)>0 else "false"
    return ["m_"+e for e in elements_in_blanket+[has_modal]]


def modality_feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict):
    """Distinguish between  modality markers found as direct governors or children of the event under consideration
    #TODO
    And modal words found elsewhere in the context of the sentence.
    """
    MODALS=["can","could","may","might","must","will","would","shall","should"]
    return common_template(row, event_dict, sdp_dict, predicate_class_dict, pos_dict, MODALS)


def conditional_feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict):
    """
    Antecedents of conditionals:  events in an if-clause
    Embedding under words marking uncertainty:  embedding under call for
    #TODO Properly.
    """
    CONDITIONALS=["if"]
    return common_template(row, event_dict, sdp_dict, predicate_class_dict, pos_dict, CONDITIONALS)
    

def negation_feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict):
    """Events are considered negated if they have a negation dependency in 
    the graph or an explicit linguistic marker of negation as
    dependent (e.g., simple negation (not), downward-monotone
    quantifiers (no, any), or restricting prepositions).
    #TODO
    Events are also considered negated if embedded in a negative context 
    (e.g., fail, cancel). 
    """
    NEGATIONS=["no", "not", "not", "none", "no one", "nobody", "nothing", "neither", "nowhere", "never", "negative", "hardly", "scarcely", "barely", "negative", "deny", "doesn't", "isn't", "wasn't", "shouldn't", "wouldn't", "couldn't", "won't", "can't", "don't"]
    return common_template(row, event_dict, sdp_dict, predicate_class_dict, pos_dict, NEGATIONS)

def worldknowledge_feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict):
    """
    #TODO
    For each verb found in the path and contained in the predicate classes:
        add the lemma of verb's' subject
        add whether or not the verb was negated. 
    #TOFIX
    To approximate such world knowledge, we also obtained subject-verb bigram and subject counts from the New York Times portion of GigaWord and then included log(subject verb-counts/subject-counts) as a feature.
    The intuition here is that some embedded clauses carry the main point of the sentence (Frazier and Clifton 2005; Simons 2007; Clifton and Frazier 2010), with the overall frequency of the elements introducing the embedded clause contributing to readers veridicality assessments. 

    """
    pass

def primary_key(row):
    """input: dict(file=, sentId=, eId=, eiId=, eText=, )
    output: (file, sentId, eId, eiId)
    """
    return (row["file"], int(row["sentId"]), row["eId"], row["eiId"])
    

def get_event_index(pk, event_dict):
    """input: (file, sentId, eId, eiId)
    output: event_dict[(file, sentId, eId)]
    >>> factbank_path= r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    >>> d=event_dict_maker(factbank_path)
    >>> assert get_event_index(("ABC19980108.1830.0711.tml", 15,"e30"), d) == 7
    """
    return event_dict[(pk[0], pk[1], pk[2])][0]

def get_event_token(pk, event_dict):
    """input: (file, sentId, eId, eiId)
    output: event_dict[(file, sentId, eId)]
    >>> factbank_path= r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    >>> d=event_dict_maker(factbank_path)
    >>> assert get_event_token(("ABC19980108.1830.0711.tml", 15,"e30"), d) == "break"
    """
    return event_dict[(pk[0], pk[1], pk[2])][1]

def sd_parse(pk, sdp_dict):
    """input: (file, sentId, eId, eiId)
    output: sdp_dict[(file, sentId)]
    """
    return sdp_dict[(pk[0], pk[1])]

def get_pos(pk, token_index, pos_dict):
    """input: (file, sentId, eId, eiId) and token_index and pos_dict
    output: pos_dict[(file, sentId, token_index)]
    """
    if token_index == -1:
        return "ROOT"
    return pos_dict[(pk[0], pk[1], token_index)]

def shortest_path_between_root(root, sdp, sofar, to_find):
    #Find the node containing root
    node=[a for a in sdp if a[1]==root]
    for n in node:
        if to_find==n[4]:
            return sofar + [n]
        l=shortest_path_between_root(n[3], [e for e in sdp if e != n], sofar + [n], to_find)
        if l is not None:
            return l
    return None
        
def predicate_trail(pk, event_index, sdp, pos_dict):
    """input:
    pk = ("ABC19980108.1830.0711.tml", 15,"e30")
    event_index=7
    sdp=[(root, ROOT, -1, lucky, 5), (xcomp, lucky, 5, break, 7), (advmod, break, 7, even, 8), (xsubj, break, 7, Kwan, 2), (aux, break, 7, to, 6)]
    (predicate, pos, relation, depth)
    >>> pk = ("ABC19980108.1830.0711.tml", 15,"e30")
    >>> pp = sd_parse(pk, sdp_dict_maker())
    >>> factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    >>> pd = pos_dict_maker(factbank_path)
    >>> assert predicate_trail(pk, 7, pp, pd) == [("lucky", "Adj", "xcomp", 1), ("ROOT", "ROOT", "root", 2)]
    """
    ptrail=shortest_path_between_root("ROOT", sdp, [], event_index)
    try: 
        return [(e[1], get_pos(pk, e[2], pos_dict), e[0], i+1) for i,e in enumerate(ptrail[::-1])]
    except: #FIX THIS HACK LATER This fails at prepositions which have been absobed into the sdp Like no woman has been in charge of this mission
        #TOFIX
        return []

def lemma(word):
    """input:
    output:
    """
    return wordNetLemmatizer.lemmatize(word)

def predicate_class_dict_maker():
    """output: dict((predicate, pos, relation))
    >>> d=predicate_class_dict_maker()
    >>> assert d["accused", "Adj", "prep_of"]=="conjecture"
    """
    d={}
    for l in open("appendix b.txt", "r"):
        l=[e.strip() for e in l.strip().split("|") if e != ""]
        pos = l[0]
        predicate = l[1]
        predicate_class = l[2]
        for relation in  l[3].split(","):
            relation = relation.strip()
            d[(predicate, pos, relation)]=predicate_class
    return d

def event_dict_maker(factbank_path):
    """This parses the factbank_path/tokens_tml file and then creates a dictionary
    output: The token number tokLoc - 1 from tokens_tml would be stored as (file, sendId, tmlTagId)
    >>> factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    >>> d=event_dict_maker(factbank_path)
    >>> assert d["ABC19980108.1830.0711.tml", 15,"e30"] == (7, "break")
    """
    tml_file_path = os.path.join(factbank_path, "annotation", "tokens_tml.txt")
    d={}
    for l in open(tml_file_path, "rb"):
        l=l.strip().split(FACTBANK_SPLITTER)
        _file=l[0][1:-1]; assert l[0][0]=="'"
        sendId=int(l[1])
        tmlTagId=l[5][1:-1]; assert l[5][0]=="'"
        tokLoc=int(l[2])
        tok=l[3][1:-1]
        d[(_file, sendId, tmlTagId)] = (tokLoc, tok)
    return d

def sentence_dict_maker(factbank_path):
    """This parses the factbank_path/tokens_tml file and then creates a dictionary output:
    >>> factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    >>> d=sentence_dict_maker(factbank_path)
    >>> assert d[("ABC19980108.1830.0711.tml", 15)] == "And Wong Kwan will be lucky to break even .", d[("ABC19980108.1830.0711.tml", 15)] 
    """
    tml_file_path = os.path.join(factbank_path, "annotation", "tokens_tml.txt")
    d=defaultdict(str)
    for l in open(tml_file_path, "rb"):
        l=l.strip().split(FACTBANK_SPLITTER)
        _file=l[0][1:-1]; assert l[0][0]=="'"
        sendId=int(l[1])
        tokLoc=int(l[2])
        tok=l[3][1:-1]
        d[(_file, sendId)] += (" "+tok)
    for k in d:
        d[k]=d[k].strip()
    return dict(d)

def get_sentence(pk, sentence_dict):
    """
    >>> factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    >>> d=sentence_dict_maker(factbank_path)
    >>> pk = ("ABC19980108.1830.0711.tml", 15,"e30")
    >>> assert get_sentence(pk, d)=="And Wong Kwan will be lucky to break even ."
    """
    return sentence_dict[(pk[0], pk[1])]

def extract_stanford_parses_from_sdp_file(sd_parse_file_name):
    sd_parses=[]
    currently_reading_a_parse=False
    _f=open(sd_parse_file_name, "rb")
    for l in _f:
        if l == "\n":
            l=_f.next()
            currently_reading_a_parse = True
        temp=[]
        while currently_reading_a_parse:
            if l == "\n":
                sd_parses.append(temp)
                currently_reading_a_parse = False
                try: 
                    l=_f.next()
                except StopIteration:
                    return sd_parses
                break
            gg=re.match("((\w|_)+)\((.+)-(\d+)'?,(.+)-(\d+)'?\)", l.strip())
            if gg is None:
                print l.strip()
                import pdb; pdb.set_trace()
            tt=gg.groups()
            temp.append((tt[0].strip(), tt[2].strip(), int(tt[3])-1, tt[4].strip(), int(tt[5])-1))
            try:
                l=_f.next()
            except StopIteration:
                return sd_parses
    return sd_parses


def sdp_dict_maker(factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data", parse_file="factbank.sdp"):
    """output: gets parse for (file, sentId) in sdp_dict
    >>> d=sdp_dict_maker()
    >>> assert ("cc", "lucky", 5, "And", 0) in d[("ABC19980108.1830.0711.tml", 15)]
    """
    sentence_file_path = os.path.join(factbank_path, "annotation", "sentences.txt")
    # Create a sent file and
    # then parses the sentence file
    # by calling make fact_bank_parse.sdp
    filename_sentId = []
    with open("factbank.sent", "wb") as sent_write_file:
        for l in open(sentence_file_path):
            l=l.strip().split(FACTBANK_SPLITTER)
            fb_filename=l[0][1:-1]; assert l[0][0]=="'"
            sentId=int(l[1])
            if sentId != 0:
                filename_sentId.append((fb_filename, sentId))
                sentence=l[2][1:-1].replace(r"\'", "'").strip()
                sent_write_file.write(sentence); assert l[2][0]=="'"
                sent_write_file.write("\n")
    # If the results does not exist
    if (not os.path.exists(parse_file)):
        os.system("make factbank.sdp")        
    #Then extract the stanford parses from the sentence file by keeping only the needed portion
    #The stanford parse for a sentence is a list of 5 tuples
    parses = extract_stanford_parses_from_sdp_file(sd_parse_file_name = "factbank.sdp")
    #Then make sure that the number of lists is exactly equal to the number of sentences
    assert len(parses) == len(filename_sentId)
    d=dict(zip(filename_sentId, parses))
    return d
    
def pos_dict_maker(factbank_path):
    """output: dict( (file, sentence, token_index) )
    >>> factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    >>> d = pos_dict_maker(factbank_path)
    >>> assert d[("ABC19980108.1830.0711.tml", 15, 7)] == "Verb"
    """
    pos_file_path = os.path.join(factbank_path, "annotation", "tokens_ling.txt")
    d={}
    with open(pos_file_path) as f :
        for l in f:
            l=l.strip().split(FACTBANK_SPLITTER)
            _file=l[0][1:-1]; assert l[0][0]=="'"
            sentId=int(l[1])
            tokLoc=int(l[2])
            pos=l[4][1:-1]; assert l[4][0]=="'"
            d[(_file, sentId, tokLoc)]=simplified_pos_tags(pos)
    return d

JJtags=set(["JJ", "JJR", "JJS" ])
Verbtags=set(["VB", "VBD", "VBG", "VBN", "VBP", "VBZ" ])
Nountags=set(["NN", "NNS", "NNP", "NNPS", ])
def simplified_pos_tags(tag):
    """JJ -> Adj  NN -> Noun V -> Verb this way it matches the dictionary values 
    """
    if tag in JJtags:
        return "Adj"
    elif tag in Verbtags:
        return "Verb"
    elif tag in Nountags:
        return "Noun"
    else:
        return tag

def get_incoming_grammatical_relation(sdp, event_token, event_index):
    """First check whether this is a collapesed conj or prep
    then search for it in the the rest of the parse.
    """
    prep_or_conj=[e for e in sdp if e[0].endswith("_"+event_token)]
    if len(prep_or_conj)>0:
        return prep_or_conj[0][0]
    for e in sdp:
        if e[3]==event_token and e[4]==event_index:
            return e[0]
    raise Exception("This cant be happening. This sdp "+str(sdp)+"has no incoming grammatical relation for "+event_token+ " "+ str(event_index))

def get_root(sdp):
    root_candidates=[e for e in sdp if e[0]=="root"]
    assert len(root_candidates)==1
    return root_candidates[0][3]

def get_root_index(sdp):
    root_candidates=[e for e in sdp if e[0]=="root"]
    assert len(root_candidates)==1
    return root_candidates[0][4]

def get_root_subject(sdp):
    """
    >>> sdp=[('nsubj', 'participate', 9, 'Poland', 0),('nsubj', 'participate', 9, 'Hungary', 2),('conj_and', 'Poland', 0, 'Republic', 6),('nsubj', 'participate', 9, 'Republic', 6),('nn', 'planning', 13, 'NATO', 11),('nn', 'planning', 13, 'strategy', 12),('prep_in', 'participate', 9, 'planning', 13),('nsubj', 'approved', 21, 'states', 19),('nn', 'Scharping', 31, 'Rudolf', 30),('nsubj', 'said', 32, 'Scharping', 31),('root', 'ROOT', -1, 'said', 32)]
    >>> assert get_root_subject(sdp)=="Scharping"
    """
    root_index=get_root_index(sdp)
    subject=[e[3] for e in sdp if e[0] in ["nsubj", "nsubjpass", "csubj", "csubjpass", "subj"] and e[2]==root_index]
    if len(subject) == 0:
        return ""
    return subject[0]
    
def get_blanket_of_token(event_token, event_index, sdp):
    """
    >>> sd=[('nsubj', 'participate', 9, 'Poland', 0),('conj_and', 'Poland', 0, 'Hungary', 2),('nsubj', 'participate', 9, 'Hungary', 2),('det', 'Republic', 6, 'the', 4),('nn', 'Republic', 6, 'Czech', 5),('conj_and', 'Poland', 0, 'Republic', 6),('nsubj', 'participate', 9, 'Republic', 6),('aux', 'participate', 9, 'can', 7),('advmod', 'participate', 9, 'now', 8),('ccomp', 'said', 32, 'participate', 9),('nn', 'planning', 13, 'NATO', 11),('nn', 'planning', 13, 'strategy', 12),('prep_in', 'participate', 9, 'planning', 13),('mark', 'approved', 21, 'because', 15),('det', 'states', 19, 'all', 16),('nn', 'states', 19, 'NATO', 17),('nn', 'states', 19, 'member', 18),('nsubj', 'approved', 21, 'states', 19),('aux', 'approved', 21, 'have', 20),('advcl', 'participate', 9, 'approved', 21),('dobj', 'approved', 21, 'their', 22),('xcomp', 'approved', 21, 'joining', 23),('det', 'alliance', 25, 'the', 24),('dobj', 'joining', 23, 'alliance', 25),('amod', 'Scharping', 31, 'German', 27),('nn', 'Scharping', 31, 'defense', 28),('nn', 'Scharping', 31, 'minister', 29),('nn', 'Scharping', 31, 'Rudolf', 30),('nsubj', 'said', 32, 'Scharping', 31),('root', 'ROOT', -1, 'said', 32),('tmod', 'said', 32, 'Saturday', 33)]
    >>> assert get_blanket_of_token("participate", 9, sd)==set(["Republic", "Poland", "Hungary", "can", "now", "planning", "said", "approved"]), get_blanket_of_token("participate", 9, sd)
    """
    children=[e[3] for e in sdp if e[1]==event_token and e[2]==event_index]
    parents=[e[1] for e in sdp if e[3]==event_token and e[4]==event_index]
    return set(children+parents)

if __name__ =="__main__":
    import doctest
    print "testing"
    doctest.testmod()
