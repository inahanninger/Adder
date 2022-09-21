from fastapi import FastAPI, Request, status, Form, Depends, HTTPException
from fastapi_utils.tasks import repeat_every
from random import randint
import uuid
import time
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from . import crud, models, schemas, utils
from .database import SessionLocal, engine
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

models.Base.metadata.create_all(bind=engine)

tags_metadata = [
    {"name": "Challenges", "description": "Endpoints for creating and retrieving challenges"},
    {"name": "Submissions", "description": "Endpoints for creating and retrieving submissions"},
    {"name": "Statistics", "description": "Endpoints for retrieving computed statistics"}
]

app = FastAPI(title= "ShiftAdd", openapi_tags=tags_metadata)
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
app.mount("/static", StaticFiles(directory=str(Path(BASE_DIR, 'static'))), name="static")

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

@app.get("/", response_class = HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    ## Return template
    player_ip = request.client.host
    page_data = get_current_challenge(db).__dict__
    page_data["request"] = request
    page_data["challenges_submitted"] = get_number_of_challenges_submitted(player_ip,db)
    page_data["mean_score"] = get_player_mean_score(player_ip, db)
    page_data["longest_streak"] = get_longest_streak(player_ip, db)
    latest_submission = get_last_submission(player_ip, db)
    page_data["score"] = latest_submission.score
    page_data["answer"] = latest_submission.answer

    # return current_challenge
    return templates.TemplateResponse("index.html", page_data)

@app.post("/", response_class = HTMLResponse)
async def root_post(request: Request, challenge_id: str = Form(...), answer: str = Form(...), db: Session = Depends(get_db)):
    ## Return template
    submit_challenge(challenge_id, int(answer), request, db)

    return RedirectResponse(url=app.url_path_for("root"), status_code=status.HTTP_303_SEE_OTHER)

@app.post("/challenges", response_model=schemas.Challenge, tags=["Challenges"])
def create_new_challenge(challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    ## Save challenge to db ##
    return crud.create_challenge(db, challenge=challenge)

@app.get("/challenges", tags=["Challenges"])
def get_all_challenges(db: Session = Depends(get_db)):
    ## Get 100 most recent challenges
    db_challenges = crud.get_recent_challenges(db=db)
    if db_challenges is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return db_challenges

@app.get("/current-challenge", response_model=schemas.Challenge, tags=["Challenges"])
def get_current_challenge(db: Session = Depends(get_db)):
    ## Get current challenge from db
    db_challenge = crud.get_newest_challenge(db)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return db_challenge 

@app.get("/challenges/{challenge_id}", response_model=schemas.Challenge, tags=["Challenges"])
def get_challenge(challenge_id: str, db: Session = Depends(get_db)):
    ## Get challenge by id from db
    db_challenge = crud.get_challenge(db=db, challenge_id=challenge_id)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return db_challenge 


@app.post("/submissions/{challenge_id}/{answer}", response_model=schemas.Submission, tags=["Submissions"], status_code=201)
def submit_challenge(challenge_id: str, answer: int, request: Request, db: Session = Depends(get_db)):
    ## Create a submission based on the challenge_id and answer inputted
    ## Only allow submissions that are for the current challenge
    time_now = round(time.time(), 2)
    current_challenge = crud.get_newest_challenge(db)
    if challenge_id != current_challenge.id:
        raise HTTPException(status_code=400, detail="Submission is not for current challenge")

    player_ip = request.client.host
    last_submission = get_last_submission(player_ip, db)
    if (last_submission != None and last_submission.challenge_id == challenge_id):
        raise HTTPException(status_code=400, detail="Player has already submitted for this challenge")
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

@app.get("/submissions/player/{player_ip}/latest", tags=["Submissions"])
def get_last_submission(player_ip:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_player_latest_submission(db, player_ip)
    return db_submissions

@app.get("/submissions/challenge/{challenge_id}", tags=["Submissions"])
def get_challenge_submissions(challenge_id:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_challenge_submissions(db, challenge_id)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for challenge not found")
    return db_submissions

@app.get("/submissions/player/{player_ip}/mean-score", tags=["Statistics"])
def get_player_mean_score(player_ip:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_player_submissions(db, player_ip)
    if db_submissions is None:
        raise HTTPException(status_code=404, detail="Submission for user not found")
    return utils.get_mean_score(db_submissions)

@app.get("/challenges/{challenge_id}/mean-score", tags=["Statistics"])
def get_challenge_mean_score(challenge_id:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_challenge_submissions(db, challenge_id)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for challenge not found")
    return utils.get_mean_score(db_submissions)

@app.get("/submissions/player/{player_ip}/challenges-submitted", tags=["Statistics"])
def get_number_of_challenges_submitted(player_ip:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_player_submissions(db, player_ip)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for user not found")
    return len(db_submissions)

@app.get("/submissions/player/{player_ip}/longest-streak", tags=["Statistics"])
def get_longest_streak(player_ip:str, db: Session = Depends(get_db)):
    db_submissions = crud.get_player_submissions(db, player_ip)
    if (db_submissions is None or len(db_submissions)==0):
        raise HTTPException(status_code=404, detail="Submissions for user not found")
    return utils.get_longest_streak(db_submissions)
