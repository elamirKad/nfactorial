import numpy as np
from bot.game_functions import *

def random_move(current_state):
    index = np.random.randint(4)
    return ["up", "down", "left", "right"][index]

def playthrough(gamestate, num_tries, max_depth):
    score = 0
    for i in range(num_tries):
        newstate = gamestate
        depth = 0
        while game_status(get_matrix(newstate)) == "not over" and depth < max_depth:
            best_move = random_move(newstate)
            best_move = game_logic[best_move]
            newstate, _ = best_move(newstate)

            depth += 1
        score += newstate[1]

    return score / num_tries

def predict_next_move(current_state, num_tries=100, max_depth=25, initial_tries=20):
    indextomove = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}
    movetoindex = {'up': 0, 'down': 1, 'left': 2, 'right': 3}
    action_score = np.array([0, 0, 0, 0])
    action_tries = np.array([0, 0, 0, 0])
    exploration_tries, exploration_score = 0, 0

    for move in ['up', 'down', 'left', 'right']:
        _, valid = game_logic[move](current_state)
        if not valid:
            action_tries[movetoindex[move]] = initial_tries
            action_score[movetoindex[move]] = -1000000
            continue

        for tries in range(initial_tries):
            montecarlo_state, _ = game_logic[move](current_state)
            montecarlo_score = playthrough(montecarlo_state, 1, max_depth)
            maxindex = movetoindex[move]
            action_tries[maxindex] += 1
            action_score[maxindex] += montecarlo_score
            exploration_tries += 1
            exploration_score += montecarlo_score

    c = exploration_score / exploration_tries

    for totaltries in range(num_tries):
        action_heuristic = action_score / action_tries + c * np.sqrt(np.log(totaltries + 1) / action_tries)
        maxindex = np.argmax(action_heuristic)
        move = indextomove[maxindex]
        montecarlo_state, _ = game_logic[move](current_state)
        montecarlo_score = playthrough(montecarlo_state, 1, max_depth)
        action_tries[maxindex] += 1
        action_score[maxindex] += montecarlo_score

    bestmoveindex = np.argmax(action_score / action_tries)
    bestmove = indextomove[bestmoveindex]

    return bestmove

# state = make_new_game(4)
# while True:
#     print(state)
#     bestmove = predict_next_move(state)
#     state, _ = game_logic[bestmove](state)