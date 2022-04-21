import numpy as np
import pandas as pd
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
            matrix.append(list(line[3]+line[:3]))
        df.loc[0] = [number, id, matrix]
        print(type(matrix))
        return df
    except IOError as e:
        print("Unable to read dataset file!\n")

read("Project2\Sketch-Data-master\SketchData\SketchData\Domain01\833.txt").to_csv("Dataframe")
