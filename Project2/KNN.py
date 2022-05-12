import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn import neighbors
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

def read(filepath):
    '''Function that reads a file at the given filepath and returns the informations
    in a dataframe  '''
    try:
        df = pd.DataFrame(columns=['number', 'id', 'time_sequence'])
        lines = [line.strip() for line in open(filepath,'r')]
        number = int(lines[1].split(" ")[3])
        id = int(lines[2].split(" ")[3])
        matrix = []
        for i in range(5,len(lines)):
            line = lines[i].split(",")
            line = np.array(line).astype(np.float64)
            matrix.append([*line[:3]])
        matrix=StandardScaler().fit_transform(matrix)
        
        df.loc[0] = [number, id, matrix]
        return df
    except IOError as e:
        print("Unable to read dataset file!\n")

directory = 'Sketch-Data-master\SketchData\SketchData\Domain01'


def cross_validation_split():
    '''Function to separate the train and test set based on the users'''
    dataset_split = []
    for i in range(10):
        fold=[x for x in range(100*i, 100*(i+1))]
        other=[x for x in range(1000) if x not in fold]
        dataset_split+=[(fold,other)]
    return dataset_split

def DTWdistance(data1,data2, w):
    '''Function that compute the Dynamic Time Wraping distance between
    two samples. Algorithm found on https://en.wikipedia.org/wiki/Dynamic_time_warping'''
    n=len(data1)
    m=len(data2)
    data2=StandardScaler().fit_transform(data2)

    DTW=np.zeros((n,m))
    w=max(w,abs(n-m))

    for i in range(n):
        for j in range(m):
            DTW[i,j]=np.inf
    DTW[0,0]=0

    for i in range(1,n):
        for j in range(max(1,i-w),min(m,i+w)):
            DTW[i,j]=0
    
    for i in range(1,n):
        for j in range(max(1,i-w),min(m,i+w)):
            cost=distance(data1[i],data2[j])
            DTW[i,j]=cost+np.min([DTW[i-1,j],#insertion
                                DTW[i,j-1],#deletion
                                DTW[i-1,j-1]])#match
    
    return DTW[n-1,m-1]

def distance(a,b):
    '''Function to compute the distance between to vectors as d=|a-b|'''
    return np.linalg.norm(np.absolute(np.array(a)-np.array(b)))

def dist_matrix(x):
    '''Compute the distance between all samples of x 
    and return the matrix of those distances'''
    dist_m = np.zeros((x.shape[0],x.shape[0]))
    for i in range(x.shape[0]):
        for j in range(i+1,x.shape[0]):
            dist_m[i,j]=DTWdistance(x[i],x[j],100)
            dist_m[j,i]=dist_m[i,j]
        if i%50==0:
            print(i/10, "%")
    return dist_m

#Reading all the files and puting themn in a dataframe
df = pd.DataFrame(columns=['number', 'id', 'time_sequence'])
for filename in range(1,1001):
    f = os.path.join(directory, str(filename)+".txt")
    # checking if it is a file
    if os.path.isfile(f):
        df=pd.concat([df,read(f)], ignore_index=True)

''' Decomment the 3 next lines to recompute the distance matrix'''
#X = df["time_sequence"].array
#X=dist_matrix(X)
#np.savetxt("dist_matrix2.csv",X,delimiter=",")

X=np.genfromtxt("dist_matrix2.csv",delimiter=",")
for i in range(len(X)):
    for j in range(len(X[i])):
        if(X[i,j]==np.inf):
            X[i,j]=99999999
y = np.array(df["number"].array,dtype=float)


'''KNearest Neighbors cross-validation'''
n_neighbors = 5

# we only take the first two features. We could avoid this ugly
# slicing by using a two-dim dataset

scores_KNN=[]
scores_SVC=[]
conf_matrix_KNN=np.zeros((10,10))
conf_matrix_SVC=np.zeros((10,10))
for test_ind, train_ind in cross_validation_split():
    x_train, y_train = X[train_ind], y[train_ind]
    x_train=x_train[:,train_ind]
    x_test, y_test = X[test_ind], y[test_ind]
    x_test=x_test[:,train_ind]

    clf = neighbors.KNeighborsClassifier(n_neighbors, metric="precomputed")
    clf.fit(x_train, y_train)
    scores_KNN+=[clf.score(x_test,y_test)]
    conf_matrix_KNN+=confusion_matrix(y_test,clf.predict(x_test))

    sv=SVC(kernel='precomputed',C=1000, gamma='auto')
    sv.fit(x_train,y_train)
    scores_SVC+=[sv.score(x_test,y_test)]
    conf_matrix_SVC+=confusion_matrix(y_test,sv.predict(x_test))

print("Average accuracy KNN = "+str(np.mean(scores_KNN)))
print("Standard Deviation KNN = "+str(np.std(scores_KNN)))
print("Median KNN = "+str(np.median(scores_KNN)))
print(scores_KNN)
disp=ConfusionMatrixDisplay(conf_matrix_KNN)
disp.plot()

print("Average accuracy SVC = "+str(np.mean(scores_SVC)))
print("Standard Deviation SVC = "+str(np.std(scores_SVC)))
print("Median KNN = "+str(np.median(scores_SVC)))
print(scores_SVC)
disp=ConfusionMatrixDisplay(conf_matrix_SVC)
disp.plot()