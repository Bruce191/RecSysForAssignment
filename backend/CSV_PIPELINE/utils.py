import pandas as pd
from io import BytesIO
from pathlib import Path
from azure.storage.blob import BlobServiceClient
import os

# ---------- CONFIG ----------
USE_AZURE = os.getenv("USE_AZURE", "false").lower() == "true"

# Azure config (from env or secrets)
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = "recsys"

# Local CSV path
DATA_PATH = Path(__file__).parent / "database"


# ---------- Utility Functions ----------

def blob_to_df(container_client, blob_name):
    client = container_client.get_blob_client(blob_name)
    data = client.download_blob().readall()
    return pd.read_csv(BytesIO(data))


def read_csv(file_name):
    if USE_AZURE:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        return blob_to_df(container_client, file_name)
    else:
        try:
            return pd.read_csv(DATA_PATH / file_name, encoding='utf-8', on_bad_lines='skip')
        except UnicodeDecodeError:
            return pd.read_csv(DATA_PATH / file_name, encoding='latin1', on_bad_lines='skip')

def write_csv(df, file_name):
    if USE_AZURE:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        container_client.get_blob_client(file_name).upload_blob(df.to_csv(index=False), overwrite=True)
    else:
        df.to_csv(DATA_PATH / file_name, index=False)


def remove_prefixes(text, prefixes):
    for prefix in prefixes:
        if text.startswith(prefix):
            return text[len(prefix):]
    return text
