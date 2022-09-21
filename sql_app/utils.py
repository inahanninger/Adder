

def get_score(answer, correct_answer, time_submitted, time_started):
    time_to_answer = time_submitted - time_started
    if answer == correct_answer and time_to_answer < 30:
        return round(30 - time_to_answer, 2)
    else:
        return -1

def get_mean_score(submissions):
    score_list = [i.score for i in submissions]
    sum = 0
    for submission in score_list:
        sum += submission
    mean_score = sum / len(score_list)
    return round(mean_score, 2)

def get_longest_streak(submissions):
    streaks = []
    current_streak = 0
    for submission in submissions:
        if submission.score != -1:
            current_streak += 1
        else:
            streaks.append(current_streak)
            current_streak = 0
    streaks.append(current_streak)
    return max(streaks)

