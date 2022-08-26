from enum import unique
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(String, primary_key=True, index=True)
    a = Column(Integer)
    b = Column(Integer)
    time_started = Column(Float, index= True)
    correct_answer = Column(Integer)

    # submissions = relationship("Submission", back_populates="game")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True)
    challenge_id = Column(String)
    player_ip = Column(String)
    answer = Column(Integer)
    time_submitted = Column(Float, index= True)
    score = Column(Float)

    # game = relationship("Challenge", back_populates= "submissions")