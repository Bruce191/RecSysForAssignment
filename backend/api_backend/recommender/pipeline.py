import pandas as pd
from sqlalchemy.orm import Session
from ..Database import models
from ..recommender.utils import RecommenderSystem


class RecommendationPipeline:

    def __init__(self, db: Session):
        self.db = db


###########################################Load Data START ################################################################

    def load_data(self):
        """Retrieve all relevant data from DB and convert to DataFrames."""

        # ------------------------------------------- USERS START ------------------------------------------- #
        users = self.db.query(models.user_map).all()
        user_df = pd.DataFrame([u.__dict__ for u in users])

        # These columns may not actually exist in the DB yet → fill empty to avoid KeyErrors
        for col in ["liked_cat", "liked_subcat"]:
            if col not in user_df.columns:
                user_df[col] = ""

        self.users_df = user_df[["user_id", "name", "liked_cat", "liked_subcat"]]

        # ------------------------------------------- USERS END ------------------------------------------- #


        # --- INTERACTIONS START
        interactions = self.db.query(models.interactions).all()
        self.interactions_df = pd.DataFrame([i.__dict__ for i in interactions])[
            ["user_id", "content_id", "interaction_type"]
        ]

        # --- CONTENT (REAL TABLE) ---
        content_rows = self.db.query(models.content).all()
        content_df = pd.DataFrame([c.__dict__ for c in content_rows])

        # Guard: if table is empty, avoid crashes later
        if content_df.empty:
            # include abstract column in the schema even if empty
            self.content_df = pd.DataFrame(
                columns=["content_id", "title", "categories", "sub_category", "abstract"]
            )
        else:
            # Your content table columns:
            # content_id, category, sub_category, title, abstract, is_harmful, harm_category
            content_df.rename(columns={"category": "categories"}, inplace=True)

            # 🔹 Safely select only columns that actually exist
            cols = ["content_id", "title", "categories", "sub_category"]
            if "abstract" in content_df.columns:
                cols.append("abstract")
            else:
                # if abstract is missing, create it as empty string
                content_df["abstract"] = ""

            self.content_df = content_df[cols]

        return self
    
###########################################Load Data END ################################################################


##########################################preprocess_interactions START##################################################

    def preprocess_interactions(self):
        """Convert interaction types into scored format for ranking model."""

        if self.interactions_df.empty:
            # No interactions yet → model will rely on fallback later
            self.resolved_scores_df = pd.DataFrame(columns=["user_id", "content_id", "ResolvedScore"])
            return self

        score_map = {
            "Viewed": 2,
            "Like": 3,
            "Dislike": -3,
            "Report": -4,
            "Share": 5,
            "Comment": 4,
        }

        df = self.interactions_df.copy()
        df["ResolvedScore"] = df["interaction_type"].map(score_map).fillna(0)

        # collapse multiple user events → final sentiment score
        self.resolved_scores_df = (
            df.groupby(["user_id", "content_id"])["ResolvedScore"].max().reset_index()
        )

        return self

##########################################preprocess_interactions END ##################################################


##########################################generate_recommendations START ###############################################
    def generate_recommendations(self):
        """Generate ranked list using ML recommender logic."""

        results = []

        # If we have at least one interaction, use the ML model
        if not self.resolved_scores_df.empty and not self.content_df.empty:
            recommender = RecommenderSystem(self.resolved_scores_df, model_type="SVD")

            for user_id in self.users_df["user_id"]:
                try:
                    recs = recommender.recommend(user_id, n_recommendations=100)
                except Exception:
                    # Fallback for users not in the matrix
                    recs = list(
                        self.content_df["content_id"].sample(
                            min(100, len(self.content_df)), replace=False
                        )
                    )
                for rank, content_id in enumerate(recs):
                    results.append(
                        {
                            "user_id": user_id,
                            "content_id": content_id,
                            "rank": rank,
                        }
                    )
        else:
            # No interactions at all OR no content → cold start: random content for everyone
            for user_id in self.users_df["user_id"]:
                if self.content_df.empty:
                    break  # nothing to recommend
                for rank, content_id in enumerate(
                    self.content_df["content_id"].sample(
                        min(100, len(self.content_df)), replace=False
                    )
                ):
                    results.append(
                        {
                            "user_id": user_id,
                            "content_id": content_id,
                            "rank": rank,
                        }
                    )

        self.recommendations_df = pd.DataFrame(results)

        # Attach metadata from the REAL content table (including abstract)
        if not self.recommendations_df.empty:
            self.recommendations_df = self.recommendations_df.merge(
                self.content_df, on="content_id", how="left"
            )

        return self

########################################## generate_recommendations END ##################################################


    def save_to_db(self):
        """Replace existing ranked_recommendations with updated results.

        ⚠️ Only touches ranked_recommendations table. Does NOT modify:
        - users
        - interactions
        - content
        """

        # Clear old recommendations (derived table)
        self.db.query(models.ranked_recommendations).delete()

        # Insert new recommendations
        for _, row in self.recommendations_df.iterrows():
            entry = models.ranked_recommendations(
                user_id=row["user_id"],
                content_id=row["content_id"],
                title=row.get("title", ""),
                category=row.get("categories", ""),
                sub_category=row.get("sub_category", ""),
                abstract=row.get("abstract", ""),
            )
            self.db.add(entry)

        self.db.commit()
        return self





    def run(self):
        """Execute full pipeline."""
        return (
            self.load_data()
            .preprocess_interactions()
            .generate_recommendations()
            .save_to_db()
        )
