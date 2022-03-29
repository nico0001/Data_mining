from markov import *
import matplotlib.pyplot as plt

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

instances = ["i01","i02","i03","i04","i05", "i07"]
expec=[]
empirical=[]
turns=[]
diff=[]
#layout = gen_layout()
for inst in instances:
    layout,circle = (read_instance(inst))
    strat = markovDecision(layout,circle)
    expec+=[strat[0][0]]
    turn_lst = []
    for i in range(10000):
        nb_turns = apply_strat(layout,circle,strat)
        turn_lst.append(nb_turns)
    empirical+=[np.mean(turn_lst)]
    diff+=[abs(np.mean(turn_lst)-strat[0][0])]
    turns+=[turn_lst]
        # finding the 1st quartile
    q1 = np.quantile(turn_lst, 0.25)
     
    # finding the 3rd quartile
    q3 = np.quantile(turn_lst, 0.75)
    med = np.median(turn_lst)
     
    # finding the iqr region
    iqr = q3-q1
    
    
    # finding upper and lower whiskers
    upper_bound = q3+(1.5*iqr)
    lower_bound = q1-(1.5*iqr)
    print(iqr, upper_bound, lower_bound)
    outliers = np.where((turn_lst < lower_bound) | (turn_lst> upper_bound))
    print(len(outliers[0])*100/10000)
    

layout=gen_layout()
strat = markovDecision(layout,circle)
expec+=[strat[0][0]]
turn_lst = []
for i in range(10000):
    nb_turns = apply_strat(layout,circle,strat)
    turn_lst.append(nb_turns)
empirical+=[np.mean(turn_lst)]
diff+=[abs(np.mean(turn_lst)-strat[0][0])]
turns+=[turn_lst]



'''print(np.std(turn_lst))
print("expected cost =",np.mean(turn_lst))
if abs(np.mean(turn_lst)-strat[0][0])>0.05:
    1/0'''
plt.boxplot(turns, labels=("Normal","Restart","Penalty","Prison","Bonus","Handmade", "Random"))
plt.plot(range(1,8), expec, label="Theoretical expected cost")
plt.xticks(rotation=45)
plt.xlabel("Type of layout")
plt.ylabel("Number of turns")
plt.legend()
plt.title("Comparison of the theoritical expected cost \n and the empirical average cost on 10000 games")
plt.show()
plt.plot(range(7), diff)