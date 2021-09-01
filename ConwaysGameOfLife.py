# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 14:32:09 2019

@author: s.saeed
"""

# Conway's game of life
# Finite life board
# Input is centered

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import datetime
import csv
import os, psutil

process = psutil.Process(os.getpid())
board = [[[]]]  # Main board 3 layers deep to track 3 generations
nMap = [[]]  # Neighbor count Map
TSet = set()  # List of indexes where cells were updated
newTSet = set()  # List of indexes where cells going to be tested for updates
DataMap = {}

def convBinaryStringToMatrix(s, l=0, w=0):
    if l == 0:
        l = int(math.sqrt(len(s)))
    if w == 0:
        w = l

    mat = np.zeros((l, w), dtype=int)
    x = 0
    y = 0
    for i in range(len(s)):
        c = s[i]
        mat[(x, y)] = int(c)
        y += 1
        if y >= l:
            y = 0
            x += 1
        if x >= w:
            return mat


def convMatrixToBinaryString(mat):
    s = ""
    for index, val in np.ndenumerate(mat):
        s = s + str(val)
    return (s)


def genLifeGroupDict(grpSize,startPos = 0):
    # Generates a csv associated with a Dict/Hashmap for a given size of life group
    # Said csv can be loaded on startup to avoid calculating Conway's rules at runtime
    # Saves all possible permutations in hashmap
    # grpSize has to be >=1, and implies width/height of grouping
    # Since surrounding cells affect value of cell in lifeStep
    # calculation, a grpSize of 1 generates a 3x3 hashmap for a 3x3 array.
    # grpSize of 2 will generate a 4x4 hashmap for a 4x4 array
    # Note: increasing grpSize takes successively more and more time!
    # grpSize = 2 has 65k unique combinations to account for

    finalDict = {}
    g = grpSize + 2
    b = np.zeros((g, g))
    global nMap
    init(g)
    for i in range(startPos+1,2 ** (g ** 2)):
        keyStr = str(bin(i))[2:].zfill(g ** 2)
        k = convBinaryStringToMatrix(keyStr)
        getNMap(k)
        v = np.zeros(k.shape, dtype=int)
        for index, val in np.ndenumerate(k):
            v[index] = updateCell(index, k)

        finalDict[keyStr] = convMatrixToBinaryString(v)
        if i % 1000 == 0 and i % 10000 != 0: print(i)
        if i % 10000 == 0 and i > 0:
            print(i, "File Written")
            partNumber = int(i/10000)
            f = "DataMap for group Cluster of " + str(grpSize) + "x" + \
                str(grpSize) + " combinations - Part " + str(partNumber) + ".csv"
            partNumber = partNumber + 1
            writeCSVFile(f, finalDict)
            finalDict.clear()

        f = "DataMap for group Cluster of " + str(grpSize) + "x" + str(grpSize) + " combinations.csv"
        writeCSVFile(f, finalDict)


def writeCSVFile(fileName, d):
    csv_file = fileName
    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for oldGen, newGen in d.items():
                writer.writerow([oldGen, newGen])
    except IOError:
        print("I/O error")

def readDataMapsFromFile():
    # Reads all data maps saved in current working directory and maps it to dictionary
    # Note: All datamaps files are identified with the prefix 'DataMap...'
    global DataMap
    s = os.getcwd()
    onlyfiles = [f for f in os.listdir(s) if os.path.isfile(os.path.join(s, f))]
    for each in onlyfiles:
        print("Reading " + str(each))
        if each.startswith("DataMap"):    
            try:
                with open(each, 'r', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for rows in reader:
                        DataMap[rows[0]] = rows[1]
            except IOError:
                print("I/O error")
        

def init(boardSize):
    # Creates a board lbxlb 3 layers deep
    # depth layers to capture 2 previous generations
    global board
    global nMap
    board = np.zeros((3, boardSize, boardSize)).astype(int)  # force integer values instead of floats
    nMap = np.zeros((boardSize, boardSize)).astype(int)
    for index, each in np.ndenumerate(board[0]):
        newTSet.add(index)


def createLife():
    # Life at depth  zero is randomized.
    board[0] = np.random.randint(0, 2, (board[0].shape[0], board[0].shape[0]))


def centerLife(life):
    # Centers the life on the 0th layer of the board
    # Using the shape of the life and life board, find start position locations

    # test if life is larger than board size
    global board
    if np.shape(life)[0] > np.shape(board[0])[0] or np.shape(life)[1] > np.shape(board[0])[0]:
        print("Size of life larger than board")
        return None

    init()

    (lifeX, lifeY) = np.shape(life)
    locX = math.ceil(np.shape(board[0])[0] / 2 - lifeX / 2)
    locY = math.ceil(np.shape(board[0])[0] / 2 - lifeY / 2)

    board[0, locX:locX + lifeX, locY:locY + lifeY] = life


def prettyPrintBoard():
    # pretty print for entire board. All 3 gens. Strictly informative
    for x in range(0, lb):
        print("\r")
        for z in range(0, 3):
            for y in range(0, lb):
                print(board[z, x, y], end=" ")
            print(end="\t")
    print("\r")


def numOfNeighbors(loc, b):
    # Calculates number of live neighbors at any location for the latest gen
    # loc index location of cell, b = board associated with the loc
    (x, y) = loc
    left, right = x - 1, x + 2
    top, bot = y - 1, y + 2
    boardSize = b.shape[0]
    if left < 0: left = 0
    if right > boardSize: right = boardSize
    if top < 0: top = 0
    if bot > boardSize: bot = boardSize
    s = np.sum(b[left:right, top:bot]) - b[x, y]
    return s


def updateIndexList(index, boardSize):
    global newTSet
    (x, y) = index

    left, right = x - 1, x + 2
    top, bot = y - 1, y + 2
    if left < 0: left = 0
    if right > boardSize: right = boardSize
    if top < 0: top = 0
    if bot > boardSize: bot = boardSize

    for X in range(left, right):
        for Y in range(top, bot):
            if (X, Y) not in newTSet:
                newTSet.add((X, Y))


def getNMap(b=None):
    # returns a 2d array of num of neighbors at each location
    # Obsolete. Incorporated into lifeStep() to eliminate extra for loop
    global nMap
    global board
    if b is None: b = board[0]
    for index, each in np.ndenumerate(b):
        nMap[index] = numOfNeighbors(index, b)


def updateCell(index, b):
    # applies Conway's rules and updates value at a specific location
    currGen = b
    if currGen[index] == 0:
        if nMap[index] == 3:
            updateIndexList(index, b.shape[0])
            return 1
    elif currGen[index] == 1:
        if nMap[index] < 2 or nMap[index] > 3:
            updateIndexList(index, b.shape[0])
            return 0
    return currGen[index]


def lifeStep(b=None):
    # Triggers creation of a new generation
    global nMap
    global board
    global TSet
    newGen = 1 * board[0]
    TSet = set(newTSet)
    newTSet.clear()

    for each in TSet:
        nMap[each] = numOfNeighbors(each, board[0])
        newGen[each] = updateCell(each, board[0])
    # new generation becomes 0th layer and all layers are shifted.
    # Also, splice out layer older than 2 generations
    board = np.vstack(([newGen], board))[:-1, :, :]


'''
MAIN
'''
'''
lb = 200  # life board size
LoopCount = 0  # loop counter
maxLoop = 100  # maximum loop count before printout
print("Timing Info for", lb, "sized board with", maxLoop, "loops")

init(lb)
createLife()


def updateFig(*args):
    global LoopCount
    LoopCount += 1
    if newTSet and TSet or LoopCount == 1:
        lifeStep()
    im.set_array(board[0])
    if LoopCount == maxLoop:
        finish = datetime.datetime.now()
        print("Finish:", finish, "\nDiff:", (finish - start) / maxLoop)
        print(process.memory_info().rss / 1024 / 1024, " MB")
        ani.event_source.stop()
    return im,


start = datetime.datetime.now()
print("Start:", start)

fig = plt.figure(figsize = [5,5],facecolor = 'white')
ani = anim.FuncAnimation(fig, updateFig, interval=10, blit=True)
im = plt.imshow(board[0], animated=True)

plt.show()
'''
# readDataMapsFromFile()

genLifeGroupDict(3,100001)