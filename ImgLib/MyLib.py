# -*- coding: utf-8 -*-
# Important functions for  Seam-Paper
import numpy as np
from ImgLib.Poisson import poissonInsertMask, laplace_div


def absDivergence(img):
    '''
    Returns a function that adds the absolute values of the gradient.
    |di(x,y)/dx| + |di(x,y)/dy|
    @param img The Image
    @return Numpy array with the energy
    '''
    grad = np.gradient(img)
    return np.abs(grad[0]) + np.abs(grad[1])


def findOptimalSeam(s, stopFunc = None):
    """
    Finds optimal adjacent pixels in every row.
    These pixels minimize the energy s.
    @param s The energy function (a numpy array)
    @param stopFunc Function, stopFunc()==True stops the algorithm.
    @return A vector M. The size of its elements are equal to the size of s rows.
            The value M[i] gives the best column of the pixel at the row i.
            If it is impossible to return a seam that has not the energy infinity or if
            the algorithm has stopped, None will be returned.
    """
    M, N = s.shape
    C = np.zeros((M, N))
    Pointer = [[0 for x in range(0, N)] for y in range(0, M)]
    # Fill first row with 0
    for c in range(0, N):
        C[0, c] = s[0, c] 
    # Then compute for every column in every row the best neighbor above
    for r in range(1, M):  
        for c in range(N): 
            if (stopFunc and stopFunc()):
                return None
            left = max(c - 1, 0)  
            right = min(N - 1, c + 1) 
            j = left + C[r - 1, left:right + 1].argmin()  
            # Set the energy
            C[r, c] = C[r - 1, j] + s[r, c]  
            # Set the neighbor
            Pointer[r][c] = (r - 1, j)  
    # Find the way with the lowest energy
    minPointer = C[M - 1, :].argmin()
    if (C[M - 1, minPointer] == np.inf):
        return None
    # Creating the result
    seam = np.zeros(M, dtype=np.int)
    seam[M - 1] = minPointer
    minPointer = Pointer[M - 1][minPointer]
    for y in range(-M + 1, 0):
        prevR, row = minPointer
        seam[prevR] = row
        minPointer = Pointer[prevR][row]
    return seam


def findTopDisjointSeams(s, count, progressFunc=None, bigvalue=np.inf, stopFunc = None):
    """
      Tries to find a list of seams which are pairwise disjoint.
      In other words two seams, which do not have the same value in 
      the same row.
      Sometimes the algorithm cannot find as many disjoint seams as needed.
      In that case, the algorithm returns only the found disjoint seams. 
      @param s The energy numpy array 
      @param count the number of seams to find
      @param bigvalue A value to replace the energy on seams that are already found. (Used to find disjoint seams).
      @param stopFunc Function, if stopFunct()==True then the algorithm will stop.
      @return List of seams. [], if stopped.
    """
    (h, w) = s.shape
    shapes = []
    toAdd = [w * i for i in range(h)]

    def biggerSeam(seam, array):
        tmp = array.flatten()
        tmp[seam + toAdd] = bigvalue
        return tmp.reshape((h, w))

    for pack in range(count):
        if stopFunc and stopFunc():
            return []
        if (not progressFunc is None):
            progressFunc((pack + 1) * 100 / count)
        seam = findOptimalSeam(s, stopFunc)
        if (seam is None):
            break
        shapes.append(seam)
        s = biggerSeam(seam, s)
    return shapes


def defaultSeam(img):
    """
    Returns the seam that minimizes absDivergence.
    @param img The image (grayscale picture)
    @return Optimal seam.
    """
    img_div = absDivergence(img)
    return findOptimalSeam(img_div)


def removeSeams(img, seams):
    """
    Remove the seams in the image img.
    @param img The image
    @param seams a list of seams or just one.
    @return A image where the seams are removed.
    """
    if (type(seams) == np.ndarray):
        seams = [seams]
    def removeGray(img):
        h, w = img.shape
        toAdd = np.array([w * x for x in range(0, h)])
        toDelete = np.array([])
        for seam in seams:
            toDelete = np.append(toDelete, seam + toAdd)
        nimg = np.delete(img, toDelete)
        nimg.shape = (h, w - len(seams))
        return nimg
    if (type(seams) == np.ndarray):
        seams = [seams]
    if (np.ndim(img) == 3):
            h, w, p = img.shape
            toAdd = np.array([w * x for x in range(0, h)])
            toAppend = np.array([])
            for seam in seams:
                toAppend = np.append(toAppend, (seam + toAdd) * p)
            toDel = np.array([])
            for k in range(0, p):
                toDel = np.append(toDel, toAppend + k)
            nimg = np.delete(img, toDel)
            nimg.shape = (h, w - len(seams), p)
            return nimg
    else:
        return removeGray(img)


def removeSeamsInGradient(img, seams, it=20, mixCount=15, progressFunc = None, stopFunc = None):
    '''
    Removes seams from the gradient of the image img and reconstructs the result image
    from the gradient.
    @param img The image
    @param seams A list of seams or just one
    @param it Number of iterations used to solve the system of linear equations. 0 let solve the equations exactly.
    @param mixCount number of pixel that will be deleted around the seams and be mixed with the original picture.
    @param progressFunc A function for showing the progress. (int -> )
    @param stopFunc Function. Stops the algorithm when evaluated to true. (-> boolean)
    @return The reconstructed picture. None, if stopped.
    '''
    if (type(seams) == np.ndarray):
        seams = [seams]
    def removeGray(img, progressFunc):
        h, w = img.shape
        img_div = removeSeams(laplace_div(img), seams)
        img_rem = removeSeams(img, seams)
        mask = np.zeros((h, w))
        for seam in seams:
            for i in range(h):
                pos = seam[i]
                for k in range(-mixCount, mixCount):
                    if (stopFunc and stopFunc()):
                        return None
                    if (pos + k >= 0 and pos + k < w ):
                        if mask[i, pos + k] == 0:
                            mask[i, pos + k] = 1 - abs(k) * 1.0 / (mixCount + 1)
                        else:
                            mask[i, pos + k] = 1  
        mask = removeSeams(mask, seams)
        return poissonInsertMask(img_rem, mask, img_div, it, progressFunc, stopFunc)

    if (np.ndim(img) == 3):
        h, w, p = img.shape
        res = np.zeros((h, w - len(seams), p))
        nprogressFunc = None
        for i in range(p):
            if (progressFunc):
                nprogressFunc = lambda k: progressFunc(i*100/p+k/p)
            res[:, :, i] = removeGray(img[:, :, i], nprogressFunc)
        return res
    else:
        return removeGray(img, progressFunc)


def duplicateSeams(img, seams):
    """
      Duplicates and interpolates seams.
      @param img The Image
      @param seams the list of seams.
    """
    if (len(seams) == 0):
        return img
    def duplicateGray(img):
        h, w = img.shape
        toAdd = np.array([w * x for x in range(0, h)])
        res = np.array([])
        for seam in seams:
            res = np.concatenate((res, seam + toAdd))
        res = res.astype("int")
        not_edge_right = ((res+1)% w != 0).astype("int") # Points at the left edge of the image => do not interpolate left
        not_edge_left = (res% w != 0).astype("int") # Points at the right edge => do not interpolate right
        img = img.flatten()
        nimg = np.insert(img, res, img[res]/3+img[res-not_edge_left]/3+img[res+not_edge_right]/3)  
        nimg.shape = (h, w + len(seams))
        return nimg
    if (np.ndim(img) == 3):
        h, w, p = img.shape
        res = np.zeros((h, w + len(seams), p))
        for k in range(p):
            pic = img[:, :, k]
            pic = duplicateGray(pic)
            res[:, :, k] = pic  # 256-pic 
        return res
    else:
        return duplicateGray(img)


def resizeConventional(img, newWidth, newHeight):
    '''
    Scales the image with Nearest Neighbor
    @param img The image
    @param newWidth The new width (int)
    @param newHeight The new height (int)
    @return the scaled image
    '''

    def nearestNeighbour(img, y, x):
        return img[int(round(y)), int(round(x))]

    def resizeBW(img_g):
        h, w = img_g.shape
        res = np.zeros((newHeight, newWidth))
        factorH = h * 1.0 / newHeight
        factorW = w * 1.0 / newWidth
        for x in range(newWidth):
            for y in range(newHeight):
                res[y, x] = nearestNeighbour(img_g, factorH * y, factorW * x)
        return res

    if (np.ndim(img) == 2):
        return resizeBW(img)
    h, w, p = img.shape
    res = np.zeros((newHeight, newWidth, p))
    for i in range(p):
        res[:, :, i] = resizeBW(img[:, :, i])
    return res


def rotateMirror(img):
    '''
    Rotates the image and mirrors it. (Transposing)
    @param img The image
    @return the transposed image.
    '''
    if (np.ndim(img) == 3):
        h, w, p = img.shape
        res = np.zeros((w, h, p))
        for i in range(p):
            res[:, :, i] = img[:, :, i].transpose()
        return res
    return img.transpose()


def seamEnergy(energy, seam):
    '''
    Summarizes the energy of every pixel, which the seam contains.
    @param energy the energy function (numpy array)
    @param seam the seam
    @return the energy of the seam.
    '''
    h, w = energy.shape
    toAdd = [r * w for r in range(h)]
    return energy.flatten()[seam + toAdd].sum()


def retargetingImage(img, xCount, yCount, energyFactory, progressFunc=None, stopFunc = None):
    '''
    Retargeting the image with optimal seam order.
    Resizes the image by finding the optimal order for deleting vertically or horizontally.
    @param img The image
    @param xCount The number of column to delete.
    @param yCount The number of rows to delete.
    @param energyFactory A function computing the energy function (numpy array) of an image (numpy image -> numpy image)
    @param progressFunc Will be called if progress happens. (int ->)
    @param stopFunc  Function, if stopFunct()==True then the algorithm stops. (-> boolean)
    @return A image decreasing the width and height by xCount and yCount.
    '''
    h = img.shape[0]
    w = img.shape[1]
    costMatrix = np.zeros((yCount + 1, xCount + 1)) # Contains the cost of each step
    imageMatrix = [[None for x in range(xCount + 1)] for y in range(yCount + 1)] # Contains all calculated images
    imageMatrix[0][0] = img
    for y in range(yCount + 1):
        for x in range(xCount + 1):
            if (stopFunc and stopFunc()):
                return
            energyAbove = None #Energy by removing seam within image above in imageArray
            seamAbove = None # Seam for removing in the image above
            energyLeft = None # Energy by removing within image left
            seamLeft = None # Seam for that.
            if y > 0:
                img = rotateMirror(imageMatrix[y - 1][x]) # Calculate horizontal seam
                energyFunc = energyFactory(img)
                seamAbove = findOptimalSeam(energyFunc)
                energyAbove = costMatrix[y - 1, x] + seamEnergy(energyFunc, seamAbove)
            if x > 0:
                img = imageMatrix[y][x - 1] # Calculate vertical seam
                energyFunc = energyFactory(img)
                seamLeft = findOptimalSeam(energyFunc)
                energyLeft = costMatrix[y, x - 1] + seamEnergy(energyFunc, seamLeft)
            if (progressFunc):
                progressFunc((x + (y * (xCount + 1))) * 100 / ((xCount + 1) * (yCount + 1)))
            if ((not energyAbove is None and not energyLeft is None and energyAbove <= energyLeft) or (
                not energyAbove is None and energyLeft is None)): #  Better removing horizontal (less energy)
                costMatrix[y, x] = energyAbove 
                imageMatrix[y][x] = rotateMirror(removeSeams(rotateMirror(imageMatrix[y - 1][x]), seamAbove))
            elif ((not energyAbove is None and not energyLeft is None and energyAbove > energyLeft) or (
                not energyLeft is None and energyAbove is None)): # Better removing vertically
                costMatrix[y, x] = energyLeft
                imageMatrix[y][x] = removeSeams(imageMatrix[y][x - 1], seamLeft)
    return imageMatrix[yCount][xCount] 
