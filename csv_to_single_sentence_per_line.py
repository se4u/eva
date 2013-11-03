import sys, csv
input_file_name=sys.argv[1]
output_file_name=sys.argv[2]
d=csv.DictReader(open(input_file_name))
ld=list(d)

###
## If we set the threhold here to be 0 then we would get all the cases which require lemmatization. Let not care about them for a moment
f=open(output_file_name, "wb")
for e in ld:
    f.write(e["normalization"])
    if e["normalization"][-1] not in ".!":
        f.write(".")
    f.write("\n")
f.close()

