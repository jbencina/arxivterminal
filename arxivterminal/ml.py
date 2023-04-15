import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
from joblib import dump, load
from numpy import dot
from numpy.linalg import norm
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer

from arxivterminal.db import ArxivDatabase
from arxivterminal.models import ArxivPaper


def cosine_sim(a, b):
    """Return cosine similarity"""
    return dot(a, b.T) / (norm(a) * norm(b))


class LsaDocumentSearch:
    def __init__(self, model_path: str):
        """
        Initialize an instance of the LsaDocumentSearch class.

        Parameters
        ----------
        model_path : str
            Path to the pre-trained model file.
        """
        self.model_path = model_path
        self.is_trained = Path(model_path).exists()

        if self.is_trained:
            self.model = load(self.model_path)
        else:
            self.model = None

    def fit(
        self,
        papers: List[ArxivPaper],
        force_overwrite: bool = False,
        min_df: int = 5,
        max_df: Union[float, int] = 0.7,
        ngram_range: Tuple = (1, 2),
        max_features: Optional[int] = 3000,
        sublinear_tf: bool = True,
        embedding_dim: int = 64,
    ):
        """
        Train the LSA model on a list of ArxivPaper objects.

        Parameters
        ----------
        papers : List[ArxivPaper]
            A list of ArxivPaper objects for training the model.
        force_overwrite : bool, optional
            If True, overwrites the existing model if one exists, by default False.
        min_df : int, optional
            Minimum document frequency for the TfidfVectorizer, by default 5.
        max_df : Union[float, int], optional
            Maximum document frequency for the TfidfVectorizer, by default 0.7.
        ngram_range : Tuple, optional
            N-gram range for the TfidfVectorizer, by default (1, 2).
        max_features : Optional[int], optional
            Maximum features for the TfidfVectorizer, by default 3000.
        sublinear_tf : bool, optional
            If True, applies sublinear term frequency scaling, by default True.
        embedding_dim : int, optional
            The number of components for TruncatedSVD, by default 64.
        """
        if self.is_trained and not force_overwrite:
            logging.info(f"Model already trained at {self.model_path}")
            return

        abstracts = [p.summary for p in papers]

        vectorizer = TfidfVectorizer(
            min_df=min_df,
            max_df=max_df,
            stop_words="english",
            ngram_range=ngram_range,
            max_features=max_features,
            sublinear_tf=sublinear_tf,
        )

        svd = TruncatedSVD(n_components=embedding_dim)

        normalizer = Normalizer()

        pipeline = Pipeline([("tfidf", vectorizer), ("svd", svd), ("norm", normalizer)])

        pipeline.fit(abstracts)

        self.model = pipeline
        self.is_trained = True
        dump(pipeline, self.model_path)
        logging.info(f"Trained and saved model to {self.model_path}")

    def find_match(
        self,
        papers: List[ArxivPaper],
        query: str,
        limit: int = 10,
        force_refresh: bool = False,
    ):
        """
        Find the most similar papers to a given query.

        Parameters
        ----------
        papers : List[ArxivPaper]
            A list of ArxivPaper objects to search.
        query : str
            The search query.
        limit : int, optional
            The maximum number of similar papers to return, by default 10.
        force_refresh: bool, optional
            Forces a refresh of the trained model

        Returns
        -------
        List[ArxivPaper]
            A list of ArxivPaper objects that are most similar to the query.
        """
        abstracts = [p.summary for p in papers]

        if force_refresh:
            self.fit(papers, force_overwrite=True)

        reference = self.model.transform(abstracts)
        lookup = self.model.transform([query])
        sim = cosine_sim(lookup, reference)

        vals = np.argsort(-sim)[0, :limit]
        top_papers = [papers[i] for i in vals]
        return top_papers

    def search(
        self,
        db: ArxivDatabase,
        query: str,
        limit: int = 10,
        force_refresh: bool = False,
    ):
        """
        Search for similar papers in the database using the given query.

        Parameters
        ----------
        db : ArxivDatabase
            An instance of the ArxivDatabase class.
        query : str
            The search query.
        limit : int, optional
            The maximum number of similar papers to return, by default 10.
        force_refresh: bool, optional
            Forces a refresh of the trained model

        Returns
        -------
        List[ArxivPaper]
            A list of ArxivPaper objects that are most similar to the query.
        """
        papers = db.get_papers()
        return self.find_match(papers, query, limit=limit, force_refresh=force_refresh)
