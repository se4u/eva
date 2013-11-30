from nltk.stem import WordNetLemmatizer
import os, re
wordNetLemmatizer = WordNetLemmatizer()
FACTBANK_SPLITTER='|||'

def feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict):
    """Calculate predicate feature. 
    row = a dictionary representing a row from the marneffe_data.csv file
    """
    pk=primary_key(row)
    event_index=event(pk, event_dict)
    sdp=sd_parse(pk, sdp_dict)
    t=predicate_trail(pk, event_index, sdp, pos_dict)
    f=[]
    #Only the first tuple is useful so far.
    for (predicate, pos, relation, depth) in t[:1]:
        temp_key=(predicate, pos, relation)
        if temp_key in predicate_class_dict:
            f.extend([predicate_class_dict[temp_key], lemma(predicate)])
    return f

def primary_key(row):
    """input: dict(file=, sentId=, eId=, eiId=, eText=, )
    output: (file, sentId, eId, eiId)
    """
    return (row["file"], int(row["sentId"]), row["eId"], row["eiId"])
    

def event(pk, event_dict):
    """input: (file, sentId, eId, eiId)
    output: event_dict[(file, sentId, eId)]
    >>> factbank_path= r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    >>> d=event_dict_maker(factbank_path)
    >>> assert event(("ABC19980108.1830.0711.tml", 15,"e30"), d) == 7
    """
    return event_dict[(pk[0], pk[1], pk[2])]

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
    >>> pd = pos_dict_maker(factbank_path)
    >>> assert predicate_trail(pk, 7, pp, pd) == [("lucky", "Adj", "xcomp", 1), ("ROOT", "ROOT", "root", 2)]
    """
    ptrail=shortest_path_between_root("ROOT", sdp, [], event_index)
    try: 
        return [(e[1], get_pos(pk, e[2], pos_dict), e[0], i+1) for i,e in enumerate(ptrail[::-1])]
    except: #FIX THIS HACK LATER This fails at prepositions which have been absobed into the sdp Like no woman has been in charge of this mission
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
    >>> assert d["ABC19980108.1830.0711.tml", 15,"e30"] == 7
    """
    tml_file_path = os.path.join(factbank_path, "annotation", "tokens_tml.txt")
    d={}
    for l in open(tml_file_path, "rb"):
        l=l.strip().split(FACTBANK_SPLITTER)
        _file=l[0][1:-1]; assert l[0][0]=="'"
        sendId=int(l[1])
        tmlTagId=l[5][1:-1]; assert l[5][0]=="'"
        tokLoc=int(l[2])
        d[(_file, sendId, tmlTagId)] = tokLoc
    return d


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
    # If the results does not exist or is older than sentence_file
    if (not os.path.exists(parse_file)) or (os.path.getmtime(parse_file) < os.path.getmtime(sentence_file_path)):
        os.system("make factbank.sdp")        
    #Then extract the stanford parses from the sentence file by keeping only the needed portion
    #The stanford parse for a sentence is a list of 5 tuples
    parses = extract_stanford_parses_from_sdp_file(sd_parse_file_name = "factbank.sdp")
    #Then make sure that the number of lists is exactly equal to the number of sentences
    assert len(parses) == len(filename_sentId)
    d=dict(zip(filename_sentId, parses))
    #Store this in a pickle
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
    
if __name__ =="__main__":
    import doctest
    print "testing"
    doctest.testmod()
