from cgitb import text
from starlette.testclient import TestClient
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql_app.main import app, get_db
from sql_app.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_new_challenge():
    response = client.post(
        "/challenges",
        json = {
                "id": "983b88f66cb946a198bc9e527241a749",
                "a": 2,
                "b": 3,
                "time_started": 1661414993.85,
                "correct_answer": 5
                }
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == "983b88f66cb946a198bc9e527241a749"
    assert data["time_started"] == 1661414993.85
    assert data["correct_answer"] == 5
    challenge_id = data["id"]

    ## test that we can retrieve this newly created resource by id
    response = client.get(f"/challenges/{challenge_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == challenge_id
    assert data["time_started"] == 1661414993.85
    assert data["correct_answer"] == 5

    ## Now test if, after adding another one, "/current-challenge" will return the newest one
    ## First post a newer response

    newer_response = client.post(
        "/challenges",
        json = {
                "id": "983b88f66cb946a198bc9e527241a750",
                "a": 7,
                "b": 6,
                "time_started": 1661415123.85,
                "correct_answer": 13
                }
    )
    assert newer_response.status_code == 201, newer_response.text
    
    ## Then check it returns the newer one using "/current-challenge"
    response = client.get("/challenges/current-challenge")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == "983b88f66cb946a198bc9e527241a750"
    assert data["time_started"] == 1661415123.85
    assert data["correct_answer"] == 13


def test_submit_challenge():
    current_challenge = client.get("/challenges/current-challenge")
    current_challenge_data = current_challenge.json()
    challenge_id = current_challenge_data["id"]
    answer = current_challenge_data["correct_answer"]
    response = client.post(f"/submissions/{challenge_id}/{answer}")

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"]
    assert data["challenge_id"] == challenge_id
    assert data["player_ip"]
    assert data["time_submitted"]
    assert data["score"] == -1

def test_submit_challenge_not_current():
    challenge_id = "983b88f66cb946a198bc9e527241a743"
    answer = 2
    response = client.post(f"/submissions/{challenge_id}/{answer}")
    assert response.status_code == 400


