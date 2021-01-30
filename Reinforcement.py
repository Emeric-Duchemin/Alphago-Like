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

# FOnction gloable de récupération des données dans un json lors du self play
def collecting_data_loop() :
    #On récupère tous les données du JSON précédents et on enlève les 100 premières
    # On va les remplacer par 100 nouvelles données clalculées lors du self play.
    with open('data.json','r') as file :
        data = json.load(file)
    data = data[100:]
    stri = " "
    # On charge notre modèle qui va jouer
    model_champion1 = "model"
    for i in range(100):
        # On lance la récupération d'un plateau de jeu avec ces différentes retombées
        sum = doit(model_champion1,model_champion1)
        stri += sum + ","
    # Une fois toutes les nouvelles données récupérées on les écrits dans le fichier qui servira d'entraînement
    with open('data_test.json', 'a') as outfile:
        #outfile.write(",")
        json.dump(data,',',sum)

# Lance nb_sample simulation de monte carlo
def monte_carlo(game, game_rem, moves, nbsamples = 100):
    list_of_moves = [] # moves to backtrack
    epochs = 0 # Number of played games
    toret = []
    black_wins = 0
    white_wins = 0
    black_points = 0
    white_points = 0
    # On copie l'état du jeu au départ avant de lancer les simulations afin d'établir des statistiques.
    copy_game(game_rem,game)
    while epochs < nbsamples:
        nbmoves = 0
        # On cherche afin d'avoir un certain caractère exploratoire, à jouer les meilleurs coups randomizés.
        # Ainsi à chaque fois on ne joue pas forcément le meilleur coup (puisque l'on s'entraîne encore,
        # le choix du meilleur coup serait peut être mauvais). On cherche donc à jouer le coup aléatoire pondéré
        # Jusqu'à ce que la première ou la deuxième version du joueur gagne
        while True :
            r = game.play_randomized_best()
            nbmoves += 1
            if nbmoves > 1 and game.list_of_moves[-1] == "PASS" and game.list_of_moves[-2] == "PASS":
                break
        # On récupère ensuite le score de la partie et on le faite remonter pour le calcul des statistiques.
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
        # On revient ensuite à l'état de plateau initial pour relancer une simulation
        copy_game(game,game_rem)
    if(game.nextPlayer == 2) : # Si le prochain player est white
        return format(black_wins/float(nbsamples),'.2f')
    else :
        return format(white_wins/float(nbsamples),'.2f')

_dic = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'J':8}

def flatten(s):
    return (_dic[s[0]], int(s[1]) - 1)

# Fonction qui va se charger de lancer une simulation pour un plateau qu'elle va sélectionner.
def doit(model_champion1, model_champion2):
    # On instancie notre environnement de jeu.
    game = Game_RL(model_champion1, model_champion2)
    # On instancie la variable qui nous permettra de revenir à l'état initial
    game_rem = Game_RL(model_champion1, model_champion2)
    # On joue un certains nombre de coup pour se retrouver plus tard dans un état intéressant
    game = start(game)
    legal = game.b.legal_moves()
    proba_matrix = [[0 for i in range(9)] for j in range(9)]
    # On calcule aléatoirement le nombre de rollout que l'on va effectuer
    nb_rollout = (110 - min(100, len(legal) * 2)) // 2
    copy_game(game_rem,game)
    # On joue tous les coups possibles à partir du plateau que l'on a et on récupère les statistiques
    # associées à chaque coup
    for m in legal :
        game.play_this(m)
        proba_win = monte_carlo(game, game_rem,game.list_of_moves, nb_rollout)
        copy_game(game,game_rem)
        flat_move = flatten(m)
        proba_matrix[flat_move[0]][flat_move[1]] = proba_win
    game.play_this("PASS")
    copy_game(game,game_rem)
    # On calcule les proba pour le dernier coup : PASS
    proba_win_pass = monte_carlo(game, game_rem, game.list_of_moves, nb_rollout)
    # On renvoie ensuite la compilation des résultats pour l'écriture dans le JSON
    summary = {"depth": len(list_of_moves), "list_of_moves": list_of_moves,
                "black_stones":blackstones, "white_stones": whitestones,
                "rollouts":nb_rollout,
                "winning_proba" : proba_matrix, "proba_win_pass": proba_win_pass,
                "black_wins":0, "black_points": 0,
                "white_wins":0, "white_points":0, "player": moves.player()}
    return summary

# Fonction qui copie l'état de game2 dans game1
def copy_game(game1,game2) :
    game1.b = copy.deepcopy(game2.b)
    game1.nextplayercolor = game2.nextplayercolor
    game1.nbmoves = game2.nbmoves
    game1.list_moves_colors = copy.deepcopy(game2.list_moves_colors)
    game1.list_of_moves = copy.deepcopy(game2.list_of_moves)
    #game1.player = copy.deepcopy(game2.player)

# Joue entre 40 et 50 coups pour partir d'un plateau de départ intéressant
def start(game):
    n = random.randrange(40, 50)
    list_of_moves = []
    blackstones = []
    whitestones = []
    for i in range(n):
        game.play_randomized_best()
    return game


# Lance 200 parties entre les deux modèles (le nouveau modèle contre l'ancien)
# 100 parties dans chaque configuration (Blanc/Noir)
def play_each_other() :
    stats = play_hundred("model", "model_test")
    stats2 = play_hundred("model_test", "model")
    # On récupère ensuite les statistiques de victoire
    stats_global = [stats[0]+stats2[1],stats[1]+stats2[0]]
    return stats_global[0]<stats_global[1]


def play_hundred(str1,str2):
    stats = [0,0]
    # Lance 100 jeux blanc contre noir
    for i in range(100) :
        game = Game_RL(str1,str2)
        rem_b = copy.deepcopy(game.b)
        # On joue 100 partie avec des coups randomizé pondéré.
        # On fait cela pour éviter de toujours jouer les même coups
        # On teste ainsi la robustesse de l'algorithme.
        while not(game.b.is_game_over()) :
            game.play_randomized_best()
        r = game.result()
        if score[0] == "W":
            stats[1] += 1
        elif score[0] == "B":
            stats[0] += 1
        # On réinitialise le plateau de jeux pour pouvoir recommencer une nouvelle partie. 
        game.b = copy.deepcopy(rem_b)
        game.b.nextplayercolor = Goban.board._BLACK
        game.nbmoves = 0
        game.list_moves_colors = [[],[]]
        game.list_of_moves = []
        game.player = []
    return stats

# Echange le model_test avec le modèle model
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
    # Instancie le modèle avec les poids du json et du h5
    model = instanciate_model()
    # spéare et prépare les données
    x_train,x_val,y_train,y_val = adaptation_data(data)
    # Entraînement du modèle
    model.fit(x_train, y_train, validation_data=(x_val,y_val), epochs=20, batch_size=128,verbose=0)
    # Enregistre le modèle
    model_json = model.to_json()
    with open("model_test.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights("model_test.h5")
    print("Saved model to disk")

# Fonction main
# Appelle chaque composante de la boucle d'apprentissage
def main_loop() :
    while(True) :
        collecting_data_loop()
        training_model()
        winning = play_each_other()
        if(winning) :
            print("New model won")
            change_model()

main_loop()
