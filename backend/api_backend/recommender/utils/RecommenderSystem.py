import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds

from .KNNRecommender import KNNRecommender
from .SVDRecommender import SVDRecommender

class RecommenderSystem:
    def __init__(self, interactions_df, model_type='KNN', **kwargs):
        self.interactions_df = interactions_df
        self.user_item_matrix = None
        self.recommendations_cache = {}

        if model_type == 'KNN':
            self.model = KNNRecommender(**kwargs)
        elif model_type == 'SVD':
            self.model = SVDRecommender(**kwargs)
        else:
            raise ValueError("Unsupported model type. Choose 'KNN' or 'SVD'.")
        
        self.fit()

    def fit(self):
        self.user_item_matrix = self.interactions_df.pivot_table(
            index='user_id', columns='content_id', values='ResolvedScore', aggfunc='sum').fillna(0)
        self.model.fit(self.user_item_matrix)

    def recommend(self, user_id, n_recommendations=100):
        if user_id not in self.recommendations_cache:
            self.recommendations_cache[user_id] = self.model.recommend(user_id, n_recommendations)
        return self.recommendations_cache[user_id][:n_recommendations]

    def get_more_recommendations(self, user_id, start_idx, n_recommendations):
        return self.recommendations_cache[user_id][start_idx:start_idx + n_recommendations]
