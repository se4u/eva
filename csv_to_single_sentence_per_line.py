import sys, csv
input_file_name=sys.argv[1]
output_file_name=sys.argv[2]
factbank_path=sys.argv[3]
d=csv.DictReader(open(input_file_name))
ld=list(d)

f=open(output_file_name, "wb")
for e in ld:
    f.write(e["normalization"])
    if e["normalization"][-1] not in ".!":
        f.write(".")
    f.write("\n")
f.close()

