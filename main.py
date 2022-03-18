from markov import *

def apply_strat(layout,circle,strat, epoch=99999) :
    nb_turns=0
    dice = strat[1]
    curr_pos = 0
    finished = False
    fast_lane = False

    while nb_turns<epoch and not finished :
        
        # Throw the dice
        curr_dice = dice[curr_pos]+1
        move = np.random.randint(curr_dice)
        #print(curr_pos, move, curr_dice-1)
        # Fast lane ?
        if curr_pos==2 :
            fast_lane = bool(np.random.randint(2))
            if fast_lane and move!=0 :
                curr_pos+=7
        #print("fast_lane=",fast_lane)
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
        #print("prob =",prob)
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
                if curr_pos<0:curr_pos=0
            elif cell==3:
                nb_turns+=1
            elif cell==4:
                nb_turns-=1
        #print("turn=",nb_turns)
    #if not finished : return 0
    return nb_turns

def gen_layout():
    layout = [0] * 15
    for i in range(1, 14):
        if bool(np.random.randint(2)):
            layout[i] = np.random.randint(1, 5)
    return layout

def read_instance(path) :
    with open("instances/"+path, 'r') as f:
            lines = f.readlines()
    layout = list(map(lambda x: int(x), lines[0].strip()))
    circle = bool(int(lines[1]))
    return layout,circle

instances = ["i01","i02","i03","i04","i05","i06","i07"]
layout,circle = (read_instance(instances[5]))
layout = gen_layout()
strat = markovDecision(layout,circle)
print(layout, circle)
print(strat)
#strat[1] = np.array([4,4,4,4,4,4,4,4,4,4,4,4,4,4])
#strat[1] = np.array([2,2,2,2,2,2,2,2,2,2,2,2,2,2])
turn_lst = []
for i in range(10000):
    nb_turns = apply_strat(layout,circle,strat)
    turn_lst.append(nb_turns)
print(np.std(turn_lst))
print("expected cost =",np.mean(turn_lst))
if abs(np.mean(turn_lst)-strat[0][0])>0.05:
    1/0