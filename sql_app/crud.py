from sqlalchemy.orm import Session

from . import models, schemas


def get_challenge(db: Session, challenge_id: str):
    return db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()

def get_newest_challenge(db: Session):
    return db.query(models.Challenge).order_by(models.Challenge.time_started.desc()).first()

def get_recent_challenges(db: Session):
    return db.query(models.Challenge).order_by(models.Challenge.time_started.desc()).limit(100).all()

def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(**challenge.dict())
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def create_submission(db: Session, submission: schemas.SubmissionCreate):
    db_submissions = models.Submission(**submission.dict())
    db.add(db_submissions)
    db.commit()
    db.refresh(db_submissions)
    return db_submissions

def get_player_submissions(db: Session, player_ip:str, skip: int=0, limit: int=100):
    return db.query(models.Submission).filter(models.Submission.player_ip == player_ip).offset(skip).limit(limit).all()

def get_challenge_submissions(db: Session, challenge_id: str, skip: int=0, limit: int=100):
    return db.query(models.Submission).filter(models.Submission.challenge_id == challenge_id).offset(skip).limit(limit).all()

def get_player_latest_submission(db: Session, player_ip:str):
    return db.query(models.Submission).filter(models.Submission.player_ip == player_ip).order_by(models.Submission.time_submitted.desc()).first()