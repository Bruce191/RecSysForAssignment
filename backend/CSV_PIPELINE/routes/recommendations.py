# backend/routes/recommendations.py
import os
from fastapi import APIRouter, HTTPException, Query
from azure.storage.blob import BlobServiceClient
import utils
import pandas as pd
from datetime import datetime
import random

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

CONTAINER_NAME = "recsys"
RANKED_BLOB = "ranked_recommendations/ranked_recommendations.csv"
INTERACTIONS_BLOB = "interactions/interactions.csv"

AZ_CONN = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
LOCAL_DIR = os.getenv("LOCAL_DATA_DIR")

if LOCAL_DIR:
    container_client = LOCAL_DIR
else:
    if not AZ_CONN:
        raise RuntimeError("Set AZURE_STORAGE_CONNECTION_STRING or LOCAL_DATA_DIR")
    blob_service_client = BlobServiceClient.from_connection_string(AZ_CONN)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@router.get("/{user_id}")
async def get_recommendations(user_id: str, start: int = 0, end: int = 100):
    df = utils.blob_to_df(container_client, RANKED_BLOB)
    if df.empty:
        return {"recommendations": []}
    user_df = df[df['user_id'] == user_id].reset_index(drop=True)
    sliced = user_df.iloc[start:end]
    # Ensure JSON-serializable types
    return {"recommendations": sliced.fillna("").to_dict(orient="records")}

@router.post("/interaction")
async def record_interaction(payload: dict):
    required = ['user_id', 'content_id', 'interaction_type']
    for r in required:
        if r not in payload:
            raise HTTPException(status_code=400, detail=f"Missing {r}")
    try:
        int_df = utils.blob_to_df(container_client, INTERACTIONS_BLOB)
    except Exception:
        int_df = pd.DataFrame(columns=['interaction_id','user_id','content_id','interaction_type','interaction_date'])
    # if empty DataFrame returned
    if int_df is None or (isinstance(int_df, pd.DataFrame) and int_df.empty):
        int_df = pd.DataFrame(columns=['interaction_id','user_id','content_id','interaction_type','interaction_date'])
    new_entry = {
        "interaction_id": random.randint(100000, 999999),
        "user_id": payload['user_id'],
        "content_id": payload['content_id'],
        "interaction_type": payload['interaction_type'],
        "interaction_date": datetime.today().strftime("%Y-%m-%d")
    }
    updated = pd.concat([int_df, pd.DataFrame([new_entry])], ignore_index=True)
    # write back
    if LOCAL_DIR:
        out_path = os.path.join(LOCAL_DIR, os.path.basename(INTERACTIONS_BLOB))
        updated.to_csv(out_path, index=False)
    else:
        container_client.get_blob_client(INTERACTIONS_BLOB).upload_blob(updated.to_csv(index=False), overwrite=True)
    return {"status":"success", "entry": new_entry}
