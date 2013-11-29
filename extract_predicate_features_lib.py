from nltk.stem import WordNetLemmatizer
import os, re, cPickle
wordNetLemmatizer = WordNetLemmatizer()
FACTBANK_SPLITTER='|||'
def feature(row, event_dict, sdp_dict, predicate_class_dict, pos_dict):
    """Calculate predicate feature. 
    row = a dictionary representing a row from the marneffe_data.csv file.
    """
    pk=primary_key(row)
    event_index=event(pk, event_dict)
    sdp=sd_parse(pk, sdp_dict)
    t=predicate_trail(pk, event_index, sdp, pos_dict)
    f=[]
    for (predicate, pos, relation, depth) in t[:1]:
        temp_key=(predicate, pos, relation)
        if temp_key in predicate_class_dict:
            f.extend([predicate_class_dict[temp_key], lemma(predicate)])
    return f

def primary_key(row):
    """input: dict(file=, sentId=, eId=, eiId=, eText=, )
    output: (file, sentId, eId, eiId)
    """
    return (row["file"], row["sentId"], row["eId"], row["eiId"])
    

def event(pk, event_dict):
    """input: (file, sentId, eId, eiId)
    output: event_dict[(file, sentId, eId)]
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
    return pos_dict[(pk[0], pk[1], token_index)]

def predicate_trail(pk, event_index, sdp, pos_dict):
    """input: event_index=8, sdp=[(root ROOT, 0, lucky, 6), (xcomp, lucky, 6, break, 8), advmod(break-8, even-9), xsubj(break-8, Kwan-3), aux(break-8, to-7)]
    output: [(lucky, POS_of_lucky, xcomp, 1), (ROOT, ROOT, root_xcomp, 2)]
    """
    pass

def lemma(word):
    """input:
    output:
    """
    return wordNetLemmatizer.lemmatize(word)

def predicate_class_dict_maker():
    """output: dict((predicate, pos, relation))
    """
    d={}
    for l in open("appendix b.txt", "rb"):
        l=[e.strip() for e in l.strip().split("|")][1:-1]
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
    """
    tml_file_path = os.path.join(factbank_path, "annotation", "tokens_tml.txt")
    d={}
    for l in open(tml_file_path, "rb"):
        l=l.strip().split(FACTBANK_SPLITTER)
        _file=l[0][1:-1]; assert l[0][0]=="'"
        sendId=l[1]
        tmlTagId=l[5][1:-1]; assert l[5][0]=="'"
        tokLoc=int(l[2])
        d[(_file, sendId, tmlTagId)] = tokLoc - 1 
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
            temp.append(gg.groups())
            try: 
                l=_f.next()
            except StopIteration:
                return sd_parses
    return sd_parses


def sdp_dict_maker(factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data", parse_pickle="parse.pickle"):
    """output: gets parse for (file, sentId) in sdp_dict
    """
    sentence_file_path = os.path.join(factbank_path, "annotation", "sentences.txt")
    # If the results does not exist or is older than sentence_file
    if (not os.path.exists(parse_pickle)) or (os.path.getmtime(parse_pickle) < os.path.getmtime(sentence_file_path)):
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
        os.system("make factbank.sdp")        
        #Then extract the stanford parses from the sentence file by keeping only the needed portion
        #The stanford parse for a sentence is a list of 5 tuples
        parses = extract_stanford_parses_from_sdp_file(sd_parse_file_name = "factbank.sdp")
        #Then make sure that the number of lists is exactly equal to the number of sentences
        assert len(parses) == len(filename_sentId)
        d=dict(zip(filename_sentId, parses))
        #Store this in a pickle
        with open(parse_pickle, "wb") as parse_pickle_f:
            cPickle.dump(d, parse_pickle_f)
        return d
    else:
        d=cPickle.load(open(parse_pickle, "rb"))
        assert type(d) is dict
        return d

def pos_dict_maker(factbank_path):
    """output: dict( (file, sentence, token_index) )
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
    
