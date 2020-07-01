import pandas as pd
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from scipy.spatial import distance
from sklearn.metrics.pairwise import euclidean_distances
from nltk.stem.porter import PorterStemmer
from django.conf import settings

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))



def preprocess(text):
	tokenized = text.lower().split()
	preprocess_tokens = [stemmer.stem(term) for term in tokenized if term not in stop_words]
	return ' '.join(preprocess_tokens)


def generateSimilarity(df, query_string, column_to_process):
	target_column = 'pre_process'
	df[target_column] = df[column_to_process].apply(preprocess)

	all_names = [query_string] + df[target_column].tolist()

	# BOW representation
	vectorizer = CountVectorizer()
	cnt_vectorizer = vectorizer.fit_transform(all_names)

	# TF-IDF representation
	tfidf_transformer = TfidfTransformer()
	tfidf_transformer.fit(cnt_vectorizer)

	# df['query_string'] = query_string

	# text embedding for search query
	q_string_cnt_vector = vectorizer.transform([query_string])
	q_string_tfidf_vector = tfidf_transformer.transform(q_string_cnt_vector)

	TFIDF_COSINE = []

	def getTextSimilarity(result_name):
		nonlocal q_string_tfidf_vector
		result_string_cnt_vector = vectorizer.transform([result_name])
		result_string_tfidf_vector = tfidf_transformer.transform(result_string_cnt_vector)

		# TFIDF Cosine
		tfidf_cosine = distance.cosine(q_string_tfidf_vector[0].toarray(),result_string_tfidf_vector[0].toarray())
		TFIDF_COSINE.append(tfidf_cosine)

	df[target_column].apply(getTextSimilarity)

	df['TFIDF_COSINE'] = TFIDF_COSINE
	del df[target_column]			# removing temp preprocessed column
	df['text_match_weightage'] = df['TFIDF_COSINE'].rank(ascending=True).astype(int)
	df['text_match_weightage'] = settings.TEXT_WEIGHTAGE/df['text_match_weightage']
	return df

