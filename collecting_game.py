import sys
import importlib
import time
from io import StringIO
import Goban
import myPlayer

class Game_RL() :

    __init()__ :
        self.b = Goban.Board()
        self.nextplayercolor = Goban.Board._BLACK
        self.nbmoves = 0
        self.list_moves_colors = [[],[]]
        self.list_of_moves = []
        self.player = []


    def initialize_player(model_champion1, model_champion2):
        self.player.append(myPlayer.myPlayer(model_champion1))
        self.player.append(myPlayer.myPlayer(model_champion2))
        self.player[0].newGame(Goban.Board._BLACK)
        self.player[1].newGame(Goban.Board._WHITE)


    def play() :
        while not b.is_game_over():
            nbmoves += 1
            otherplayer = (nextplayer + 1) % 2
            othercolor = Goban.Board.flip(nextplayercolor)

            currentTime = time.time()
            sys.stdout = stringio
            move = players[nextplayer].getPlayerMove() # The move must be given by "A1", ... "J8" string coordinates (not as an internal move)
            sys.stdout = sysstdout
            playeroutput = stringio.getvalue()
            stringio.truncate(0)
            stringio.seek(0)
            print(("[Player "+str(nextplayer) + "] ").join(playeroutput.splitlines(True)))
            outputs[nextplayer] += playeroutput
            totalTime[nextplayer] += time.time() - currentTime
            print("Player ", nextplayercolor, players[nextplayer].getPlayerName(), "plays: " + move) #changed

            if not Goban.Board.name_to_flat(move) in legals:
                print(otherplayer, nextplayer, nextplayercolor)
                print("Problem: illegal move")
                wrongmovefrom = nextplayercolor
                break
            b.push(Goban.Board.name_to_flat(move)) # Here I have to internally flatten the move to be able to check it.
            players[otherplayer].playOpponentMove(move)

            nextplayer = otherplayer
            nextplayercolor = othercolor

            print("Round time", time.time() - currentTime)

    def play_randomized_best(self):
        m = self.player[self.nextplayercolor-1].get_randomized_best()
        self.play_this(m)
        return

    def play_this(self,m) :
        self.b.push(Goban.Board.name_to_flat(move))
        self.list_of_moves.append(move)
        self.list_moves_colors[self.nextplayercolor-1].append(move)
        self.nextplayercolor = 3 - self.nextplayercolor
        self.nbmoves += 1
        return

    def result(self) :
        return self.b.result()


    # players = []
    # player1class = importlib.import_module(classNames[0])
    # player1 = player1class.myPlayer()
    # player1.newGame(Goban.Board._BLACK)
    # players.append(player1)
    #
    # player2class = importlib.import_module(classNames[1])
    # player2 = player2class.myPlayer()
    # player2.newGame(Goban.Board._WHITE)
    # players.append(player2)
