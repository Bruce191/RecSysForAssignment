from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from datetime import timedelta, datetime
from jose import JWTError, jwt

from backend.api_backend.Database.db import get_db
from backend.api_backend.Database import models
from backend.api_backend.Authentication import security, auth
from backend.api_backend import schemas

router = APIRouter()

#when registering we need to ask for preferences ? Rohini: yes need to redirect to preference page and then refresh recommendations accordingly
@router.post("/register", summary = "User self Register", response_model=schemas.UserResponse) #add a response model
async def user_register(request: Request, User_Register: schemas.UserRegister, db: Session = Depends(get_db)):


    ### ensure token is being read and catched correctly ###
    token = request.cookies.get("access_token")

    print(token)

    if token:
        raise HTTPException(status_code=404, detail="Error - User already logged in")
    
    ##########################################################################################



    db_user = auth.get_user(db, name=User_Register.name)

    if db_user:
        raise HTTPException(status_code=404, detail="Error - Username already in use")
      
    hashed_password = security.get_password_hash(User_Register.password)
    
    # Pick a random user who has at least one entry in ranked_recommendations
    random_user = db.query(models.User)\
        .join(models.RankedRecommendation, models.RankedRecommendation.user_id == models.User.user_id)\
        .order_by(func.newid())\
        .first()

    if random_user:
        random_user_id = random_user.user_id
        #add check to ensure the ranodm user id is not alreayd existing insode of user_mpa if so get a new one
    else:
        #when no user id is found 
        #random_user_id = None
        #generating a random userID from the users table
        random_user = db.query(models.User).order_by(func.random()).first() #changed odels.users to model.User if
        random_user_id = random_user.user_id
        print("No users with recommendations found")

    db_user = models.user_map(
    user_id=random_user_id,
    name = User_Register.name,
    is_child = User_Register.is_child, 
    hashed_password=hashed_password)

    try:
        db.add(db_user)
        db.commit()
    except IntegrityError:
        db.rollback()
    db.refresh(db_user)

    return db_user




@router.post("/login", response_model=schemas.Token, summary="User Login")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
            username = payload.get("sub")
            if username:
                # Only raise if token is valid
                raise HTTPException(status_code=400, detail="User already logged in")
        except JWTError:
            # Invalid or expired token, allow login
            pass

    user = auth.get_user(db, form_data.username)

    if not user:
        print("USERNAME NOT FOUND")

    if not security.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Error - Incorrect login details")
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user.name}, expires_delta=access_token_expires)

    response = JSONResponse(content={"message": "Login successful"})
    response.delete_cookie("access_token")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False, 
        samesite="Lax", 
        max_age=3600, 
        path="/" 
    )
    return response


# import time

# @router.post("/login", response_model=schemas.Token, summary="User Login")
# async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

#     start_total = time.time()

#     t0 = time.time()
#     token = request.cookies.get("access_token")  
#     print(f"Cookie lookup: {(time.time() - t0)*1000:.3f} ms")
#     # O(1) — dictionary lookup in cookies

#     if token:
#         try:
#             t0 = time.time()
#             payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])  
#             print(f"JWT decode: {(time.time() - t0)*1000:.3f} ms")
#             # O(1) — small fixed-size token

#             t0 = time.time()
#             username = payload.get("sub")  
#             print(f"Payload get username: {(time.time() - t0)*1000:.3f} ms")
#             # O(1) — dictionary access

#             if username:
#                 raise HTTPException(status_code=400, detail="User already logged in")  
#                 # O(1)

#         except JWTError:
#             pass  # O(1)

#     t0 = time.time()
#     user = auth.get_user(db, form_data.username)  
#     print(f"DB lookup: {(time.time() - t0)*1000:.3f} ms")
#     # O(log n) with index

#     if not user:
#         print("USERNAME NOT FOUND")  # O(1)

#     t0 = time.time()
#     password_valid = security.pwd_context.verify(form_data.password, user.hashed_password)
#     print(f"Password verify: {(time.time() - t0)*1000:.3f} ms")
#     # O(1) — constant but intentionally slow (hashing)

#     if not password_valid:
#         raise HTTPException(status_code=404, detail="Error - Incorrect login details")  
#         # O(1)

#     t0 = time.time()
#     access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)  
#     print(f"Create timedelta: {(time.time() - t0)*1000:.3f} ms")
#     # O(1)

#     t0 = time.time()
#     access_token = security.create_access_token(
#         data={"sub": user.name}, 
#         expires_delta=access_token_expires
#     )  
#     print(f"Create token: {(time.time() - t0)*1000:.3f} ms")
#     # O(1)

#     t0 = time.time()
#     response = JSONResponse(content={"message": "Login successful"})  
#     print(f"Create response: {(time.time() - t0)*1000:.3f} ms")
#     # O(1)

#     t0 = time.time()
#     response.delete_cookie("access_token")  
#     print(f"Delete cookie: {(time.time() - t0)*1000:.3f} ms")
#     # O(1)

#     t0 = time.time()
#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#         httponly=True,
#         secure=False, 
#         samesite="Lax", 
#         max_age=3600, 
#         path="/" 
#     )  
#     print(f"Set cookie: {(time.time() - t0)*1000:.3f} ms")
#     # O(1)

#     print(f"Total time: {(time.time() - start_total)*1000:.3f} ms")

#     return response  
#     # O(1)

# #Simplified = o( log n)



    
@router.post("/logout", summary="User Logout")
async def user_delete_token():
    try:
        # Always create a fresh response
        response = JSONResponse(content={"message": "Logged out"})

        # Attempt to delete cookie safely
        response.delete_cookie(
            key="access_token",
            path="/",
            httponly=True,
            samesite="lax"
        )

        return response

    except Exception as e:
        # Log the error (important for debugging)
        print(f"Logout failed: {e}")

        # STILL return success to client (never fail)
        return JSONResponse(
            content={"message": "Logged out"},
            status_code=200
        )

@router.post("/get-recommendations", summary="Get user recommendations")
async def get_recommendations(current_user: models.user_map = Depends(auth.get_current_user), db: Session = Depends(get_db)):

    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    

    #print("current user_data id:", current_user.user_id)
    #print("Current user_data username is: ", current_user.name)

    try:
        recommendations = db.query(models.RankedRecommendation)\
            .filter(models.RankedRecommendation.user_id == current_user.user_id)\
            .all()

        if not recommendations:
            print(f"No recommendations found for user_id {current_user.user_id}")
            recommendations = []

    except Exception as e:
        print(f"Error fetching recommendations for user_id {current_user.user_id}: {e}")
        recommendations = []


    return recommendations


#we need to rmove the "un" logic from this, if its already liked and the user clicks the like again just rmeove the like
@router.post("/store-interaction", summary="Store or remove user interaction")
async def store_interactions(
    user_interaction: schemas.UserInteraction,
    request: Request,
    current_user: models.user_map = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
    ):

    #print("cookies:", request.cookies)
    #print(current_user.name)

    if not current_user:

        raise HTTPException(status_code=401, detail="Unauthorized")
    
    interaction_type = user_interaction.interaction_type.lower()
    content_id = user_interaction.content_id

    #ALLOWED INTERACTION TYPES - send one if these from frontend as str with relevant content id
    # renamed the interaction types removing the undo keyword
    interactions_types = ["like", "dislike", "share", "report", "comment",
                          "unlike", "undislike", "unshare", "unreport", "uncomment"]

    ### checking if interactions is valid ###
    if interaction_type not in interactions_types:
        raise HTTPException(status_code=400, detail="Invalid interactions")
    else:
        print("Interactions is OK! it is: ", interaction_type)

    ### CODE FOR IF UNDOING INTERACTION ## 
    if interaction_type.startswith("un"):

        #check what type of interaction the undo is for
        cleaned_type = interaction_type[2:] # remove "un"
        print(f"Removing the {cleaned_type}, for {content_id} ")

        #querying the db to see if this undo interactions currently exists
        existing_interaction = db.query(models.Interaction).filter(
            models.Interaction.user_id == current_user.user_id,
            models.Interaction.content_id == content_id,
            models.Interaction.interaction_type == cleaned_type
        ).first()

        if existing_interaction:

            db.delete(existing_interaction)
            db.commit()
            return(f"'{cleaned_type}' undone successfully")
        else:
            return(f"No Existing '{cleaned_type}' interaction found for content id: {content_id}")

    ### CODE FOR IF ADDING NEW INTERACTION, NOT UNDOING ###
    else:
        existing_content = db.query(models.RankedRecommendation).filter(
            models.RankedRecommendation.content_id == content_id,
        ).first()

        # DELETE the other interaction (like or dislike) enforce mutual exclusion
        if interaction_type == "like":
            db.query(models.Interaction).filter(
                models.Interaction.user_id == current_user.user_id,
                models.Interaction.content_id == content_id,
                models.Interaction.interaction_type == "dislike"
            ).delete()
        elif interaction_type == "dislike":
            db.query(models.Interaction).filter(
                models.Interaction.user_id == current_user.user_id,
                models.Interaction.content_id == content_id,
                models.Interaction.interaction_type == "like"
            ).delete()
        
        db.commit()

        if  existing_content:

            existing_interaction = db.query(models.Interaction).filter(
            models.Interaction.user_id == current_user.user_id,
            models.Interaction.content_id == content_id,
            models.Interaction.interaction_type == interaction_type
            ).first()

            if existing_interaction:
                return "interaction already exists"
            
            new_interaction = models.Interaction(
                user_id=current_user.user_id,
                content_id=content_id,
                interaction_type= interaction_type,
                interaction_date = datetime.now()
            )

            db.add(new_interaction)
            db.commit()

            return("interaction added successfully")
        else:
            return("content id doesnt exist")
        
        #the current code allows you to add interactions for new and undo types
        #it does not let you add duplicate interactions (line 198-205)
        #ince the current code do


        #questions for Qiqi
        #can a user like a post then dislike it do we keep the like interaction log or delete it
        #can a user like a post AND report it
        #we can store liekes and dislikes at the same time or do you want to rmeove the prevous clashing interaction? (similar to point 1)
    


#fix this route to user proper schema etc
@router.post("/update-preferences", summary="Update user preferences")
async def update_preferences(
        prefs: dict,
        current_user: models.user_map = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
    ):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    current_user.liked_cat = ",".join(prefs.get("categories", []))
    current_user.liked_subcat = ",".join(prefs.get("subcategories", []))

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Preferences updated"}


@router.get("/me", summary="Get current logged-in user")
async def get_current_user_route(current_user: models.user_map = Depends(auth.get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {
        "name": current_user.name, "user_id": current_user.user_id
    }

@router.get("/interactions", summary="Get all interactions of the current user")
async def get_user_interactions(current_user: models.user_map = Depends(auth.get_current_user),
                                db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    interactions = db.query(models.Interaction).filter(
        models.Interaction.user_id == current_user.user_id
    ).all()

    return interactions

#route for tracking - open story click