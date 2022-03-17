import numpy as np

def markovDecision(layout,circle,tol=0.00000001,nb_epoch=9999) :
    expec = np.zeros(15)
    trans_matrix=transition_matrix(layout,circle)
    '''for line in trans_matrix:
        print(line)'''
    delta = v_star(layout,expec,trans_matrix)
    k=0
    while delta > tol and k<nb_epoch:
        delta=v_star(layout,expec,trans_matrix)
        k+=1
        #print("delta=",delta)
    dices = get_dices(layout,expec,trans_matrix)
    #print(k)
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
                sum+=p*(expec[j] + cost(layout[j],d))
                v_list[d] = sum
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
                    sum+=p*(expec[j] + cost(layout[j],d))
                v_list[d] = sum
            min_index = 0
            min_val = np.min(v_list)
            for d in range(3):
                if v_list[d] == min_val:
                    min_index=d
            dices[i] = min_index+1
        return dices.astype(int)
       
def transition_matrix(layout,circle):
    trans=np.zeros((3,len(layout), len(layout)))
    for d in range(3):
        for i in range(len(layout)):
            for j in range(len(layout)):
                trans[d,i,j]=prob_from_cell_to_cell(layout,i,j,d+2,circle)
    return trans

def cost(cell,d):
    if cell==3:
        return 1+d/2
    if cell==4:
        return 1-d/2
    return 1




def prob_from_cell_to_cell(layout,from_state,to_state,dice,circle):
    
    from_ind = from_state
    to_ind,to_cell = to_state,layout[to_state]

    # No prob from goal
    if from_ind==14:
        if to_ind==14:
            return 1
        return 0
    
    board_dist = board_distance(layout,from_state,to_state,circle)
        
    prob = 1

    # Type of dice 
    trigger_prob=(dice-2)/2

    # cell cases
    if to_ind!=14:
        if to_cell==1 or to_cell==2:
            prob*= (1-trigger_prob)
           
    # End of game when no circle
    if not circle and to_ind==14 and board_dist<3:
        prob *= (dice-board_dist)
    
    # in reach of dice
    if board_dist<dice and board_dist>=0:
        if from_ind==2 and board_dist!=0:
            prob *= 0.5
        prob*= (1/dice)
    else :
        prob = 0

    # Add cases where we are being moved
    for dist in range(dice) :
        reachable_state = from_state+dist
        if circle:
            if from_ind<10 and from_ind>7:
                reachable_state -= 11
            elif from_ind==13:
                reachable_state -= 15
        if (reachable_state<14 and from_ind>9) or (reachable_state<10 and from_ind<10):
            if from_ind==2:
                prob+=0.5*add_prob_move(layout,reachable_state,to_ind,dice,board_dist-dist)
                prob+=0.5*add_prob_move(layout,reachable_state+7,to_ind,dice,board_dist-dist)
            else:
                prob+=add_prob_move(layout,reachable_state,to_ind,dice,board_dist-dist)
    
    return prob

def board_distance(layout,from_state,to_state,circle):
    from_ind,from_cell = from_state,layout[from_state]
    to_ind = to_state

    board_dist = to_ind-from_ind
    # End of slow lane
    if to_ind==14 and from_ind<10:
        board_dist-=4
    # Start of fast lane
    elif to_ind >9 and to_ind!=14 and from_ind==2:
        board_dist-=7
    # Fast lane reversed or circle
    elif from_ind >9 and to_ind<3:
        # Circle fast lane
        if board_dist+15<4 and circle: board_dist+=15
        # Start of fast lane reversed
        elif from_cell==2: board_dist+=7
        else : board_dist+=99
    # Circle slow lane
    elif circle and board_dist+11<4 and from_ind<10 and from_ind>7 and to_ind<3:
            board_dist+=11
    # Seperate the two lanes
    elif (to_ind>9 and from_ind<10) or (from_ind>9 and to_ind<10):
        board_dist+=99
    return board_dist

def add_prob_move(layout,reachable_state,to_ind,dice,board_dist):
    if (to_ind==0 and layout[reachable_state]==1) or (((board_dist==-3) or (to_ind==0 and reachable_state<3)) 
    and layout[reachable_state]==2):
        return (dice-2)/2/dice
    return 0