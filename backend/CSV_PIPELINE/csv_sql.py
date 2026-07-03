import pandas as pd
from tqdm import tqdm
import logging
from sqlalchemy.orm import Session
from api_backend.Database.db import get_db
from api_backend.Database import models

# Setup logging
logging.basicConfig(
    filename='db_insert_users.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Read CSV
df = pd.read_csv("/home/tdi/Desktop/RecSys Project/RecSys_App/backend/database/users (1).csv", header=0)

def insert_users(db: Session):
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Inserting into DB"):
        try:
            rec = models.users(
                user_id=row["user_id"],
                is_child=row["is_child"],
                name=row["name"],
                restricted_tags=row["restricted_tags"],
                liked_cat=row["liked_cat"]
            )
            db.add(rec)
            logging.info(f"Added user_id={row['user_id']}")
        except Exception as e:
            logging.error(f"Error adding user_id={row['user_id']}: {e}")
    db.commit()

if __name__ == "__main__":
    db = next(get_db())
    insert_users(db)
