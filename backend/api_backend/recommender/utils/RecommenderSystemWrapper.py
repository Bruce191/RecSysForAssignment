import mlflow.pyfunc
import cloudpickle
import pandas as pd
from RecommenderSystem import RecommenderSystem

class RecommenderSystemWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        with open(context.artifacts["recommender_pickle"], "rb") as f:
            self.model = cloudpickle.load(f)

    def predict(self, context, model_input):
        user_ids = model_input['user_id']
        return user_ids.apply(lambda uid: self.model.recommend(uid, n_recommendations=100))
