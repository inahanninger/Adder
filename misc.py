# class Challenge():
#     def __init__(self, id: str, a: int, b: int, time_started: float, correct_answer: int):
#         self.id = id
#         self.a = a
#         self.b = b
#         self.time_started = time_started
#         self.correct_answer = correct_answer
    
#     __pydantic_model__ = create_model("Challenge", id=(str, ...), a=(int, ...), b=(int, ...), time_started=(float, ...), correct_answer=(int, ...))


# class Player():
#     def __init__(self, player_ip:str, score_log):
#         self.player_ip = player_ip
#         self.score_log = score_log
    
#     def add_submission(self, score):
#         self.score_log.append(score)
    
#     def get_mean_score(self):
#         sum = 0
#         for submission in self.score_log:
#             sum += submission
#         return sum / len(self.score_log)
    
#     __pydantic_model__ = create_model("Player", player_ip=(str,...), score_log=(Any,...))

#     class Submission():
#     def __init__(self, challenge: Challenge, player: Player, answer: str, time_submitted: float, score: timedelta):
#         self.challenge = challenge 
#         self.player = player
#         self.answer = answer
#         self.time_submitted = time_submitted
#         self.score = score

#     # def get_score(self):
#     #     if self.answer == self.challenge.correct_answer:
#     #         return self.time_submitted - self.challenge.time_started
#     #     else:
#     #         return -1

#     # score = property(get_score)

#     __pydantic_model__ = create_model("Submission", challenge=(Challenge,...), player=(Player,...), answer=(str,...), time_submitted=(float,...), score=(timedelta,...))

# class Challenge_Response(BaseModel):
#     challenge: Challenge

# class Submission_Response(BaseModel):
#     submission: Submission

# class Player_Response(BaseModel):
#     player: Player


# BaseConfig.arbitrary_types_allowed = True # Allow arbitrary classes in pydantic

# # Initialize in-memory databases
# db_challenge = Base('challenges', save_to_file=False)
# db_challenge.create('id', 'a', 'b', 'time_started', 'correct_answer')
# db_submissions = Base('submissions', save_to_file=False)
# db_submissions.create('challenge_id', 'player_ip', 'score')

