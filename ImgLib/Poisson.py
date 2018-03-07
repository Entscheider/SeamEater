# -*- coding: utf-8 -*-
# Functions  for Poisson-Reconstruction
import numpy as np
from ImgLib.MyFilter import myfilter as filter
# Some explanations: http://eric-yuan.me/poisson-blending/

def jacobi(A, b, N=25, x=None, progressFunc = None, stopFunc=None):
    """
      Solving A*x =b for x by using the Jacobi-method.
      @param A The Matrix
      @param b The solution A*x=b
      @param N the iterations for solving.
      @param x A guess value for beginning.
      @param progressFunc A function for showing the progress.
      @param stopFunc Function. Stopping when evaluated to true
      @return The solution x
    """
    # Create an initial guess if needed
    if x is None:
        x = np.zeros(len(A[0]))
    # Create a vector of the diagonal elements of A
    # and subtract them from A
    D = np.diag(A)
    R = A - np.diagflat(D)
    # Iterate for N times
    for i in range(N):
        if (progressFunc):
            progressFunc(i*100/N)
        if stopFunc and stopFunc():
            return x
        x = (b - np.dot(R, x)) / D
    return x


def laplace_div(array):
    '''
    Calculating the Laplace derivative
    @param array The Image
    @return The numpy array of the Laplace derivative
    '''
    kern=-np.array([[0,1,0],[1,-4,1],[0,1,0]])
    return filter(array,kern)


# Inspired by http://pebbie.wordpress.com/2012/04/04/python-poisson-image-editing/
def poissonInsertMask(m, mask, div, iterations=20, progressFunc = None, stopFunc=None):
    '''
    Computes from the Laplace derivative div and the picture m 
    a new picture. That picture blends them together using Poisson.
    @param m The target picture
    @param mask mask[x,y]=1 => Reconstruct this pixel.
                mask[x,y]=0 => Use the value from m for this pixel
                0<mask[x,y]<1 => Mix both picture
    @param div The Laplace derivative for reconstruction. (numpy Array)
    @param iterations Number of iteration for solving the linear system of equations.
            iterations <=0 => Use the exact solution
    @param progressFunc A function for showing the progress.
    @param stopFunc Function. Stopping when evaluated to true
    @return the reconstructed picture.
    '''
    h, w = mask.shape
    r, c = mask.nonzero()  
    N = len(r)
    idx = np.zeros(mask.shape, dtype=np.uint32)

    for i in range(N):
        idx.itemset((r.item(i), c.item(i)), i + 1)

    b_r = np.zeros(N)

    A = np.zeros((N, N))
    for i in range(N):
        if (progressFunc):
            progressFunc(i*100//(2*N))
        if stopFunc and stopFunc():
            return
        y, x = r.item(i), c.item(i)  
        b_r.itemset(i, div.item((y, x)))  
        p = i 
        Np = 0
        if y > 0 and mask.item((y - 1, x)):  
            q = idx.item((y - 1, x)) - 1  
            A[p, q] = -1. 
            Np += 1  
        if x > 0 and mask.item((y, x - 1)):  
            q = idx.item((y, x - 1)) - 1  
            A[p, q] = -1.
            Np += 1
        if y < h - 1 and mask.item((y + 1, x)): 
            q = idx.item((y + 1, x)) - 1
            A[p, q] = -1.
            Np += 1
        if x < w - 1 and mask.item((y, x + 1)):  
            q = idx.item((y, x + 1)) - 1
            A[p, q] = -1
            Np += 1
        A[p, p] = Np * 1.  
    guess = None
    x = 0
    if (iterations <= 0):
        x = np.linalg.solve(A,b_r).astype("uint8")
    else: 
        if (progressFunc):
            x = jacobi(A, b_r, x=guess, N=iterations, progressFunc = lambda k:progressFunc(50+k/2),  stopFunc = stopFunc)  
        else:
            x = jacobi(A, b_r, x=guess, N=iterations,  stopFunc = stopFunc) 
    if stopFunc and stopFunc():
        return None
    for i in range(N):
        yy, xx = r.item(i), c.item(i)
        v = m[yy, xx] - x[i]  
        
        if v < 0:
            v = 0
        elif v > 255:
            v = 255
        
        if (iterations >0): # mixing
          m[yy, xx] = v * mask[yy, xx] + m[yy, xx] * (1 - mask[yy, xx])
        else: # no mixing needed ?!
          m[yy, xx] = v
    return m
