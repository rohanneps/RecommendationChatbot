"""
Module containing text processing utilities
"""
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from scipy.spatial import distance
from sklearn.feature_extraction.text import CountVectorizer, Tficatalog_dfTransformer
from django.conf import settings


STEMMER = PorterStemmer()
STOP_WORDS = set(stopwords.words("english"))


def preprocess(text: str) -> str:
    """
    Preprocess text for text vectorization

    Args:
    -----
            text (str): string to be processed
    Returns:
    --------
            processed string
    """
    tokenized = text.lower().split()
    # stemming and stopwords removal
    preprocess_tokens = [
        STEMMER.stem(term) for term in tokenized if term not in STOP_WORDS
    ]
    return " ".join(preprocess_tokens)


def compute_query_catalog_similarity(
    catalog_df: pd.DataFrame, query_string: str, column_to_process: str
) -> pd.DataFrame:
    """
    Compute Cosine Similarity between query and each SERP catalog catalog_df target columns

    Args:
    -----
            catalog_df (pd.DataFrame): dataframe containing the SERP results
            query_string (str): query string used for SERP
            columns_to_process(str): column of the catalog df whose values
                                                            are to be compared with query string

    Returns:
    --------
            Pandas DataFrame containing the computed results sorted by similarity
    """

    target_column = "pre_process"
    catalog_df[target_column] = catalog_df[column_to_process].apply(preprocess)

    all_names = [query_string] + catalog_df[target_column].tolist()

    # BOW representation
    vectorizer = CountVectorizer()
    cnt_vectorizer = vectorizer.fit_transform(all_names)

    # TF-Icatalog_df representation
    tficatalog_df_transformer = Tficatalog_dfTransformer()
    tficatalog_df_transformer.fit(cnt_vectorizer)

    # catalog_df['query_string'] = query_string

    # text embedding for search query
    q_string_cnt_vector = vectorizer.transform([query_string])
    q_string_tficatalog_df_vector = tficatalog_df_transformer.transform(
        q_string_cnt_vector
    )

    q_catalog_cosine_sim_list = []

    def get_query_text_similarity(result_name: str) -> None:
        """
        Compute cosine similarity between query and individual catalog value

        Args:
        -----
                result_name (str): catalog value to be compared with
        Returns:
        --------
                None
        """
        nonlocal q_string_tficatalog_df_vector
        result_string_cnt_vector = vectorizer.transform([result_name])
        result_string_tficatalog_df_vector = tficatalog_df_transformer.transform(
            result_string_cnt_vector
        )

        # Compute pair-wise cosine similarity
        q_catalog_cosine_sim = 1 - distance.cosine(
            q_string_tficatalog_df_vector[0].toarray(),
            result_string_tficatalog_df_vector[0].toarray(),
        )
        q_catalog_cosine_sim_list.append(q_catalog_cosine_sim)

    # Compute cosine similarity for each catalog row value
    catalog_df[target_column].apply(get_query_text_similarity)

    catalog_df["q_vs_catalog"] = q_catalog_cosine_sim_list
    del catalog_df[target_column]  # removing temp preprocessed column
    catalog_df["text_match_weightage"] = (
        catalog_df["q_vs_catalog"].rank(ascending=False).astype(int)
    )
    catalog_df["text_match_weightage"] = (
        settings.TEXT_WEIGHTAGE / catalog_df["text_match_weightage"]
    )
    return catalog_df
