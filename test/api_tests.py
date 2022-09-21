from cgitb import text
import time
import os
from starlette.testclient import TestClient
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql_app.main import app, get_db
from sql_app.database import Base

if os.path.exists("./test.db"):
    os.remove("./test.db")

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
    assert response.status_code == 200, response.text
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
    assert newer_response.status_code == 200, newer_response.text
    
    ## Then check it returns the newer one using "/current-challenge"
    response = client.get("/current-challenge")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == "983b88f66cb946a198bc9e527241a750"
    assert data["time_started"] == 1661415123.85
    assert data["correct_answer"] == 13


def test_submit_challenge():
    current_challenge = client.get("/current-challenge")
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

def test_get_player_submissions():
    ## Add another challenge and get the player to submit it correctly
    time_now = round(time.time(), 2)
    response = client.post(
        "/challenges",
        json = {
                "id": "fbdbeafc72df4cf39ffa0d7d5d39ea87",
                "a": 57,
                "b": 52,
                "time_started": time_now,
                "correct_answer": 109
                }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    challenge_id = data["id"]
    answer = data["correct_answer"]

    submission_response = client.post(f"/submissions/{challenge_id}/{answer}")
    assert submission_response.status_code == 201

    ## Now test that player submissions are returned successfully
    player_ip = "testclient"
    player_response = client.get(f"/submissions/player/{player_ip}")
    assert player_response.status_code == 200, player_response.text
    player_data = player_response.json()
    assert len(player_data) == 2

    ## Test that /challenges-submitted endpoint returns successfully too
    player_ip = "testclient"
    player_response = client.get(f"/submissions/player/{player_ip}/challenges-submitted")
    assert player_response.status_code == 200, player_response.text
    player_data = player_response.json()
    assert player_data == 2

def test_get_player_mean_score():
    player_ip = "testclient"
    player_response = client.get(f"/submissions/player/{player_ip}/mean-score")
    assert player_response.status_code == 200, player_response.text
    player_data = player_response.json()
    assert player_data == 14.49

def test_longest_streak():
    player_ip = "testclient"
    player_response = client.get(f"/submissions/player/{player_ip}/longest-streak")
    assert player_response.status_code == 200, player_response.text
    player_data = player_response.json()
    assert player_data == 1

def test_get_all_challenges():
    response = client.get("/challenges")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 3

def test_get_challenge_mean_score():
    challenge_id = "fbdbeafc72df4cf39ffa0d7d5d39ea87"
    response = client.get(f"/challenges/{challenge_id}/mean-score")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == 29.98
