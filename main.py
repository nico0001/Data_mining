from markov import *

def apply_strat(layout,circle,strat, epoch=99999) :
    nb_turns=0
    dice = strat[1]
    curr_pos = 0
    finished = False
    fast_lane = False
    print(circle)

    while nb_turns<epoch and not finished :
        # Throw the dice
        curr_dice = dice[curr_pos]+1
        move = np.random.randint(curr_dice)

        # Fast lane ?
        if curr_pos==2 :
            fast_lane = bool(np.random.randint(2))
            if fast_lane and move!=0 :
                curr_pos+=7
        curr_pos+=move
        nb_turns+=1

        # The end ?
        if curr_pos>=14 or ((not fast_lane) and curr_pos>=10):
            if (not circle) or curr_pos==14 or curr_pos==10:
                finished = True
            else :
                if fast_lane : 
                    curr_pos=curr_pos%14-1
                    fast_lane = False
                else : curr_pos=curr_pos%10-1

        # Type of dice 
        prob=False
        if curr_dice==3 :
            prob = bool(np.random.randint(2))
        elif curr_dice==4 :
            prob = True

        # Effect of cell
        if prob and not finished :
            cell = layout[curr_pos]
            if cell==1:
                curr_pos=0
                fast_lane=False
            elif cell==2:
                curr_pos-=3
                if fast_lane and curr_pos <=9:
                    curr_pos-=7
                    fast_lane = False
                elif curr_pos<0:curr_pos=0
            elif cell==3:
                nb_turns+=1
            elif cell==4:
                nb_turns-=1
    #if not finished : return 0
    return nb_turns

def read_instance(path) :
    with open("instances/"+path, 'r') as f:
            lines = f.readlines()
    layout = list(map(lambda x: int(x), lines[0].strip()))
    circle = bool(int(lines[1]))
    return layout,circle

instances = ["i01","i02","i03","i04","i05"]
layout,circle = (read_instance(instances[4]))
strat = markovDecision(layout,circle)
print(strat)
#strat[1] = np.array([4,4,4,4,4,4,4,4,4,4,4,4,4,4])
#strat[1] = np.array([2,2,2,2,2,2,2,2,2,2,2,2,2,2])
nb_turns = apply_strat(layout,circle,strat)
print(nb_turns)