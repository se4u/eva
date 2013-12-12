#Check http://web.mit.edu/gnu/doc/html/make_10.html#SEC94 for explanation of these make symbols
#run make train.sdp and then make train_predicate.features

train.csv test.csv : marneffe_data.csv
	python split_into_train_test.py marneffe_data.csv

%.sent : %.csv 
	python csv_to_single_sentence_per_line.py $< $@

%.sdp : %.sent 
# We need top copy in this stupid way because the parser appends the suffix to the original file name
	java -cp /Users/pushpendrerastogi/stanford-corenlp-full-2013-06-20/stanford-corenlp-3.2.0.jar:/Users/pushpendrerastogi/stanford-corenlp-full-2013-06-20/stanford-corenlp-3.2.0-models.jar -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,parse -outputExtension ".out" -ssplit.eolonly -file  $< && cp $<.out $@
##################  Predicate Features
######################################
%_predicate.features : %.csv 
	python extract_features.py predicate $^ ~/Dropbox/evsem_data/factbank/data $@

###################  General Features
#####################################
%_general.features : %.csv
	python extract_features.py general $^ ~/Dropbox/evsem_data/factbank/data $@

################## Conditional Features
############################################
%_conditional.features : %.csv
	python extract_features.py conditional $^ ~/Dropbox/evsem_data/factbank/data $@

################## Quotation Feature
#############################################
%_quotation.features : %.csv
	python extract_features.py quotation $^ ~/Dropbox/evsem_data/factbank/data $@

################## Modality Feature
#############################################
%_modality.features : %.csv
	python extract_features.py modality $^ ~/Dropbox/evsem_data/factbank/data $@

################## Negation Feature
#############################################
%_negation.features : %.csv
	python extract_features.py negation $^ ~/Dropbox/evsem_data/factbank/data $@

################## Worldknowledge Feature
#############################################
%_worldknowledge.features : %.csv
	python extract_features.py worldknowledge $^ ~/Dropbox/evsem_data/factbank/data $@

##################  THE BASELINE
################################
%.classifier_input.bow : %.csv
	python make_classifier_input.py $^ $@

loglinear_model.bow.train_error.bow : train.classifier_input
	java -jar ~/stanford-classifier-2013-11-12/stanford-classifier-3.3.0.jar -prop classifier_bow.prop2 1> $@

loglinear_model.bow.test_error.bow : train.classifier_input test.classifier_input
	java -jar ~/stanford-classifier-2013-11-12/stanford-classifier-3.3.0.jar -prop classifier_bow.prop 1> $@

################# The pgcqmn features
####################################
%.classifier_input.pgcqmn : %_predicate.features %_general.features %_conditional.features %_quotation.features %_negation.features
	#paste -d , $^ > $@
	#This is not complete, actually need to made a script to make the output like the previous one.
loglinear_model.pgcqmn.train_error : train.classifier_input.pgcqmn
	java -jar ~/stanford-classifier-2013-11-12/stanford-classifier-3.3.0.jar -prop classifier_pgcqmn.prop2 1> $@

loglinear_model.pgcqmn.test_error : train.classifier_input.pgcqmn test.classifier_input.pgcqmn
	java -jar ~/stanford-classifier-2013-11-12/stanford-classifier-3.3.0.jar -prop classifier_pgcqmn.prop 1> $@

