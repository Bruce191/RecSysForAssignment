# backend/routes/learn.py
from fastapi import APIRouter

router = APIRouter(prefix="/learn", tags=["learn"])

@router.get("/")
async def learn():
    return {
        "title": "Learn about us",
        "content": [
            "Welcome! 👋 This simple app gives you personalised news recommendations.",
            "Log in with your name on the login page.",
            "You can like, dislike, share or report items to record interactions for future recommendations."
        ]
    }
