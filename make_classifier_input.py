import sys 
from csv import DictReader
import os
argv=sys.argv
CLASSES=["CT_plus","CT_minus","PR_plus","PR_minus","PS_plus","PS_minus","Uu"]
csv_filename=argv[1]
MODE=argv[-1]
if MODE == "bow":
    factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    sentence_file_path = os.path.join(factbank_path, "annotation", "sentences.txt")
    FACTBANK_SPLITTER="|||"
    d={}
    for l in open(sentence_file_path):
        l=l.strip().split(FACTBANK_SPLITTER)
        fb_filename=l[0][1:-1]; assert l[0][0]=="'"
        sentId=l[1]
        sentence=l[2][1:-1].replace(r"\'", "'").strip()
        d[(fb_filename, sentId)]=sentence

    with open(csv_filename) as csv_file:
        _csv=DictReader(csv_file)
        for row in _csv:
            majority = [_class for _class in CLASSES if int(row[_class])>=6]
            if majority != []:
                sys.stdout.write(majority[0])
                sys.stdout.write("\t")
                sys.stdout.write(d[(row["file"], row["sentId"])])
                sys.stdout.write("\n")
elif MODE=="pgcqmn":
    _csv=DictReader(open(csv_filename))
    predicate_fn = open(argv[2], "rb") 
    general_fn = open(argv[3], "rb") 
    conditional_fn = open(argv[4], "rb") 
    quotation_fn = open(argv[5], "rb") 
    modality_fn = open(argv[6], "rb") 
    negation_fn = open(argv[7], "rb")
    for row in map(lambda a,b,c,d,e,f,g : (a,b.strip(),c.strip(),d.strip(),e.strip(),f.strip(),g.strip()), _csv, predicate_fn, general_fn, conditional_fn, quotation_fn, modality_fn, negation_fn):
        assert all(e is not None for e in row)
        majority = [_class for _class in CLASSES if int(row[0][_class])>=6]
        if majority != []:
            sys.stdout.write(majority[0])
            sys.stdout.write("\t")
            sys.stdout.write(" ".join(row[1:]))
            sys.stdout.write("\n")

elif MODE=="pgcqmnbow":

    _csv=DictReader(open(csv_filename))
    predicate_fn = open(argv[2], "rb") 
    general_fn = open(argv[3], "rb") 
    conditional_fn = open(argv[4], "rb") 
    quotation_fn = open(argv[5], "rb") 
    modality_fn = open(argv[6], "rb") 
    negation_fn = open(argv[7], "rb")
    factbank_path=r"/Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data"
    sentence_file_path = os.path.join(factbank_path, "annotation", "sentences.txt")
    FACTBANK_SPLITTER="|||"
    d={}
    for l in open(sentence_file_path):
        l=l.strip().split(FACTBANK_SPLITTER)
        fb_filename=l[0][1:-1]; assert l[0][0]=="'"
        sentId=l[1]
        sentence=l[2][1:-1].replace(r"\'", "'").strip()
        d[(fb_filename, sentId)]=sentence
    for i, row in enumerate(map(lambda a,b,c,d,e,f,g : (a,b.strip(),c.strip(),d.strip(),e.strip(),f.strip(),g.strip()), _csv, predicate_fn, general_fn, conditional_fn, quotation_fn, modality_fn, negation_fn)):
        print >>sys.stderr, i
        assert all(e is not None for e in row)
        majority = [_class for _class in CLASSES if int(row[0][_class])>=6]
        if majority != []:
            sys.stdout.write(majority[0])
            sys.stdout.write("\t")
            sys.stdout.write(" ".join(row[1:]))
            sys.stdout.write(d[(row[0]["file"], row[0]["sentId"])])
            sys.stdout.write("\n")
