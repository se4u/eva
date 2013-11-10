##
#Create Predicate features by using the stanfor dependency parses and the event introducing verbs etc.
##
import sys, csv
stanford_parse_file_name=sys.argv[1]
complete_csv_file_name=sys.argv[2]
output_file_name=sys.argv[3]
d=csv.DictReader(open(stanford_parse_file_name))
ld=list(d)
for e in ld:
    f.write(e["normalization"])


#| Judge | eText    | normalization                                                | CT_plus | CT_minus | PR_plus | PR_minus | PS_plus | PS_minus | Uu |
#| Readr | agree    | Justices Sandra Day O'Connor and Anthony Kennedy agree       |       1 |        0 |       8 |        0 |       0 |        0 |  1 |
#|       |          | that the law amounted to unconstitutional sex discrimination |         |          |         |          |         |          |    |
#| Readr | hint     | there was no hint of trouble in the last conversation        |      10 |        0 |       0 |        0 |       0 |        0 |  0 |
#| Readr | arrests  | there have been arrests in the slayings                      |       0 |       10 |       0 |        0 |       0 |        0 |  0 |
#| Readr | amounted | the law amounted to unconstitutional sex discrimination      |       3 |        0 |       4 |        0 |       2 |        0 |  1 |
#| Readr | raised   | the issues had been raised before                            |       0 |       10 |       0 |        0 |       0 |        0 |  0 |



#*Predicate classes*
#Sauri's thesis defines classes of predicates(nouns and verbs) that project the same veridicality value onto the events they introduce. (Appendix A, P#Age 164)
#The classes also define the grammatical relations that need to hold between the predicate and the event it introduces, because grammatical contexts
#matter for veridicality.
#
#Different veridicality values will indeed be assigned to X in He doesnt know that X and in He doesnt know if X.
#The classes have names like ANNOUNCE, CONFIRM, CONJECTURE, and SAY.
#We used dependency graphs produced by the Stanford parser to follow the path from the target event to the root of the sentence.
#
#If a predicate in the path was contained in one of the classes and the grammatical relation matched, 
#      we added 
#         1. the lemma of the predicate as a feature
#         2. a feature marking the predicate class.



