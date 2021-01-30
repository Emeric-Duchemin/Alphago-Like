import random
import numpy as np
import math
import statistics
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization,  MaxPooling2D
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
import tensorflow.keras
import tensorflow.keras.optimizers as optimizers
import tensorflow as tf
import sklearn.model_selection
import json
import functools
import operator
import sys

#Instancie le modèle à deux tête qui permet :
#    - un qui permet l'évaluation du plateau
#    - le second qui donne les coups les plus probables à jouer
def instanciate_model() :
    model = Sequential()
    imputs = Input(shape=(9,9,3))
    x = Conv2D( 64 , kernel_size=3, activation='relu', padding='same', data_format='channels_last' ,input_shape=(9,9,3))(imputs)
    x = Conv2D( 64 , kernel_size=5, activation='relu', padding='same', data_format='channels_last' )(x)
    #model.add(BatchNormalization())
    x = Conv2D( 32 , kernel_size=3, activation='relu', padding='same', data_format='channels_last' )(x)
    #model.add(BatchNormalization())
    x = Conv2D( 64 , kernel_size=3, activation='relu', padding='same', data_format='channels_last' )(x)
    x = Flatten()(x)
    x = Dense(units=128,activation='relu')(x)

    board = Dense(units=82,activation='relu', name='board')(x)
    glob = Dense(units=1,activation='relu', name='global')(x)

    model = Model(inputs=imputs,
                  outputs = [board, glob],
                  name="Champion4")

    model.compile(loss={'board' : 'mse', 'global' : 'mse'},optimizer='adam',metrics={'board':'accuracy', 'global':'accuracy'})

    return model

def name_to_coord(s):
    assert s != "PASS"
    indexLetters = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'J':8}

    col = indexLetters[s[0]]
    lin = int(s[1:]) - 1
    return col, lin

# Fonction qui permet d'adapter les données à l'entrée désirée par le modèle.
# Réalise aussi l'augmentation de données
def create_data(data):
    lst = []
    for i in data :
        once = np.zeros((9,9,3))
        for j in i["black_stones"] :
            if(j != "PASS") :
                once[name_to_coord(j)[0]][name_to_coord(j)[1]][1] = 1
        for j in i["white_stones"] :
            if(j != "PASS") :
                once[name_to_coord(j)[0]][name_to_coord(j)[1]][0] = 1
        once[:][:][2].fill(i["depth"]%2)
        # Calcul de toutes les rotations
        dos = np.rot90(once,axes=(0,1))
        tres = np.rot90(dos,axes=(0,1))
        cuatro = np.rot90(tres,axes=(0,1))
        sym_h_once = np.flipud(once)
        sym_v_once = np.fliplr(once)
        sym_h_dos = np.flipud(dos)
        sym_v_dos = np.fliplr(dos)
        sym_h_tres = np.flipud(tres)
        sym_v_tres = np.fliplr(tres)
        sym_h_cuatro = np.flipud(cuatro)
        sym_v_cuatro = np.fliplr(cuatro)
        lst.append(sym_h_once)
        lst.append(sym_v_once)
        lst.append(sym_h_dos)
        lst.append(sym_v_dos)
        lst.append(sym_h_tres)
        lst.append(sym_v_tres)
        lst.append(sym_h_cuatro)
        lst.append(sym_v_cuatro)
        lst.append(once)
        lst.append(dos)
        lst.append(tres)
        lst.append(cuatro)
    lst = np.asarray(lst)
    return lst

# Créé les Y associés aux X déjà calculés dans la fonction create_data
def create_predictions(data) :
    lst = []
    for i in data :
        once = np.asarray(i["winning_proba"])
        s = 0
        nb = 0
        for k in range(len(once)):
          for j in range(len(once[0])):
            if len(once[k][j]) > 1:
              s += float(once[k][j])
              nb += 1
        #On calcule toutes les rotations et on leur affecte le Y correspondant.
        dos = np.rot90(once,axes=(0,1))
        tres = np.rot90(dos,axes=(0,1))
        cuatro = np.rot90(tres,axes=(0,1))
        sym_h_once = np.flipud(once)
        sym_v_once = np.fliplr(once)
        sym_h_dos = np.flipud(dos)
        sym_v_dos = np.fliplr(dos)
        sym_h_tres = np.flipud(tres)
        sym_v_tres = np.fliplr(tres)
        sym_h_cuatro = np.flipud(cuatro)
        sym_v_cuatro = np.fliplr(cuatro)
        once = list(once.astype('float32').flatten())
        dos = list(dos.astype('float32').flatten())
        tres = list(tres.astype('float32').flatten())
        cuatro = list(cuatro.astype('float32').flatten())
        sym_h_once = list(sym_h_once.astype('float32').flatten())
        sym_v_once = list(sym_v_once.astype('float32').flatten())
        sym_h_dos = list(sym_h_dos.astype('float32').flatten())
        sym_v_dos = list(sym_v_dos.astype('float32').flatten())
        sym_h_tres = list(sym_h_tres.astype('float32').flatten())
        sym_v_tres = list(sym_v_tres.astype('float32').flatten())
        sym_h_cuatro = list(sym_h_cuatro.astype('float32').flatten())
        sym_v_cuatro = list(sym_v_cuatro.astype('float32').flatten())

        once.append(float(i["proba_win_pass"]))
        dos.append(float(i["proba_win_pass"]))
        tres.append(float(i["proba_win_pass"]))
        cuatro.append(float(i["proba_win_pass"]))
        sym_h_once.append(float(i["proba_win_pass"]))
        sym_v_once.append(float(i["proba_win_pass"]))
        sym_h_dos.append(float(i["proba_win_pass"]))
        sym_v_dos.append(float(i["proba_win_pass"]))
        sym_h_tres.append(float(i["proba_win_pass"]))
        sym_v_tres.append(float(i["proba_win_pass"]))
        sym_h_cuatro.append(float(i["proba_win_pass"]))
        sym_v_cuatro.append(float(i["proba_win_pass"]))
        once.append(float(s/nb))
        dos.append(float(s/nb))
        tres.append(float(s/nb))
        cuatro.append(float(s/nb))
        sym_h_once.append(float(s/nb))
        sym_v_once.append(float(s/nb))
        sym_h_dos.append(float(s/nb))
        sym_v_dos.append(float(s/nb))
        sym_h_tres.append(float(s/nb))
        sym_v_tres.append(float(s/nb))
        sym_h_cuatro.append(float(s/nb))
        sym_v_cuatro.append(float(s/nb))
        lst.append(sym_h_once)
        lst.append(sym_v_once)
        lst.append(sym_h_dos)
        lst.append(sym_v_dos)
        lst.append(sym_h_tres)
        lst.append(sym_v_tres)
        lst.append(sym_h_cuatro)
        lst.append(sym_v_cuatro)
        lst.append(once)
        lst.append(dos)
        lst.append(tres)
        lst.append(cuatro)
    return np.asarray(lst)

# Fonction qui adapte les data à donner au modèle pour l'entraînement
def adaptation_data(data) :
    X = create_data(data)
    Y = create_predictions(data)
    #On sépare entre entraînement et validation
    X_train,X_val,Y_train,Y_val = sklearn.model_selection.train_test_split(X,Y,test_size=0.33,shuffle=True)
    tmp1 = []
    tmp2 = []
    # On adapte le format des Y, résultats lors de l'apprentissage
    for i in range(len(Y_train)):
      tmp1.append(np.array(Y_train[i][:-1]))
      tmp2.append(np.array([Y_train[i][-1], 1 - Y_train[i][-1]]))

    Y_train = [np.array(tmp1), np.array(tmp2)]

    tmp1 = []
    tmp2 = []

    for i in range(len(Y_val)):
      tmp1.append(np.array(Y_val[i][:-1]))
      tmp2.append(np.array([Y_val[i][-1], 1 - Y_val[i][-1]]))

    Y_val = [np.array(tmp1), np.array(tmp2)]
    return X_train,X_val,Y_train,Y_val
