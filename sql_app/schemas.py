from pydantic import BaseModel
from typing import List

from sql_app.models import Submission

class SubmissionBase(BaseModel):
    id: str
    challenge_id: str
    player_ip: str
    answer: int
    time_submitted: float
    score: float

class SubmissionCreate(SubmissionBase):
    pass

class Submission(SubmissionBase):
    # id: int
    class Config:
        orm_mode = True

class ChallengeBase(BaseModel):
    id: str
    a: int
    b: int
    time_started: float
    correct_answer: int

class ChallengeCreate(ChallengeBase):
    pass

class Challenge(ChallengeBase):
    # id: int
    # submissions: List[Submission] = []
    class Config:
        orm_mode = True