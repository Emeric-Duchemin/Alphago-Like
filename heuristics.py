import tensorflow as tf
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json

# load json and create model
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = tf.keras.models.model_from_json(loaded_model_json)
# load weights into new model
model.load_weights("model.h5")

# evaluate loaded model on test data
#model.compile(loss='mae', optimizer='adam', metrics=['accuracy'])

def adapt_data(data) :
    lst = []
    once = np.zeros((9,9,2))
    for i in range(9) :
        for j in range(9) :
            if(data[i*9+j]==1) :
                once[i][j][1] = 1
            if(data[i*9+j]==2) :
                once[i][j][0] = 1
    lst.append(once)
    return np.asarray(lst)

def get_count_entries(coup,b,turn) :
    i = b._neighborsEntries[coup]
    notfind = True
    count = 0
    while b._neighbors[i] != -1 and notfind :
        fn = b._neighbors[i]
        if b._board[fn] == b._EMPTY or b._board[fn] == (turn):
            notfind = False
            count -= 1
        i+=1
        count +=1
    return count

def evaluate(b,turn,coup) :
    data = adapt_data(b._board)
    res = model.predict(data)
    if(coup == None):
        test = res[0][turn-1]
        if(test >= 1):
            print("AHAHAHAHAHA t'es nul =)")
        else:
            print("Estimate", test)
        return
    if(turn == 2) :
        adv = (b._nbBLACK-b._nbWHITE) / 1000
    else :
        adv = (b._nbWHITE-b._nbBLACK) / 1000
    count = get_count_entries(coup,b,turn)
    if(count == 4) :
        adv -= 0.65
        b.pop()
        if(not b._lastPlayerHasPassed) :
            b.push(-1)
            b.push(coup)
            b.pop()
            b.pop()
            count = get_count_entries(coup,b,turn)
            if(count != 4) :
                adv += 0.75
        b.push(coup)
    if(count == 3 and ((coup+1) % 9 <= 1 or coup <= 8 or coup >= 73 )) :
        adv -= 0.65
        b.pop()
        if(not b._lastPlayerHasPassed) :
            b.push(-1)
            b.push(coup)
            b.pop()
            b.pop()
            count = get_count_entries(coup,b,turn)
            if(count != 3) :
                adv += 0.75
        b.push(coup)
    if(b._stringLiberties[b._getStringOfStone(coup)] <= 1):
        adv -= 0.1
    return res[0][2-turn] + adv

def compute_priors(b) :
    #priors = model.predict(board)
    priors = [[0,0,0,0,0,0,0,0,0] for i in range(9)]
    priors.append(0)
    return priors
