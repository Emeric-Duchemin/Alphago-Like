# -*- coding: utf-8 -*-

import time
import Goban
from random import randint, choice,uniform
from playerInterface import *
import sys
import heuristics
import copy
from queue import PriorityQueue

# Utilisée pour l'affichage
dico_win = {"1-0":[1,0],"0-1":[0,1],}

#debugging function
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#Fonction qui donne le prochain élément d'une liste et le retire de celle-ci
def next_elem_list(lst) :
    return lst[0],lst[1:]

#Fonction qui donne le prochain élément d'une queue et le retire de celle-ci
def next_elem_queue(queue) :
    return queue.get()[1],queue

class Node():
    estimated_win = np.full((9,9),0.0001)
    node_score = 0
    children = []
    prior = None
    coup = None
    visited = 0


    # Note : si le prior est None alors c'est que ce noeud correpond à root
    def __init__(self,coup, prior) :
        self.coup = coup
        self.prior = prior

    #TODO
    #Créer tous les children quand on traite le noeud pour la première fois
    def getConfidenceBound() :
        return(self.node_score/self.visited + np.sqrt(C*(prior.visited-self.visited)/self.visited))

    def updateScore(self,win) :
        self.node_score  = self.node_score + win
        self.visited += 1

    def getBestMove(self) :
        return max(range(len(self.children)), key=lambda i: self.children[i].node_score)

    def getBestConfidence(self) :
        return max(range(len(self.children)), key=lambda i: self.children[i].getConfidenceBound())

class myPlayer(PlayerInterface):

    def roll_game(self, b, playerTurn) :
        board = copy.deepcopy(b)
        while(not b._gameOver) :
            b.push(self.getBestMove(b,playerTurn))
            playerTurn = 3-playerTurn
        res = b.result()
        return [dico_win.get(res,[0.5,0.5])[2-playerTurn]]

    def getBestMove(self,b,playerTurn) :
        pass

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self.nbmoves = 0
        self.total_time = 0

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
        # On suppose que les paternes sont rectangulaires (on pourra faire autrement mais c'est pas fun)
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
        move = self.alpha_bet_id(self._board,True,t1,self.getTimer(self._board))
        self._board.push(move)
        heuristics.evaluate(self._board,self._mycolor, None) # Show estimations
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
