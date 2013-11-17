import csv
import re
import sys
input_file_name=sys.argv[1]
d=csv.DictReader(open(input_file_name))
ld=list(d)

###
## If we set the threhold here to be 0 then we would get all the cases which require lemmatization. Let not care about them for a moment
ll=[e for e in ld if len(re.findall(" (%s)([ .]|$)"%e["eText"], e["normalization"]))==1]
for data_type in ["train", "test"]:
    llt=[e for e in ll if e["split"]==data_type]
    f=open(data_type+".csv", "wb")
    fields=["file", "sentId", "eId", "eiId", "eText", "normalization", "CT_plus", "CT_minus", "PR_plus", "PR_minus", "PS_plus", "PS_minus", "Uu"]
    dt=csv.DictWriter(f, fields, extrasaction='ignore')
    dt.writerow(dict(zip(fields, fields)))
    dt.writerows(llt)
    f.close()

