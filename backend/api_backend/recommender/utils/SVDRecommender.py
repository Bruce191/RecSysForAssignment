import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds

class SVDRecommender():
    def __init__(self, k=10):
        self.k = k
        self.U = None
        self.S = None
        self.Vt = None
        self.user_item_matrix = None

    def fit(self, user_item_matrix):
        self.user_item_matrix = user_item_matrix
        matrix_values = user_item_matrix.fillna(0).values
        U, S, Vt = svds(matrix_values, k=self.k)
        self.U = U
        self.S = np.diag(S)
        self.Vt = Vt

    def recommend(self, user_id, n_recommendations=100):
        if self.U is None or self.S is None or self.Vt is None:
            raise ValueError("Model is not trained yet. Call `fit` with user-item matrix before recommending.")
        
        if user_id not in self.user_item_matrix.index:
            raise ValueError(f"User ID {user_id} not found in the user-item matrix.")
        
        user_index = self.user_item_matrix.index.get_loc(user_id)
        user_vector = self.U[user_index, :]
        predicted_ratings = np.dot(np.dot(user_vector, self.S), self.Vt)
        
        current_ratings = self.user_item_matrix.loc[user_id].values
        predicted_df = pd.DataFrame(predicted_ratings, index=self.user_item_matrix.columns, columns=['predicted'])
        
        interacted_items = set(self.user_item_matrix.columns[current_ratings > 0])
        all_items = set(self.user_item_matrix.columns)
        items_to_predict = all_items - interacted_items
        
        # Convert the set to a list before using as an indexer
        recommendations = predicted_df.loc[list(items_to_predict)].sort_values(by='predicted', ascending=False)
        top_n = recommendations.head(n_recommendations).index.tolist()
        
        return top_n
