#Check http://web.mit.edu/gnu/doc/html/make_10.html#SEC94 for explanation
#run make train.sdp and then maketrain_predicate.features

train.csv test.csv : marneffe_data.csv
	python split_into_train_test.py marneffe_data.csv

%.sent : %.csv 
	python csv_to_single_sentence_per_line.py $< $@

%.sdp : %.sent 
	java -cp /Users/pushpendrerastogi/stanford-corenlp-full-2013-06-20/stanford-corenlp-3.2.0.jar:/Users/pushpendrerastogi/stanford-corenlp-full-2013-06-20/stanford-corenlp-3.2.0-models.jar -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,parse -outputExtension ".out" -file  $< && cp $<.out $@

%_predicate.features : %.sdp %.csv #TODO
	python extract_predicate_features.py $^ $@

train_loglinear_model : train_predicate.features
	echo "TODO"