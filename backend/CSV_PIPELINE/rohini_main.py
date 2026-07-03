from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import get_user_id, get_recommendations, update_interactions, update_user_preferences
from utils import read_csv

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Endpoints ----------

@app.get("/api/login/{name}")
def login(name: str):
    user_id = get_user_id(name)
    if not user_id:
        return {"error": "Name not recognized."}
    return {"user_id": user_id}

@app.get("/api/recommendations/{user_id}")
def recommendations(user_id: str):
    recs = get_recommendations(user_id)
    return recs.to_dict(orient="records")

@app.post("/api/interactions/{user_id}")
def interactions(user_id: str, data: list):
    update_interactions(user_id, data)
    return {"status": "ok"}

@app.post("/api/preferences/{user_id}")
def preferences(user_id: str, data: dict):
    update_user_preferences(user_id, liked_cat=data.get("liked_cat"), liked_subcat=data.get("liked_subcat"))
    return {"status": "ok"}

@app.get("/api/content")
def get_content():
    content_df = read_csv("content.csv")
    return content_df.to_dict(orient="records")

@app.get("/api/preferences/{user_id}")
def get_preferences(user_id: str):
    users_df = read_csv("users.csv")
    user_row = users_df[users_df["user_id"] == user_id]
    if user_row.empty:
        return {"liked_cat": [], "liked_subcat": []}
    liked_cat = user_row.iloc[0].liked_cat if "liked_cat" in user_row.columns else []
    liked_subcat = user_row.iloc[0].liked_subcat if "liked_subcat" in user_row.columns else []
    return {"liked_cat": liked_cat, "liked_subcat": liked_subcat}
