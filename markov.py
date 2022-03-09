import numpy as np

def markovDecision(layout,circle) :
    expec = np.array([])
    #dice = np.array([2,2,2,2,2,2,2,2,2,2,2,2,2,2]) # 2=security ,3=normal or 4=risky
    dice = np.array([4,4,4,4,4,4,4,4,4,4,4,4,4,4])
    for i,cell in enumerate(layout) :
        pass

    return [expec,dice]

def prob_from_cell_to_cell(to_state,from_state,dice,circle):
    to_ind,to_cell = to_state
    from_ind,from_cell = from_state

    # No prob from goal
    if from_ind==14:
        return 0
    
    board_dist=0
    # End of slow lane
    if to_ind==14 and from_ind<10:
        board_dist-=4
    # Start of fast lane
    elif to_ind >9 and to_ind!=14 and from_ind<3:
        board_dist-=7
    # Start of fast lane reversed
    elif from_ind >9 and from_ind!=14 and to_ind<3:
        board_dist+=7
    # Seperate the two lanes
    elif (to_ind>9 and from_ind<10) or (from_ind>9 and to_ind<10):
        board_dist+=99
        
    if circle :
        # Fast lane circle
        if from_ind >9 and to_ind<3:
            board_dist+=15
        # Slow lane circle
        if from_ind<10 and to_ind<3:
            board_dist+=11
    board_dist= to_ind-from_ind

    prob = 1

    # Type of dice 
    trigger_prob=(dice-2)/2

    # cell cases
    if to_ind!=14 :
        if to_cell==1 or to_cell==2:
            prob*= (1-trigger_prob)
        elif (from_cell==1 and to_ind==0) or (from_cell==2 and board_dist==-3) or (from_cell==2 and to_ind==0 and from_ind<3):
            prob*= trigger_prob
            board_dist=0 # Guarantee to enter next condition
    
    # in reach of dice
    if board_dist<dice and board_dist>=0:
        if from_ind==2 and board_dist!=0:
            prob *= 0.5
        prob*= (1/dice)
    else :
        prob = 0

    return prob