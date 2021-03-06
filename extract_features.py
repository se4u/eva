""" This file creates Predicate features by using csv sentences and path to factbank.
It is called as
python extract_predicate_features.py train.csv /Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data train_predicate.features
python extract_predicate_features.py test.csv /Users/pushpendrerastogi/Dropbox/evsem_data/factbank/data test_predicate.features

The csv file is like this
file,sentId,eId,eiId,eText,normalization,CT_plus,CT_minus,PR_plus,PR_minus,PS_plus,PS_minus,Uu
ABC19980108.1830.0711.tml,15,e30,ei398,break,Wong Kwan will break even,0,0,0,5,0,1,4

The output features are calculated by the following rule.
If a predicate in the path was contained in one of the classes and the grammatical relation matched, 
we add
1. the lemma of the predicate as a feature
2. a feature marking the predicate class.

Here the actual sentence is in factbank/data/sentences.txt: 'ABC19980108.1830.0711.tml'|||15|||'And Wong Kwan will be lucky to break even.'
Its stanford dependency parse contains the following text.
cc(lucky-6, And-1)
nn(Kwan-3, Wong-2)
nsubj(lucky-6, Kwan-3)
aux(lucky-6, will-4)
cop(lucky-6, be-5)
root(ROOT-0, lucky-6)
xcomp(lucky-6, break-8)
advmod(break-8, even-9)
xsubj(break-8, Kwan-3)
aux(break-8, to-7)

The event "break" is given by the file catbank/data/fb_event.txt with the primary key 'ABC19980108.1830.0711.tml'|||15|||'e30'|||'ei398'|||'break'
The factuality value is given in the csv, under headings CT_minus etc.
basically we duplicate the features once per category.

Now since Lucky is between root and break Root -> Lucky -> Break
and it is adjective (the token_ling and tokens_tml contains pos tags and info about which token is the event)
and in the list of predicates
and the relation between lucky and break is xcomp
Therefore it would apply

And we would fire the following features
1. Lemma of all the predicate that are between the target event and the root of the sentence ?. so lucky is a feature. event_root_1_lucky:1 1 specifies the level above the event.) 
2. Feature marking the predicate class ? (so we'll be marking the predicate class of the event_root_1_class_want:1)

The features for the following sentences would be
| Judge | eText    | normalization                                                | CT_plu | CT_min | PR_plu | PR_min | PS_plu | PS_min | Uu |
| Readr | agree    | Justices Sandra Day O'Connor and Anthony Kennedy agree       |     1 |     0 |     8 |     0 |     0 |     0 |  1 |
|       |          | that the law amounted to unconstitutional sex discrimination |       |       |       |       |       |       |    |
| Readr | hint     | there was no hint of trouble in the last conversation        |    10 |     0 |     0 |     0 |     0 |     0 |  0 |
| Readr | arrests  | there have been arrests in the slayings                      |     0 |    10 |     0 |     0 |     0 |     0 |  0 |
| Readr | amounted | the law amounted to unconstitutional sex discrimination      |     3 |     0 |     4 |     0 |     2 |     0 |  1 |
| Readr | raised   | the issues had been raised before                            |     0 |    10 |     0 |     0 |     0 |     0 |  0 |
########################## GENERAL FEATURES
The lemma of the event
The lemma of the root of the sentence
The incoming grammatical relation to the event
A general class feature. 


#### GENERIC FACTBANK INFO
There are 2 source tables
1. fb_relSource these introduce stuff that I dont know and I leaving for now f26 s0 -1 
2. fb_source

I need to know the 
The file sentId eId eiId are described in factbank
factbank contains 2 folders
data
   original - contains files from wsj, APW, NYT, ABC, CNN etc.
   annotation - offsets, sentences
                fb_corefSource.txt
                fb_factValue.txt
                fb_sip.txt
                fb_source.txt        
                fb_event.txt
                fb_relSource.txt
                fb_sipAndSource.txt
                fb_sourceString.txt

                tml_alink.txt
                tml_event.txt
                tml_instance.txt
                tml_signal.txt
                tml_slink.txt
                tml_timex3.txt
                tml_tlink.txt     

                tokens_ling.txt
                tokens_tml.txt
docs
   readme.pdf
"""
import sys, csv
sys.path.append("")
from extract_features_lib import event_dict_maker, predicate_class_dict_maker, sdp_dict_maker, pos_dict_maker, predicate_feature, general_feature, conditional_feature, quotation_feature, modality_feature, negation_feature, worldknowledge_feature, sentence_dict_maker
argv=sys.argv
feature_type=argv[1]
input_file_name=argv[2]
factbank_path=argv[3]
output_file_name=argv[4]
predicate_class_dict=predicate_class_dict_maker()
event_dict=event_dict_maker(factbank_path)
sdp_dict=sdp_dict_maker(factbank_path)
pos_dict=pos_dict_maker(factbank_path)
sentence_dict=sentence_dict_maker(factbank_path)
_input=csv.DictReader(open(input_file_name, "rb"))
with open(output_file_name, "wb") as f:
    for e in _input:
        if feature_type=="predicate":
            feature_func=predicate_feature
        elif feature_type=="general":
            feature_func=general_feature
        elif feature_type=="conditional":
            feature_func=conditional_feature
        elif feature_type=="quotation":
            feature_func=lambda a,b,c,d,e: quotation_feature(a,b,c,d,e,sentence_dict)
        elif feature_type=="modality":
            feature_func=modality_feature
        elif feature_type=="negation":
            feature_func=negation_feature
        elif feature_type=="worldknowledge":
            feature_func=worldknowledge_feature
        fff=feature_func(e, event_dict, sdp_dict, predicate_class_dict, pos_dict)
        f.write(" ".join(fff))
        f.write("\n")
exit()

