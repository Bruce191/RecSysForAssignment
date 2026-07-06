from fastapi import FastAPI
import uvicorn
from backend.api_backend.RoutesFolder.UserRoutes import router as user_router
from backend.api_backend.RoutesFolder.BackendFunctionRoutes import router as BackendFunctions_router
from fastapi.middleware.cors import CORSMiddleware
from backend.api_backend.Database.db import Base, engine
import os
from backend.api_backend.Database import models
app = FastAPI()

app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(BackendFunctions_router, prefix="/BackendFunctions", tags=["BackendFunctions"])

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://frontend-production-21e03.up.railway.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,   # must allow cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    #uvicorn.run("main:app", reload=True)
    #uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)