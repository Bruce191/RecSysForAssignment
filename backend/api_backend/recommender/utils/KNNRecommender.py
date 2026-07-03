import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds

class KNNRecommender:
    def __init__(self, n_neighbors=100):
        self.n_neighbors = n_neighbors
        self.model = None
        self.user_item_matrix = None

    def fit(self, user_item_matrix):
        self.user_item_matrix = user_item_matrix
        self.model = NearestNeighbors(n_neighbors=self.n_neighbors, metric='cosine')
        self.model.fit(user_item_matrix.values)

    def recommend(self, user_id, n_recommendations=100):
        if self.model is None:
            raise ValueError("Model is not trained yet. Call `fit` with user-item matrix before recommending.")
        
        if user_id not in self.user_item_matrix.index:
            raise ValueError(f"User ID {user_id} not found in the user-item matrix.")
        
        user_vector = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
        distances, indices = self.model.kneighbors(user_vector, n_neighbors=self.n_neighbors + 1)
        similar_user_indices = indices.flatten()[1:]

        similar_users_items = self.user_item_matrix.iloc[similar_user_indices]
        mean_ratings = similar_users_items.mean(axis=0)
        
        user_rated_items = self.user_item_matrix.loc[user_id]
        unrated_items = user_rated_items[user_rated_items == 0].index
        
        recommendations = mean_ratings.loc[unrated_items].sort_values(ascending=False)
        return recommendations.head(n_recommendations).index.tolist()
