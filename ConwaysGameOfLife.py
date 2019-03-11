# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 14:32:09 2019

@author: s.saeed
"""

#Conway's gameof life
#Finite life board
#Input is centered

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import datetime

board = [[[]]]
nMap = [[]] #Neighbor count Map
TSet = set() #List of indexes where cells were updated
newTSet = set() #List of indexes where cells going to be tested for updates

def init():
    #Creates a board lbxlb 3 layers deep
    #depth layers to capture 2 previous generations
    global board
    global nMap
    board = np.zeros((3,lb,lb)).astype(int) #force integer values instead of floats
    nMap = np.zeros((lb,lb)).astype(int)
    for index,each in np.ndenumerate(board[0]):
        newTSet.add(index) 
#    print(newTSet)
    
def createLife():
    #Life at depth  zero is randomized.
    init()
    board[0] = np.random.randint(0,2,(lb,lb))

def centerLife(life):
    #Centers the life on the 0th layer of the board
    #Using the shape of the life and life board, find start position locations
        
    #test if life is larger than board size
    if np.shape(life)[0] > lb or np.shape(life)[1]>lb:
        print("Size of life larger than board")
        return None
    
    init()
    
    (lifeX,lifeY) = np.shape(life)
    locX = math.ceil(lb/2 - lifeX/2)
    locY = math.ceil(lb/2 - lifeY/2)
    
    board[0,locX:locX+lifeX,locY:locY+lifeY] = life

def prettyPrintBoard():
    #pretty print for entire board. All 3 gens. Strictly informative
    for x in range(0,lb):
        print("\r")
        for z in range(0,3):
            for y in range(0,lb):
                print(board[z,x,y], end = " ")
            print(end="\t")
    print("\r")
   
def numOfNeighbors(loc):
    #Calculates number of live neighbors at any location for the latest gen
    (x,y) = (loc)
    left,right = x-1 , x+2
    top,bot = y-1 , y+2
    if left<0 : left = 0
    if right>lb : right = lb
    if top<0 : top = 0
    if bot>lb : bot = lb
    s = np.sum(board[0,left:right,top:bot]) - board[0,x,y]
    return(s)

def updateIndexList(index):
    global newTSet
    (x,y) = (index)
    
    left,right = x-1 , x+2
    top,bot = y-1 , y+2
    if left<0 : left = 0
    if right>lb : right = lb
    if top<0 : top = 0
    if bot>lb : bot = lb
    
#    extract = np.array(board[0,left:right,top:bot])
    for X in range(left,right):
        for Y in range(top,bot):                
            if (X,Y) not in newTSet:
                newTSet.add((X,Y))
    
def getNMap():
    #returns a 2d array of num of neighbors at each location
    #Obsolete. Incorporated into lifeStep() to eliminate extra for loop
    global nMap
    for index,each in np.ndenumerate(board[0]):
       nMap[index] = numOfNeighbors(index) 
       
def updateCell(index):
    #applies Conway's rules and updates value at a specific location
    currGen = board[0]
    if currGen[index] == 0:
        if nMap[index] ==3:
            updateIndexList(index)
            return 1
    elif currGen[index] == 1:
        if nMap[index] < 2 or nMap[index] > 3:
            updateIndexList(index)
            return 0
    return currGen[index]

def lifeStep():
    #Triggers creation of a new generation
    global nMap
    global board
    global TSet
    newGen = 1*board[0]
    TSet = set(newTSet)
    newTSet.clear()

    
#    for index,each in np.ndenumerate(board[0]):
#        nMap[index] = numOfNeighbors(index) 
#        newGen[index] = updateCell(index)
    
    for each in TSet:        
        nMap[each] = numOfNeighbors(each) 
        newGen[each] = updateCell(each)
    #new generation becomes 0th layer and all layers are shifted. 
    #Also, splice out layer older than 2 generations
    board = np.vstack(([newGen],board))[:-1,:,:]
    
'''
MAIN
'''

lb = 250        #life board size
LoopCount = 0   #loop counter
maxLoop = 100    #maximum loop count before printout
print("Timing Info for",lb,"sized board with", maxLoop,"loops")

createLife()
#centerLife([[0,0,1,0,0],[1,1,0,1,1],[1,0,1,0,1],[1,1,0,1,1],[0,0,1,0,0]])
#centerLife([[1,1,1]])
im = plt.imshow(board[0],animated = True)


def updateFig(*args):    
    global LoopCount    
    LoopCount += 1
#    print("Iteration:",LoopCount)
    if newTSet and TSet or LoopCount==1:
        lifeStep()
    im.set_array(board[0])
    
#    print(board[0])
    if LoopCount == maxLoop : 
        finish = datetime.datetime.now()
        print("Finish:",finish, "\nDiff:",(finish-start)/maxLoop) 
    return im,
        
start = datetime.datetime.now()
print("Start:",start) 

ani = anim.FuncAnimation(plt.figure(),updateFig, interval = 5, blit=True)