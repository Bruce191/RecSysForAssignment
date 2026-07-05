from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from backend.api_backend.Database.db import get_db
from backend.api_backend.Database import models

router = APIRouter()

#get all possible new categories - This route displays all possible categories available
@router.get("/preference-categories", summary="Get all news categories for user preferences")
async def get_categories(db: Session = Depends(get_db)):

    categories = db.query(distinct(models.Content.category)).all()
    categories_list = [c[0] for c in categories]

    return categories_list

#get all possible sub-categories - This route displays all possible sub-categories available
@router.get("/preference-sub-categories", summary="Get all news SUB-categories for user preferences")
async def get_sub_categories(db: Session = Depends(get_db)):
    
    results = db.query(
            models.Content.category,
            models.Content.sub_category
            ).filter(
                models.Content.category != None,
                models.Content.sub_category != None
            ).distinct().all()

    return [
        {
            "category": r.category,
            "sub_category": r.sub_category
        }
        for r in results
    ]
    

@router.get("/content", summary="Get all existing news content items")
async def get_all_content(db: Session = Depends(get_db)):
    content_items = db.query(models.Content).all()

    result = []

    for item in content_items:
        result.append({
            "content_id": item.content_id,
            "title": item.title,
            "category": item.category,
            "sub_category": item.sub_category,
            "abstract": item.abstract,
            "harm_category": item.harm_category,
            "is_harmful": item.is_harmful,
        })

    return result


@router.post("/refresh-recommendations", summary="Regenerate recommendations from model")
async def refresh_recommendations():
    from ..recommender.recommender_runner import run_recommender
    result = run_recommender()
    return result