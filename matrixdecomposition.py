# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 12:17:57 2012

@author: Fela Winkelmolen
"""


import scipy as sp
import scipy.linalg
from matrixgeneration import *

"""
Decomposes an optionally incomplete matrix, into two components, one low rank, and one sparse. It takes the following arguments:
    Y: The matrix to decompose. It is supposed that Y is equal to TH + GA + W, where TH is an approximately low rank matrix, GA is a sparse "spiky" matrix, and W is noise. A full matrix needs to be given, but some parts can be ignored, as specified by the mask.
    Mask: A mask can be given to treat the matrix as incomplete. It must be of the same dimentions as Y. It must have 0 or False in the positions where Y is incomplete, 1 or True elsewhere. Defaults to None.
    lambda_d: regularization paramater for the low rank TH matrix.
    mu_d: regularization parameter for the sparse GA matrix. Use higher values if no spikes are expected.
    alpha: parameter that limits the maximum element of the low rank TH matrix. Bigger matrices will need a bigger alpha values.

It will return TH and GA.
"""
def matrix_decomposition(Y, Mask=None, lambda_d=0.025, mu_d=0.005, alpha=20, max_iterations=1000):
    # default value
    if Mask == None:        
        Mask = Y*0+1
    t = 1.0
    TH = GA = TH_last = GA_last = Y * 0.0 # theta and gamma
    for k in range(0, max_iterations):
        t_last = t
        #print (t_last - 1)/t
        t = ( 1.0 + sp.sqrt(1 + 4 * t**2) )/ 2.0
        #print (t_last - 1)/t
        Z = TH + (t_last - 1)/t*(TH-TH_last)
        N = GA + (t_last - 1)/t*(GA-GA_last)
        lambd = 0.5 # TODO: check
        f = ((Z+N) - Y) * 0.5
        first = Z - f*Mask
        second = N - f*Mask
        TH_last, GA_last = TH, GA
        TH, GA = prox_g([first, second], lambd, lambda_d, mu_d, alpha)
        if sp.sqrt(((TH - TH_last)**2).sum()) + sp.sqrt(((GA - GA_last)**2).sum()) < 1e-2:
            print k, "iterations"
            break
    return [TH, GA]

def prox_g(grad, lambd, lambda_d, mu_d, alpha):
    N, Z = grad
    
    X = N
    P = Q = N*0.0
    for i in range(0, 500): # TODO: how many iterations?
        Y = prox1(X+P, lambda_d, lambd)
        P = X + P - Y
        X_last = X
        X = prox2(Y+Q, alpha)
        Q = Y + Q - X
        if sp.sqrt(((X - X_last)**2).sum()) < 1e-4:
            break
    V = X
    
    # soft thresholding
    W = soft_threshold(Z, mu_d*lambd)
    return [V, W]

# projection of nuclear norm
def prox1(X, lambda_d, lambd):
    U, s, Vh = sp.linalg.svd(X)
    d1, d2 = X.shape
    E = sp.linalg.diagsvd(s, d1, d2) # sigma 
    S = soft_threshold(E, lambda_d*lambd)
    return U.dot(S.dot(Vh))

# projection in Q
def prox2(X, alpha):
    limit = alpha / sp.sqrt(sp.array(X.shape).prod())
    X = sp.minimum(X, limit)
    X = sp.maximum(X, -limit)
    return X

def soft_threshold(X, s):
    return (X-s)*(X>s) + (X+s)*(X<-s)

#sp.random.seed(0)
#size = 30
#TH = low_rank(size, 3)
#GA = spiky(size)
#Y = TH + GA
#X = selection(size, 0.)
#A, B = matrix_decomposition(Y*X, Mask=X)
#print X[1, :]
#print TH[1, :]
#print A[1, :]
#print GA[1, :]
#print B[1, :]
