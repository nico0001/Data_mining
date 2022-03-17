import numpy as np

def markovDecision(layout,circle,tol=0.0001,nb_epoch=9999) :
    expec = np.zeros(15)
    trans_matrix=transition_matrix(layout,circle)
    for line in trans_matrix:
        print(line)
    delta = v_star(layout,expec,trans_matrix)
    k=0
    while delta > tol and k<nb_epoch:
        delta=v_star(layout,expec,trans_matrix)
        k+=1
        #print("delta=",delta)
    dices = get_dices(layout,expec,trans_matrix)
    print(k)
    return [expec[:14],dices[:14]]

def v_star(layout,expec,trans_matrix):
    delta = 0
    for i in range(len(layout)-1) :
        temp = expec[i]
        v_list = np.zeros(3)
        for d in range(3) :
            a = trans_matrix[d,i,:]
            sum = 0
            for j in np.where(a!=0)[0]:
                p = trans_matrix[d,i,j]
                sum += p*expec[j]
            v_list[d] = 1 + sum
        expec[i] = min(v_list)
        delta = max(delta, abs(temp - expec[i]))
    return delta

def get_dices(layout,expec,trans_matrix):
        dices = np.zeros(len(layout))
        for i in range(len(layout)):
            v_list = np.zeros(3)
            for d in range(3):
                a = trans_matrix[d,i,:]
                sum = 0
                for j in np.where(a!=0)[0]:
                    p = trans_matrix[d,i,j]
                    sum+=p*expec[j]
                v_list[d] = 1 + sum
            min_index = 0
            min_val = np.min(v_list)
            for d in range(3):
                if v_list[d] == min_val:
                    min_index=d
            dices[i] = min_index+1
        return dices.astype(int)
       

def prob_from_cell_to_cell(layout,from_state,to_state,dice,circle):
    
    from_ind,from_cell = from_state,layout[from_state]
    to_ind,to_cell = to_state,layout[to_state]

    # No prob from goal
    if from_ind==14:
        if to_ind==14:
            return 1
        return 0
    
    board_dist = to_ind-from_ind
    # End of slow lane
    if to_ind==14 and from_ind<10:
        board_dist-=4
    # Start of fast lane
    elif to_ind >9 and to_ind!=14 and from_ind==2:
        board_dist-=7
    # Start of fast lane reversed
    elif from_ind >9 and to_ind<3 and from_cell==2:
        board_dist+=7
    # Seperate the two lanes
    elif (to_ind>9 and from_ind<10) or (from_ind>9 and to_ind<10):
        board_dist+=99
        
    prob = 1

    # Type of dice 
    trigger_prob=(dice-2)/2

    # cell cases
    if to_ind!=14 and dice!=2:
        if to_cell==1 or to_cell==2:
            prob*= (1-trigger_prob)
        # TODO Add the prob for the reachable cells
        '''elif (from_cell==1 and to_ind==0) or (from_cell==2 and board_dist==-3) or (from_cell==2 and to_ind==0 and from_ind<3):
            prob*= trigger_prob
            board_dist=0 # Guarantee to enter next condition'''
        
        
    #End of game when no circle
    if not circle and to_ind==14:
        if board_dist<3:
            prob = prob*(dice-board_dist)
    
    # in reach of dice
    if board_dist<dice and board_dist>=0:
        if from_ind==2 and board_dist!=0:
            prob *= 0.5
        prob*= (1/dice)
    else :
        prob = 0
    
    prob_circle = 0
    if circle :
        
        board_dist = to_ind-from_ind
    
        # Fast lane circle
        if from_ind >9 and to_ind<3:
            board_dist+=15
            prob_circle = 1
        # Slow lane circle
        elif from_ind<10 and to_ind<3:
            board_dist+=11
            prob_circle = 1
        
        # in reach of dice
        if board_dist<dice and board_dist>=0:
            if from_ind==2 and board_dist!=0:
                prob_circle *= 0.5
            prob_circle*= (1/dice)
        else :
            prob_circle = 0

    return prob + prob_circle

def transition_matrix(layout,circle):
    trans=np.zeros((3,len(layout), len(layout)))
    for d in range(3):
        for i in range(len(layout)):
            for j in range(len(layout)):
                trans[d,i,j]=prob_from_cell_to_cell(layout,i,j,d+2,circle)
    return trans
