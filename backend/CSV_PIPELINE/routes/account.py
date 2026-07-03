# backend/routes/account.py
import os
from fastapi import APIRouter, HTTPException
from azure.storage.blob import BlobServiceClient
import utils
import pandas as pd
import ast

router = APIRouter(prefix="/account", tags=["account"])

CONTAINER_NAME = "recsys"
USERS_BLOB = "users/users.csv"
CONTENT_BLOB = "content/content.csv"

AZ_CONN = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
LOCAL_DIR = os.getenv("LOCAL_DATA_DIR")

if LOCAL_DIR:
    container_client = LOCAL_DIR
else:
    if not AZ_CONN:
        raise RuntimeError("Set AZURE_STORAGE_CONNECTION_STRING or LOCAL_DATA_DIR")
    blob_service_client = BlobServiceClient.from_connection_string(AZ_CONN)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@router.get("/user/{user_id}")
async def get_user(user_id: str):
    df = utils.blob_to_df(container_client, USERS_BLOB)
    if df.empty:
        raise HTTPException(status_code=404, detail="Users file missing")
    row = df[df['user_id']==user_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="User not found")
    rec = row.iloc[0].to_dict()
    # try parse liked_cat/subcat if stored as stringified list
    for k in ['liked_cat','liked_subcat']:
        if k in rec and isinstance(rec[k], str):
            try:
                rec[k] = ast.literal_eval(rec[k])
            except Exception:
                # leave as string if parse fails
                pass
    return rec

@router.get("/content")
async def get_content():
    df = utils.blob_to_df(container_client, CONTENT_BLOB)
    if df.empty:
        return {"content": [], "categories": [], "sub_categories": []}
    cats = sorted(df['category'].dropna().unique().tolist())
    subcats = sorted(df['sub_category'].dropna().unique().tolist())
    return {"content": df.fillna("").to_dict(orient="records"), "categories": cats, "sub_categories": subcats}

@router.post("/update")
async def update_preferences(payload: dict):
    if 'user_id' not in payload:
        raise HTTPException(status_code=400, detail="Missing user_id")
    users_df = utils.blob_to_df(container_client, USERS_BLOB)
    if users_df.empty:
        raise HTTPException(status_code=500, detail="Users file missing")
    user_id = payload['user_id']
    liked_cat = payload.get('liked_cat', [])
    liked_subcat = payload.get('liked_subcat', [])
    users_df.loc[users_df['user_id'] == user_id, 'liked_cat'] = str(liked_cat)
    users_df.loc[users_df['user_id'] == user_id, 'liked_subcat'] = str(liked_subcat)
    # write back
    if LOCAL_DIR:
        out_path = os.path.join(LOCAL_DIR, os.path.basename(USERS_BLOB))
        users_df.to_csv(out_path, index=False)
    else:
        container_client.get_blob_client(USERS_BLOB).upload_blob(users_df.to_csv(index=False), overwrite=True)
    return {"status":"success"}
