from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi_utils.tasks import repeat_every
from random import randint
import uuid
import time
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas, utils
from .database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

tags_metadata = [
    {"name": "Challenges", "description": "Endpoints for creating and retrieving challenges"},
    {"name": "Submissions", "description": "Endpoints for creating and retrieving submissions"},
    {"name": "Statistics", "description": "Endpoints for retrieving computed statistics"}
]

app = FastAPI(title= "ShiftAdd", openapi_tags=tags_metadata)
# templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
@repeat_every(seconds=30, logger=True)
def generate_new_challenge(db: Session = next(get_db())):
    ## Use repeated tasks from server startup to continuously generate a random new challenge every 30 seconds
    current_challenge_id = uuid.uuid4().hex
    a=randint(0,100) 
    b=randint(0,100)
    correct_answer= a + b
    new_challenge = schemas.ChallengeCreate(id=current_challenge_id ,a=a, b=b, time_started=round(time.time(), 2), correct_answer=correct_answer)
    create_new_challenge(new_challenge, db)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    ## Return template
    current_challenge = get_current_challenge(db)

    return current_challenge
    # return templates.TemplateResponse(".templates/challenge.html", challenge.dict())


@app.post("/challenge", response_model=schemas.Challenge, tags=["Challenges"])
def create_new_challenge(challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    ## Save challenge to db ##
    return crud.create_challenge(db, challenge=challenge)

@app.get("/challenge/{challenge_id}", response_model=schemas.Challenge, tags=["Challenges"])
def get_challenge(challenge_id: str, db: Session = Depends(get_db)):
    ## Get challenge by id from db
    db_challenge = crud.get_challenge(db=db, challenge_id=challenge_id)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return db_challenge 

@app.get("/current-challenge", response_model=schemas.Challenge, tags=["Challenges"])
def get_current_challenge(db: Session = Depends(get_db)):
    ## Get current challenge from db
    db_challenge = crud.get_newest_challenge(db)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return db_challenge


@app.post("/submit/{challenge_id}/{answer}", response_model=schemas.Submission, tags=["Submissions"])
def submit_challenge(challenge_id: str, answer: int, request: Request, db: Session = Depends(get_db)):
    time_now = round(time.time(), 2)
    current_challenge = crud.get_newest_challenge(db)
    if challenge_id != current_challenge.id:
        raise HTTPException(status_code=400, detail="Submission is not for current challenge")

    player_ip = request.client.host
    submission_id = uuid.uuid1().hex

    score = utils.get_score(answer, current_challenge.correct_answer, time_now, current_challenge.time_started)

    submission = schemas.SubmissionCreate(id=submission_id,challenge_id=challenge_id,player_ip=player_ip,answer=answer,time_submitted=time_now,score=score)
    return crud.create_submission(db,submission=submission)

@app.get("/submissions/player/{player_ip}", tags=["Submissions"])
def get_player_submissions(player_ip:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_player_submissions(db, player_ip)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for user not found")
    return db_submissions

@app.get("/submissions/challenge/{challenge_id}", tags=["Submissions"])
def get_challenge_submissions(challenge_id:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_challenge_submissions(db, challenge_id)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for challenge not found")
    return db_submissions

@app.get("/player/mean-score/{player_ip}", tags=["Statistics"])
def get_player_mean_score(player_ip:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_player_submissions(db, player_ip)
    if db_submissions is None:
        raise HTTPException(status_code=404, detail="Submission for user not found")
    return utils.get_mean_score(db_submissions)

@app.get("/challenge/mean-score/{challenge_id}", response_class=float, tags=["Statistics"])
def get_challenge_mean_score(challenge_id:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_challenge_submissions(db, challenge_id)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for challenge not found")
    return utils.get_mean_score(db_submissions)

@app.get("/player/challenges-submitted/{player_ip}", response_class=int, tags=["Statistics"])
def get_number_of_challenges_submitted(player_ip:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_player_submissions(db, player_ip)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for user not found")
    return len(db_submissions)

@app.get("/player/longest-streak/{player_ip}", response_class=int, tags=["Statistics"])
def get_longest_streak(player_ip:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_player_submissions(db, player_ip)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for user not found")
    return utils.get_longest_streak(db_submissions)
