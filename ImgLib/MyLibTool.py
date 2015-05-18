# -*- coding: utf-8 -*-
import numpy as np
def makeGray(img):
    '''
    Converts a picture (may already gray) into a grayscale picture.
    @param img The picture (colored or gray)
    @return The grayscale picture
    '''
    img_g = img
    if (np.ndim(img) == 3):
        img_g = img[:, :, 1]
        for p in xrange(1, img.shape[2]):
            img_g = img_g + img[:, :, p]
        img_g = img_g / img.shape[2]
    return img_g

def seamsToRealIndex(shape,seams):
    '''
    Returns the indexes of the seams in a flatten image.
    @param shape the shape of the image where the indexes should be calculated with.
    @param seams A list of the seams
    @return An array of the indexes.
    '''
    h,w = shape
    allSeams = np.array([])
    toAdd = np.array([w*x for x in xrange(h)])
    for seam in seams:
        allSeams = np.append(allSeams,seam+toAdd)
    return allSeams.astype(np.int)

def drawSeamsInImage(img, seams):
    '''
    Draws the seams into the picture
    @param img The picture
    @param seams The seams
    @return The picture where the seams are drawn in.
    '''

    def drawSeamGray(imgB, seamsB):
        h, w = imgB.shape
        allSeams = seamsToRealIndex(imgB.shape,seamsB)
        imgR = imgB.flatten()
        imgR[allSeams] = 255 - imgR[allSeams]
        imgR.shape = (h, w)
        return imgR

    if (np.ndim(img) == 3):
        h, w, p = img.shape
        res = img.copy()
        for i in xrange(p):
            res[:, :, i] = drawSeamGray(img[:, :, i], seams)
        return res
    return drawSeamGray(img, seams)