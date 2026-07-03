# backend/routes/login.py
import os
from fastapi import APIRouter, HTTPException
from azure.storage.blob import BlobServiceClient
import utils

router = APIRouter(prefix="/login", tags=["login"])

CONTAINER_NAME = "recsys"
USER_MAP_BLOB = "user_map/user_map.csv"

AZ_CONN = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
LOCAL_DIR = os.getenv("LOCAL_DATA_DIR")

if LOCAL_DIR:
    container_client = LOCAL_DIR
else:
    if not AZ_CONN:
        raise RuntimeError("Set AZURE_STORAGE_CONNECTION_STRING or LOCAL_DATA_DIR")
    blob_service_client = BlobServiceClient.from_connection_string(AZ_CONN)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@router.post("/")
async def login(payload: dict):
    name_input = payload.get("name")
    if not name_input:
        raise HTTPException(status_code=400, detail="Missing name")
    df = utils.blob_to_df(container_client, USER_MAP_BLOB)
    if df.empty:
        raise HTTPException(status_code=500, detail="User map missing")
    mapping = dict(zip(df['name'], df['user_id']))
    if name_input in mapping:
        return {"user_id": mapping[name_input], "name": name_input}
    raise HTTPException(status_code=404, detail="Name not recognized")
