import numpy as np
from math import *

def DTWdistance(data1,data2, w):
    n=len(data1)
    m=len(data2)
    DTW=np.zeros((n,m))
    w=max(w,abs(n-m))

    for i in range(n):
        for j in range(m):
            DTW[i,j]=999999
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
    
    return DTW[n,m]

def distance(a,b):
    return np.linalg.norm(a-b)