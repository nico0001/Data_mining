import numpy as np

# Markov decision using value iteration process
def markovDecision(layout,circle) :
    tol=10**-15
    nb_epoch=9999
    expec = np.zeros(15)
    trans_matrix=transition_matrix(layout,circle)
    delta = v_star(layout,expec,trans_matrix)
    k=0
    while delta > tol and k<nb_epoch:
        delta=v_star(layout,expec,trans_matrix)
        k+=1
    dices = get_dices(layout,expec,trans_matrix)
    return [expec[:14],dices[:14]]

# Update the expected values and returns the worst accuracy improvement
def v_star(layout,expec,trans_matrix):
    delta = 0
    for i in range(len(layout)-1) :
        temp = expec[i]
        v_list = np.zeros(3)
        for d in range(3) :
            a = trans_matrix[d,i,:]
            for j in np.where(a!=0)[0]:
                p = trans_matrix[d,i,j]
                v_list[d]+=p*(expec[j] + cost(layout,i,j,d,trans_matrix))
        expec[i] = min(v_list)
        delta = max(delta, abs(temp - expec[i]))
    return delta

# Returns the best dices
def get_dices(layout,expec,trans_matrix):
    dices = np.zeros(len(layout))
    for i in range(len(layout)):
        v_list = np.zeros(3)
        for d in range(3):
            a = trans_matrix[d,i,:]
            for j in np.where(a!=0)[0]:
                p = trans_matrix[d,i,j]
                v_list[d]+=p*(expec[j] + cost(layout,i,j,d,trans_matrix))
        min_index = 0
        min_val = min(v_list)
        for d in range(3):
            if v_list[d] == min_val:
                min_index=d
        dices[i] = min_index+1
    return dices.astype(int)

# Compute the transition matrix containing the probability relation between cells
def transition_matrix(layout,circle):
    trans=np.zeros((3,len(layout), len(layout)))
    for d in range(3):
        for i in range(len(layout)):
            for j in range(len(layout)):
                trans[d,i,j]=prob_from_cell_to_cell(layout,i,j,d+2,circle)
    return trans

# Returns the cost for two cells and an action
def cost(layout,from_ind,to_ind,d,trans_matrix):
    cell = layout[to_ind]
    c = 1
    if from_ind<=to_ind :
        if cell==3:
            c+=d/2
        elif cell==4:
            c-=d/2
        # If cell(s) can move you back to a jail or retry
        # adjust the cost by the proportion of the total prob_from_cell_to_cell
        if from_ind==to_ind and (cell==3 or cell==4) and d==2:
            proportion = 1/4/trans_matrix[d,from_ind,to_ind]
            c*= proportion
            compensation = 0
            if from_ind==2:
                proportion/=2
                if from_ind+10<13 and layout[from_ind+10]==2:
                    compensation += proportion
            if from_ind+3<14 and layout[from_ind+3]==2 and (from_ind+3<10 or from_ind>9):
                compensation += proportion
            
            c = c +compensation
    return c



# Returns the probability to reach a cell from another using a certain dice
def prob_from_cell_to_cell(layout,from_state,to_state,dice,circle):
    
    from_ind = from_state
    to_ind,to_cell = to_state,layout[to_state]

    # No prob from goal
    if from_ind==14:
        if to_ind==14:
            return 1
        return 0
    
    board_dist = board_distance(from_state,to_state,circle)
        
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
            if from_ind<10 and from_ind>7 and reachable_state>11:
                reachable_state -= 11
            elif from_ind==13 and reachable_state>15:
                reachable_state -= 15
            
        if(from_state==to_ind) and dist==3 and reachable_state==1:
            reachable_state=-1
        if ((reachable_state<14 and from_ind>9) or (reachable_state<10 and from_ind<10)) and reachable_state>=0:
            if from_ind==2 and dist!=0:
                prob+=0.5*add_prob_move(layout,reachable_state,to_ind,dice,board_dist-dist)
                prob+=0.5*add_prob_move(layout,reachable_state+7,to_ind,dice,board_dist-dist)
            else:
                prob+=add_prob_move(layout,reachable_state,to_ind,dice,board_dist-dist)
    return prob

# Computes the distance between two cells on the board
def board_distance(from_ind,to_ind,circle):

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
        else : board_dist+=7
    # Circle slow lane
    elif circle and board_dist+11<4 and from_ind<10 and from_ind>7 and to_ind<3:
            board_dist+=11
    # Seperate the two lanes
    elif (to_ind>9 and from_ind<10) or (from_ind>9 and to_ind<10):
        board_dist+=99
    return board_dist

# Probality of being moved to a cell
def add_prob_move(layout,reachable_state,to_ind,dice,board_dist):
    if (to_ind==0 and layout[reachable_state]==1) or (((board_dist==-3) or (to_ind==0 and reachable_state<3)) 
    and layout[reachable_state]==2):
        return (dice-2)/2/dice
    return 0