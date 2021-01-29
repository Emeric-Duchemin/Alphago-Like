import MCTS
from training_model import *
import json
import random
import time
from collecting_game import *
import numpy as np
from copy import deepcopy
import os
import copy


def collecting_data_loop() :
    with open('data.json','r') as file :
        data = json.load(file)
    data = data[1:]
    stri = " "
    model_champion1 = "model"
    for i in range(100):
        sum = doit(model_champion1,model_champion1)
        stri += sum + ","
    with open('data_test.json', 'a') as outfile:
        #outfile.write(",")
        json.dump(data,',',sum)


def monte_carlo(game, game_rem, moves, nbsamples = 100):
    list_of_moves = [] # moves to backtrack
    epochs = 0 # Number of played games
    toret = []
    black_wins = 0
    white_wins = 0
    black_points = 0
    white_points = 0
    copy_game(game_rem,game)
    while epochs < nbsamples:
        nbmoves = 0
        while True :
            r = game.play_randomized_best()
            #r = moves.playthis(m)
            nbmoves += 1
            #list_of_moves.append(m)
            if nbmoves > 1 and game.list_of_moves[-1] == "PASS" and game.list_of_moves[-2] == "PASS":
                break
        score = game.result()
        if score[0] == "W":
            white_wins += 1
            if score[1] == "+":
                white_points += float(score[2:])
        elif score[0] == "B":
            black_wins += 1
            if score[1] == "+":
                black_points += float(score[2:])
        list_of_moves = []
        epochs += 1
        copy_game(game,game_rem)
    if(game.nextPlayer == 2) : # Si le prochain player est white
        return format(black_wins/float(nbsamples),'.2f')
    else :
        return format(white_wins/float(nbsamples),'.2f')

_dic = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'J':8}

def flatten(s):
    return (_dic[s[0]], int(s[1]) - 1)

def doit(model_champion1, model_champion2):
    game = Game_RL(model_champion1, model_champion2)
    game_rem = Game_RL(model_champion1, model_champion2)
    #moves = gnugo.Moves(gnugo)
    game = start(game)
    legal = game.b.legal_moves()
    #(_, legal) = gnugo.query("all_legal " + moves.player())
    proba_matrix = [[0 for i in range(9)] for j in range(9)]
    #legal = legal.split(' ')[1:]
    nb_rollout = (110 - min(100, len(legal) * 2)) // 2
    #print( "\t0" + "/" + str(len(legal)), end="\r")
    copy_game(game_rem,game)
    for m in legal :
        game.play_this(m)
        proba_win = monte_carlo(game, game_rem,game.list_of_moves, nb_rollout)
        copy_game(game,game_rem)
        flat_move = flatten(m)
        proba_matrix[flat_move[0]][flat_move[1]] = proba_win
        #print("\t" + str(i + 1) + "/" + str(len(legal)), end="\r")
    game.play_this("PASS")
    copy_game(game,game_rem)
    proba_win_pass = monte_carlo(game, game_rem, game.list_of_moves, nb_rollout)
    summary = {"depth": len(list_of_moves), "list_of_moves": list_of_moves,
                "black_stones":blackstones, "white_stones": whitestones,
                "rollouts":nb_rollout,
                "winning_proba" : proba_matrix, "proba_win_pass": proba_win_pass,
                "black_wins":0, "black_points": 0,
                "white_wins":0, "white_points":0, "player": moves.player()}
    return summary

def copy_game(game1,game2) :
    game1.b = copy.deepcopy(game2.b)
    game1.nextplayercolor = game2.nextplayercolor
    game1.nbmoves = game2.nbmoves
    game1.list_moves_colors = copy.deepcopy(game2.list_moves_colors)
    game1.list_of_moves = copy.deepcopy(game2.list_of_moves)
    #game1.player = copy.deepcopy(game2.player)

def start(game):
    n = random.randrange(40, 50)
    list_of_moves = []
    blackstones = []
    whitestones = []
    for i in range(n):
        game.play_randomized_best()
    return game



def play_each_other() :
    stats = play_hundred("model", "model_test")
    stats2 = play_hundred("model_test", "model")
    stats_global = [stats[0]+stats2[1],stats[1]+stats2[0]]
    return stats_global[0]<stats_global[1]


def play_hundred(str1,str2):
    stats = [0,0]
    for i in range(100) :
        game = Game_RL(str1,str2)
        rem_b = copy.deepcopy(game.b)
        while not(game.b.is_game_over()) :
            game.play_randomized_best()
        r = game.result()
        if score[0] == "W":
            stats[1] += 1
        elif score[0] == "B":
            stats[0] += 1
        game.b = copy.deepcopy(rem_b)
        game.b.nextplayercolor = Goban.board._BLACK
        game.nbmoves = 0
        game.list_moves_colors = [[],[]]
        game.list_of_moves = []
        game.player = []
    return stats

def change_model() :
    os.remove("model.json")
    os.rename("model_test.json","model.json")
    os.remove("model.h5")
    os.rename("model_test.h5","model.h5")
    os.remove("data.json")
    os.rename("data_test.json","data.json")

def training_model() :
    with open('data_test.json') as json_file :
        data  = json.load(json_file)
    model = instanciate_model()
    x_train,x_val,y_train,y_val = adaptation_data(data)
    model.fit(x_train, y_train, validation_data=(x_val,y_val), epochs=20, batch_size=128,verbose=0)
    model_json = model.to_json()
    with open("model_test.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights("model_test.h5")
    print("Saved model to disk")

def main_loop() :
    while(True) :
        collecting_data_loop()
        training_model()
        winning = play_each_other()
        if(winning) :
            print("New model won")
            change_model()

main_loop()
