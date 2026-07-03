from ..Database.db import SessionLocal
from .pipeline import RecommendationPipeline

def run_recommender():
    db = SessionLocal()
    try:
        RecommendationPipeline(db).run()
        return {"status": "success", "message": "Recommendations updated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

