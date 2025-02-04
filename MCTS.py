import time
import Goban
from random import randint, choice,uniform
from playerInterface import *
import sys
import heuristics
from queue import PriorityQueue
import numpy as np
import random
import sys
import copy
from numpy.random import choice

nb_machine = 100
nb_run = 100
C = 2


class oneBandit():
    def __init__(self, mu=None):
        if mu is None:
            self._mu = random.random() # moyenne de payoff de la machine
        else:
            self._mu = mu


class Casino():
    nb_coup = 1
    choosen_machines = []
    machine_mu = []
    _machines = []

    def __init__(self, nb=100, mus = -1):
        if(mus == -1) :
            self.machine_mu = [-1 for i in range(nb)]
        else :
            self.machine_mu = mus
        self.choosen_machines = [0.0001 for x in range(nb)]
        for _ in range(nb):
            self._machines.append(oneBandit())

    def playMachine(self, i):
        play = self._machines[i].playIt()
        if(self.machine_mu[i] == -1) :
            self.machine_mu[i] = play
        else :
            self.machine_mu[i] = (self.machine_mu[i] * self.choosen_machines[i] + play) / (self.choosen_machines[i] +1)
        self.choosen_machines[i] += 1
        self.nb_coup += 1
        return play


    def compute_upper_confidence_bound(self,i):
        return self.machine_mu[i] + np.sqrt(np.abs(C*np.log(self.nb_coup-self.choosen_machines[i])) /self.choosen_machines[i])


"""
casino = Casino()
def casinoRun():
    for i in range(nb_machine) :
        casino.playMachine(i)
    for i in range(initialCredits-nb_machine) :
        jevaischoose = max(range(nb_machine),key = lambda x : casino.compute_upper_confidence_bound(x))
        casino.playMachine(jevaischoose)
    youredabest = max(range(100),key= lambda x : casino.machine_mu[x])

    print("You're da best : " + str(youredabest))
    print(casino.realBestChoice())
"""
# Utilisée pour l'affichage
dico_win = {"1-0":[1,0],"0-1":[0,1],"1/2-1/2":[0.5,0.5]}

#debugging function
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#Fonction qui donne le prochain élément d'une liste et le retire de celle-ci
def next_elem_list(lst) :
    return lst[0],lst[1:]

#Fonction qui donne le prochain élément d'une queue et le retire de celle-ci
def next_elem_queue(queue) :
    return queue.get()[1],queue

class myPlayer(PlayerInterface):

    def __init__(self,model=''):
        self._mycolor = None
        self.nbmoves = 0
        self.total_time = 0
        self.model = heuristics.load_model(model)

    def getPlayerName(self):
        return "Clemeric"

    # Calcul de l'heuristique
    def exemplePattern(self, b, i):
        length = 1
        if b==0:
            return (length, 1)
        else:
            return b._board[i]

    def patternFound(self, pattern, b):
        # On suppose que les patern sont rectangulaires (on pourra faire autrement mais c'est pas fun)
        l, h = pattern(0, 0)
        s = 0
        for i in range(10-h):
            for j in range(10-l):
                s += pattern(b, i + 9 * j)
        return s

    # Calcul le temps alloué pour l'itérative deepning
    def getTimer(self, b):
        nb = 81 - b._nbBLACK-b._nbWHITE
        if(nb >= 10):
            return (4/ -71) * nb + 5.5
        else:
            return (2 / 9) * nb + 2.8

    # Appel de l'algorithme de MCTS.
    def mcts(self,b):
        proba_moves,probas,corresp = self.mcts_probas(b)
        legal_moves = b.legal_moves()
        cestmonmeilleurchoix = max(range(len(proba_moves)),key = lambda x : probas[x])
        return corresp[cestmonmeilleurchoix]

    # Fonction qui permet de récupérer les probas associées à MCTS
    # On a donc en sorti les mu de chaque machine ainsi qu'une liste de probabilité de coups.
    def mcts_probas(self,b) :
        count = 0
        # On instancie un Casino et on calcule quels priors peuvent effectivement être joué et lesquels ne peuvent pas.
        proba_moves = self.get_priors(b)
        legal_moves = b.legal_moves()
        proba_moves, corresp = self.get_only_legals(legal_moves,proba_moves)
        casino = Casino(len(proba_moves),proba_moves)
        visited = [1 for i in proba_moves]
        moving_board = copy.deepcopy(b)
        # On lance nb_run pour mettre à jour la liste de priors.
        while count < nb_run :
            cestmonchoix = max(range(len(proba_moves)),key = lambda x : casino.compute_upper_confidence_bound(x))
            moving_board.push(corresp[cestmonchoix])
            # On lance un rollout à partir du coup joué
            reward = self.run_rollout(moving_board,3-self._mycolor,self._mycolor)
            # On met à jour les priors avec les résultats obtenus lors du rollout
            casino.machine_mu[cestmonchoix] = (casino.machine_mu[cestmonchoix] * casino.choosen_machines[cestmonchoix] + reward[1]) / (casino.choosen_machines[cestmonchoix] +1)
            casino.choosen_machines[cestmonchoix] += 1
            casino.nb_coup += 1
            moving_board = copy.deepcopy(b)
            count += 1
        return proba_moves,casino.machine_mu, corresp

    # Choisi un coup parmi la liste des coups possibles en pondérant le choix avec les probabilité données par les priors
    def get_randomized_best(self,b) :
        proba_moves, probas,corresp = self.mcts_probas(b)
        legal_moves = b.legal_moves()
        cestmonchoix = random.choices(range(len(legal_moves)),weights=probas)[0]
        return corresp[cestmonchoix]

    # Lance un rollout à partir de l'état de jeux dans lequel on est déjà placé
    def run_rollout(self,b,color,init_color):
        if(b._gameOver) :
            res = b.result()
            return [True,dico_win.get(res,[0.5,0.5])[init_color-1]]
        lmoves = b.legal_moves()
        move = self.choose_move_random(b,color,lmoves)
        b.push(lmoves[move])
        return self.run_rollout(b,3-color,init_color)


    # Fonction qui permet de ne récupérer que les case pouvant être effectivement jouée
    def get_only_legals(self,lmoves, predicted):
        toRet = []
        toRet2 = []
        for i in lmoves :
            if i == -1 :
                toRet.append(predicted[0][0][-1])
                toRet2.append(-1)
            else :
                #index = self._board.unflatten(i)
                toRet.append(predicted[0][0][i])
                toRet2.append(i)
        return toRet,toRet2


    # Retourne les priors
    def get_priors(self,b):
        return heuristics.compute_priors(self.model,b)
    # Joue aléatoirement
    def choose_move_random(self,b,color,lmoves) :
        return random.choice(range(len(lmoves)))


    """
    #Alpha beta
    def alpha_bet_e_id_opening(self,b,coup,prof,maxprof,alpha,beta,timing,timeout) :
        mini = beta
        if(b._gameOver) :
            res = b.result()
            return [True,dico_win.get(res,[0.5,0.5])[2-self._mycolor]]
        if(prof>maxprof) :
            return [True,heuristics.evaluate(b,3-self._mycolor,coup)]
        else :
            for i in b.legal_moves() :
                b.push(i)
                t1 = time.time()
                res = self.alpha_bet_f_id_opening(b,i,prof+1,maxprof,alpha,mini,timing,timeout)
                b.pop()
                t1 = time.time()
                if(mini > res[1]) :
                    mini = res[1]
                if(mini<=alpha):
                    return [True,alpha]
                if(t1-timing>0.9*timeout or self.total_time+t1-timing>=298) :
                    return [False, mini]
        return [True,mini]

    def alpha_bet_f_id_opening(self,b,coup,prof,maxprof,alpha,beta,timing, timeout) :
        maxi = [alpha,0]
        if(b._gameOver) :
            res = b.result()
            return [True,dico_win.get(res,[0.5,0.5])[2-self._mycolor]]
        for i in b.legal_moves() :
            b.push(i)
            t1 = time.time()
            res = self.alpha_bet_e_id_opening(b,i,prof+1,maxprof,maxi[0],beta,timing,timeout)
            b.pop()
            t1 = time.time()
            if(res[1]>maxi[0]) :
                maxi[0] = res[1]
                maxi[1] = i
            if(maxi[0]>=beta):
                return [True,beta]
            if((t1-timing>0.9*timeout or self.total_time+t1-timing>=298) and maxprof > 1) :
                return [False, maxi[0]]
        if(prof == 1) :
            return [True,maxi[1]]
        return [True,maxi[0]]



    def alpha_bet_f_id(self,b,coup,prof,maxprof,alpha,beta,timing, timeout,lst) :
        maxi = [0,alpha]
        if(b._gameOver) :
            res = b.result()
            return [True,dico_win.get(res,[0.5,0.5])[2-self._mycolor]]
        queue = PriorityQueue()
        if(lst[0]!=[]) :
            pile = lst[0]
            next_elem = next_elem_queue
            empty = lambda x : x.empty()
        else :
            pile = b.legal_moves()
            next_elem = next_elem_list
            empty = lambda x : x==[]
        while not empty(pile) :
            i,pile = next_elem(pile)
            #eprint(i)
            b.push(i)
            t1 = time.time()
            res = self.alpha_bet_e_id_opening(b,i,prof+1,maxprof,maxi[1],beta,timing,timeout)
            b.pop()
            t1 = time.time()
            if((t1-timing>0.9*timeout or self.total_time+t1-timing>=298) and maxprof > 1) :
                return [False,maxi]
            if(res[1]+uniform(0,0.00001)>maxi[1]) :
                maxi[1] = max(res[1],maxi[1])
                maxi[0] = i
            queue.put((1-res[1],i))
            if(maxi[1]>=beta):
                return [True,beta]
        if(prof == 1) :
            return [True,[queue,maxi]]
        return [True,maxi[1]]


    def alpha_bet_id(self,b,ami,timing,timeout) :
        coup_to_play = choice(self._board.legal_moves())
        lst = [[]]
        if(self.nbmoves < 5):
            to_check = self.alpha_bet_f_id_opening(b,coup_to_play,1,1,-5001,5001,timing,timeout)
            if(to_check[0]) :
                coup_to_play = to_check[1]
            else :
                return coup_to_play
            return coup_to_play
        deep = 1
        nottimeout = True
        t1=time.time()
        max = 0
        while(t1-timing<0.9*timeout and self.total_time+t1-timing<=298) :
            to_check = self.alpha_bet_f_id(b,coup_to_play,1,deep,-5001,5001,timing,timeout,lst)
            if(to_check[0]) :
                coup_to_play = to_check[1][1][0]
                max = to_check[1][1][1]
                lst[0] = to_check[1][0]
            else :
                if(max<to_check[1][1]) :
                    return to_check[1][0]
                else :
                    return coup_to_play
            deep += 0
            t1=time.time()
        return coup_to_play
    """

    def getPlayerMove(self):
        timun = time.time()
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        if(self.total_time>=298) :
            return "PASS"
        if(self._board._lastPlayerHasPassed) :
            score = self._board.compute_score()
            if(score[self._mycolor-1] > score[2-self._mycolor]) :
                return "PASS"
        t1=time.time()
        move = self.mcts(self._board)
        sys.stderr.write(str(move))
        self._board.push(move)
        heuristics.evaluate(self.model,self._board,self._mycolor, None) # Show estimations
        self.nbmoves += 1
        self.total_time += time.time()-timun
        return self._board.flat_to_name(move)

    def playOpponentMove(self, move):
        print("Opponent played ", move)
        self._board.push(self._board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

"""# TODO:
- Le petit réseau de neurone double tête
- La boucle de reinforcement
- Scinder les deux
"""
