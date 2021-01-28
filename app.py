# -> Avancer jusqu'a x coup
# -> Jouer les parties et collecter res
import random
from GnuGo import *

rollouts = 100
dic = {'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7,'J':8}
def from_A1_to_0(position):
    letter = dic[position[0]]
    number = int(position[1])
    return  letter * 9 + number-1

#Function which produce a board to predict
#Returns : list_of_moves, white_stones, black_stones
def get_board():
    gnugo = GnuGo(9)
    moves = gnugo.Moves(gnugo)
    list_of_moves = []
    nb_moves = 20
    for i in range(nb_moves):
        moves._gnugo.query("set_random_seed" + str(101+102+12))
        move = moves.get_randomized_best()
        retvalue = moves.playthis(move)
        if retvalue == "ERR":
            return get_board()
        list_of_moves.append(move)
        if len(list_of_moves) > 1 and list_of_moves[-1] == "PASS" and list_of_moves[-2] == "PASS":
            return get_board()
        moves = gnugo.Moves(gnugo)
    return gnugo, moves,list_of_moves, gnugo.query('list_stones black')[1].strip().split(), gnugo.query('list_stones white')[1].strip().split()


#function which predict the board
def get_prediction():
    print("start")
    for i in range(rollouts) :
        gnugo,moves, list_of_moves, blackstones, whitestones = get_board()
        most_played_moves = get_score_from_board(moves, gnugo, list_of_moves, 100)

        summary = {"depth": len(list_of_moves), "list_of_moves": list_of_moves,
                "black_stones":blackstones, "white_stones": whitestones,
                "rollouts":rollout,
                #"detailed_results": scores,
                "played_moves":most_played_moves}
        # print(summary)
        #Write in file
    (ok, _) = gnugo.query("quit")


def get_score_from_board(moves,gnugo,list_of_moves,epochs) :
    to_ret = [0 for i in range(82)]
    (ok,pro) = gnugo.query("all_legal " + player)
    (ok,proba) = moves._gnugo.query("top_moves" + player)
    """for i in range(epochs) :
        #gnugo.set_random_seed(i+101+102+12)
        choice  = gnugo.Moves.get_randomized_best()
        print(choice)
        #choice = random.choice(list_of_moves,proba)
        choice = from_A1_to_0(choice)
        to_ret[choice] += 1"""
    return to_ret


get_prediction()
