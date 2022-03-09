import numpy as np

def markovDecision(layout,circle) :
    expec = np.array([])
    #dice = np.array([2,2,2,2,2,2,2,2,2,2,2,2,2,2]) # 2=security ,3=normal or 4=risky
    dice = np.array([4,4,4,4,4,4,4,4,4,4,4,4,4,4])
    for i,cell in enumerate(layout) :
        pass

    return [expec,dice]

def prob_of_cell(c1,c2,dice):
    i1,cell1 = c1
    i2,cell2 = c2
    # TODO fast lane and circle
    board_dist= i2-i1
    fast_lane=True
    prob = 1

    # Type of dice 
    prob_dice=0
    if dice==3 :
        prob_dice = 1/2
    elif dice==4 :
        prob_dice = 1

    # cell cases
    if cell1==1:
        if board_dist==0 :
            prob

    if board_dist<=dice-1:
        if i1==2 and board_dist!=0:
            prob = prob *0.5*1/dice
        prob= prob* 1/dice
    else :
        prob = 0