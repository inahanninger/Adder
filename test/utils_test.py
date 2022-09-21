import pytest

from sql_app.utils import *
from sql_app.models import *

test_submissions = [
  Submission(**{
    "answer": 22,
    "id": "431a7441245b11ed892d201e88d3a111",
    "score": -1,
    "time_submitted": 1661420990,
    "challenge_id": "15d2ecd6b3d14aec80544ef9d5b8f2ef",
    "player_ip": "127.0.0.1"
  }),
  Submission(**{
    "answer": 47,
    "id": "b766da99245c11ed9e48201e88d3a111",
    "score": 12,
    "time_submitted": 1661421615,
    "challenge_id": "6d57f424b9644bbcb56b9e91cc6158af",
    "player_ip": "127.0.0.1"
  }),
  Submission(**{
    "answer": 96,
    "id": "afeabebc245d11ed913c201e88d3a111",
    "score": 10,
    "time_submitted": 1661422032,
    "challenge_id": "e6f6ea13af8d4d1b9dc8a0550f986bae",
    "player_ip": "127.0.0.1"
  })
]

@pytest.mark.parametrize("answer, correct_answer, time_submitted, time_started, expected_output", [
    (3, 3, 1661416425, 1661416419, 24), ## Correct answer and within time
    (3, 5, 1661416425, 1661416419, -1), ## Wrong answer but within time limit
    (5, 5, 1661416450, 1661416419, -1), ## Correct answer but past time limit
])
def test_get_score(answer, correct_answer, time_submitted, time_started, expected_output):
    score = get_score(answer, correct_answer, time_submitted, time_started)
    assert score == expected_output

def test_get_mean_score():
    mean_score = get_mean_score(test_submissions)
    assert mean_score == 7

def test_get_longest_streak():
    streak = get_longest_streak(test_submissions)
    assert streak == 2