import numpy as np
import pandas as pd
import os

def read(filepath):
    try:
        df = pd.DataFrame(columns=['number', 'id', 'time_sequence'])
        lines = [line.strip() for line in open(filepath,'r')]
        number = int(lines[1].split(" ")[3])
        id = int(lines[2].split(" ")[3])
        matrix = []
        for i in range(5,len(lines)):
            line = lines[i].split(",")
            line = np.array(line).astype(np.float64)
            matrix.append([line[3], *line[:3]])
        df.loc[0] = [number, id, matrix]
        return df
    except IOError as e:
        print("Unable to read dataset file!\n")
df = read("Sketch-Data-master\SketchData\SketchData\Domain01\833.txt")

directory = 'Sketch-Data-master\SketchData\SketchData\Domain01'
 
# iterate over files in
# that directory
df = pd.DataFrame(columns=['number', 'id', 'time_sequence'])
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        df.append(read(f))