from GnuGo import *
import json
import random
import time
from copy import deepcopy

def monte_carlo(gnugo, moves, nbsamples = 100):
    list_of_moves = [] # moves to backtrack
    epochs = 0 # Number of played games
    toret = []
    black_wins = 0
    white_wins = 0
    black_points = 0
    white_points = 0
    while epochs < nbsamples:
        nbmoves = 0
        while True :
            m = moves.get_randomized_best()
            r = moves.playthis(m)
            if r == "RES":
                return None
            nbmoves += 1
            list_of_moves.append(m)
            if nbmoves > 1 and list_of_moves[-1] == "PASS" and list_of_moves[-2] == "PASS":
                break
        score = gnugo.finalScore()
        toret.append(score)
        if score[0] == "W":
            white_wins += 1
            if score[1] == "+":
                white_points += float(score[2:])
        elif score[0] == "B":
            black_wins += 1
            if score[1] == "+":
                black_points += float(score[2:])
        (ok, res) = gnugo.query("gg-undo " + str(nbmoves))
        list_of_moves = []
        epochs += 1
    if(moves.player() == "black") :
        return format(black_wins/float(nbsamples),'.2f')
    else :
        return format(white_wins/float(nbsamples),'.2f')

_dic = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'J':8}

def flatten(s):
    return (_dic[s[0]], int(s[1]) - 1)

def doit():
    gnugo = GnuGo(9)
    moves = gnugo.Moves(gnugo)
    list_of_moves, blackstones, whitestones = start(gnugo, moves)
    (_, legal) = gnugo.query("all_legal " + moves.player())
    proba_matrix = [[0 for i in range(9)] for j in range(9)]
    legal = legal.split(' ')[1:]
    nb_rollout = (110 - min(100, len(legal) * 2)) // 2 
    print( "\t0" + "/" + str(len(legal)), end="\r")
    for i, m in enumerate(legal):
        moves.playthis(m)
        proba_win = monte_carlo(gnugo, moves, nb_rollout)
        (ok, res) = gnugo.query("gg-undo 1")
        flat_move = flatten(m)
        proba_matrix[flat_move[0]][flat_move[1]] = proba_win
        print("\t" + str(i + 1) + "/" + str(len(legal)), end="\r")
    moves.playthis("PASS")
    proba_win_pass = monte_carlo(gnugo, moves, nb_rollout)
    (ok, res) = gnugo.query("gg-undo 1")
    summary = {"depth": len(list_of_moves), "list_of_moves": list_of_moves,
                "black_stones":blackstones, "white_stones": whitestones,
                "rollouts":nb_rollout,
                "winning_proba" : proba_matrix, "proba_win_pass": proba_win_pass,
                "black_wins":0, "black_points": 0,
                "white_wins":0, "white_points":0, "player": moves.player()}
    return summary

def start(gnugo, moves):
    n = random.randrange(40, 50)
    list_of_moves = []
    blackstones = []
    whitestones = []
    for i in range(n):
        m = moves.get_randomized_best()
        moves.playthis(m)
        list_of_moves.append(m);
        if(i%2==0) :
            blackstones.append(m)
        if(i%2==1) :
            whitestones.append(m)
    return list_of_moves, blackstones, whitestones


t1 = time.time()

for i in range(100):
    sum = doit()
    print(str(i) + "/" + str(100))
    with open('data.json', 'a') as outfile:
        outfile.write(",")
        json.dump(sum, outfile)

print("Temps pris : " + str(time.time() - t1))
