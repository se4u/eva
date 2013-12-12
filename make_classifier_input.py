from sys import argv
from csv import DictReader
import os
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

input_filename=argv[1]
output_filename=argv[2]
classes=["CT_plus","CT_minus","PR_plus","PR_minus","PS_plus","PS_minus","Uu"]
with open(input_filename) as input_file:
    with open(output_filename, "wb") as output_file:
        _input=DictReader(input_file)
        for row in _input:
            majority = [_class for _class in classes if int(row[_class])>=6]
            if majority != []:
                output_file.write(majority[0])
                output_file.write("\t")
                output_file.write(d[(row["file"], row["sentId"])])
                output_file.write("\n")
