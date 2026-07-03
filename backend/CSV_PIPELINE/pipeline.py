import pandas as pd
import random
from datetime import datetime
from utils import read_csv, write_csv, remove_prefixes

# ---------- Load CSVs ----------
users_df = read_csv("users.csv")
user_map_df = read_csv("user_map.csv")
content_df = read_csv("content.csv")
ranked_recs_df = read_csv("ranked_recommendations.csv")
interactions_df = read_csv("interactions.csv")

# ---------- User management ----------
def get_user_id(name):
    user_map = dict(zip(user_map_df["name"], user_map_df["user_id"]))
    return user_map.get(name)

def get_user_name(user_id):
    user_map = dict(zip(user_map_df["user_id"], user_map_df["name"]))
    return user_map.get(user_id)

# ---------- Recommendations ----------
def get_recommendations(user_id, start=0, end=100):
    recs = ranked_recs_df[ranked_recs_df["user_id"] == user_id].reset_index(drop=True)
    return recs.iloc[start:end]

# ---------- Update interactions ----------
def update_interactions(user_id, new_interactions):
    global interactions_df
    today = datetime.today().strftime("%Y-%m-%d")
    records = []

    for inter in new_interactions:
        record = {
            "interaction_id": random.randint(1000, 9999),
            "user_id": user_id,
            "content_id": inter["content_id"],
            "interaction_type": inter["interaction_type"],
            "interaction_date": today
        }
        records.append(record)

    new_df = pd.DataFrame(records)
    interactions_df = pd.concat([interactions_df, new_df], ignore_index=True)
    write_csv(interactions_df, "interactions.csv")
    return True

# ---------- Update user preferences ----------
def update_user_preferences(user_id, liked_cat=None, liked_subcat=None):
    global users_df
    if liked_cat:
        users_df.loc[users_df["user_id"] == user_id, "liked_cat"] = [liked_cat]
    if liked_subcat:
        users_df.loc[users_df["user_id"] == user_id, "liked_subcat"] = [liked_subcat]
    write_csv(users_df, "users.csv")
    return True
