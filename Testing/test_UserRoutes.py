import pytest
from fastapi.testclient import TestClient
from main import app

from backend.api_backend.Database.db import get_db
from backend.api_backend.Database.db import Base
from sqlalchemy import create_engine, StaticPool, inspect
from sqlalchemy.orm import sessionmaker

from backend.api_backend.Database.models import *
from backend.api_backend.Authentication.auth import get_current_user

from backend.api_backend import schemas
from backend.api_backend.Database import models

from sqlalchemy.sql import func, text
import logging
from backend.api_backend.Authentication import security, auth

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(funcName)s:%(message)s")
logger = logging.getLogger(__name__)

#python -m pytest -s


#intialise in-memory sqlite database
DATABASE_URL = "sqlite:///:memory:"

#connect the sqlite db cusing database url, SQLAlchemy parses the URL, recognizes sqlite, and then uses the appropriate SQLite driver to connect and create the engine.
#check_same_thread allows muultiple threads and poolclass is share the same single in-memory database connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)


#initialising a new session for testing only - this creates a separate session factory for tests.
#so evertime we call override_get_db in a test we call TestingSessionLocal() to initiate a session
#bind=engine, binding this session to the sqlite db
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Testclient is a built-in fastapi function to recreate all current API endpoints without using https
#"You can use the TestClient class to test FastAPI applications without creating an actual HTTP and socket connection, just communicating directly with the FastAPI code."
#the client is just a tool to send requests into the app.
client = TestClient(app)

#same db connection code as our prod however we replace the actual prod db session with the local one
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

#overriding the fastapis app get_db to the new override db function
#"Whenever FastAPI sees get_db, replace it with override_get_db instead."
#so we modify the actual app and not just the client
#so Whenever THIS app sees get_db, replace it.
app.dependency_overrides[get_db] = override_get_db


#fixture to create a fresh db on test startup and then delete all tables once finished
#1. create_all() - builds all tables in the test DB
#2 test runs
#3 drop_all() > removes all tables after the test
#In-memory SQLite does NOT automatically reset between tests. so we need to drop_all()
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

#add fixture to reset app dependencies?


def test_sqlite_proof():

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "interactions" in tables
    assert "ranked_recommendations" in tables
    assert "user_map" in tables
    assert "users" in tables
    assert "sqlite" in str(engine.url)

    for table in tables:
        print(f"TABLE: {table}")

        columns = inspector.get_columns(table)
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")


def test_register_route_correct_details(monkeypatch: pytest.MonkeyPatch):
    #patching the newid func sice we can do that in sqlite
    monkeypatch.setattr(func, "newid", lambda: func.random())

    db = TestingSessionLocal()

    ################################ generating a ranked_recommendation user start #################################
    #to cover the need for random_user inside register route we wil just 
    # generate a fake user in ranked_recs
    ranked_recs_payload = {     
        "user_id": "test_user_1",
        "content_id": "content_123",
        "category": "technology",
        "sub_category": "ai",
        "title": "How AI is changing recommendations",
        "abstract": "This article explains how recommendation systems use AI to improve personalization."
    }

    saved_ranked_recs_user = models.RankedRecommendation(**ranked_recs_payload)

    db.add(saved_ranked_recs_user)
    db.commit()
    db.refresh(saved_ranked_recs_user)

    ranked_recs_query = db.query(models.RankedRecommendation).filter_by(user_id=saved_ranked_recs_user.user_id).first()

    assert ranked_recs_query.content_id == "content_123"
    assert ranked_recs_query.category == "technology"
    ################################ generating a ranked_recommendation user end #################################

    ################################ generating a user in models.user start #################################
    user_seed = models.User(
        user_id="test_user_1",
        name="seed_user",
        is_child=False
    )

    db.add(user_seed)
    db.commit()
    ################################ generating a user in models.user end #################################
 
    ################################ registering the user - test starts here ################################
    user_payload = {
        "name": "testuser",
        "password": "securepassword123",
        "is_child": False
    }
    
    response = client.post("/user/register", json=user_payload)

    assert response.status_code == 200
    saved_user = db.query(models.user_map).filter_by(name=user_payload["name"]).first()

    assert saved_user.name == "testuser"
    assert saved_user.is_child is False
    #add assert for password check (dehash it)
    ################################ registering the user - test ends here ################################



def test_get_recommendations_route_no_existing_recommendations(monkeypatch: pytest.MonkeyPatch):
    #thiswill test the get_recommendations route when the suer has no existing recommendations
    #we need to make sure it returns nan sfely and no crash
    

    #steps
    #1 patch get db and patch get_current_user (create fake user)
    #2query rankedrecs model with current user id
    # if no recs test return
    #expected error should be caught as in the actual route

    db = TestingSessionLocal()

    # adding fake user to meet prereqs for this route  start #
    fake_user = {
        "sql_id": 1,
        "user_id": "id here 123",
        "hashed_password": "sss",
        "name": "user_1",
        "is_child": True
    }

    saved_user = models.user_map(**fake_user)

    db.add(saved_user)
    db.commit()
    db.refresh(saved_user)

    # adding fake user to meet prereqs for this route end #

    #overwriting the need to check for a logged in user (skipping this check using dependncy override)
    app.dependency_overrides[auth.get_current_user] = lambda: saved_user
    
    response = client.post("/user/get-recommendations")

    data = response.json()

    print(data)

    assert response.status_code == 200 #checking for a sucessful response
    assert isinstance(data, list) #checking if the data isa list as expected
    assert len(data) == 0 #since the user is a fake user the retuneed list should have no content (so the length should be == 0)
    








#this route is working properly as the len data is 0 menaing nothing in he list and the ata is a list fo recs
#we need to fix the atual route status codes so we can effectively tests the status codes, if there is no user founded retunr status code x

#def test_get_recommendations_route_yes_existing_recommendations(monkeypatch: pytest.MonkeyPatch):






















#def test_pytest_add_user_to_db():
    #this test will register a new user into the database to test if pytest works
    #1 setup fake user
    #2 connect to db ans register user
    #3 see if user is stored in the database 

    # db = TestingSessionLocal()

    # user_details = schemas.UserRegister(
    #     name="testuser",
    #     password="securepassword123",
    #     is_child=False,
    # )

    
    # #for now adding plain password instead of hasing it for testing purposes
    # db_user = models.user_map(
    #     name=user_details.name,
    #     hashed_password=user_details.password,
    #     is_child=user_details.is_child
    # )

    
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)

    # saved_user = db.query(models.user_map).filter_by(name=user_details.name).first()

    # assert saved_user.name == "testuser"
    # assert saved_user.hashed_password == "securepassword123"
    # assert saved_user.is_child is False


#5 tests to write
#register user correct details
#register user with incorrect details
#login with valid details
#login with invalid details
#receive recommendations

#def test_login_valid_details():
    #this test will login a user with valid details
    #1 connect to db that already has registered user from above func
    #2 call login endpoint with those previously registered details
    #3 check if response is 200
    #4 check for access token ?


   #we can either have 2 results
   #1 raise HTTPException(status_code=404, detail="Error - Incorrect login details")
   #2 statuscode 200 sucess Login successful
   
   #start by checking if the username is found
   #if username is found then check if password is correct by comparing input pass:stored pass

