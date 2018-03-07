# -*- coding: utf-8 -*-
import ImgLib.MyLib as ML
from ImgLib.MyLibTool import makeGray as __makeGray
import numpy as np
withCV2 = True
try:
    import cv2
except:
    withCV2 = False
from ImgLib.Poisson import laplace_div

# A collection of energy factories

def absEnergyFunc(img):
    '''
    Returns a function that adds the absolute values of the gradient.
    |di(x,y)/dx| + |di(x,y)/dy|
    @param img The Image
    @return Numpy array with the energy
    '''
    img_g = __makeGray(img)
    return ML.absDivergence(img_g)   # L1-Gradient-Norm


def cornerHarrisFunc(img):
    '''
    Calculates the energy with Corner Harris.   
    @param img The Image
    @return Numpy array with the energy
    '''
    img_g = __makeGray(img).astype("uint8")
    return cv2.cornerHarris(img_g, 2, 3, 0.04)


def preCornerDetectFunc(img):
    '''
    Calculates the energy by using pre corner detection
    @param img The Image
    @return Numpy array with the energy
    '''
    img_g = __makeGray(img).astype("uint8")
    return cv2.preCornerDetect(img_g, 5)

def l2gradientFunc(img):
    '''
    Calculates the energy by using the Euclidean norm of the gradient.
    (|di(x,y)/dx|^2 + |di(x,y)/dy|^2)^(1/2)
    @param img The Image
    @return Numpy array with the energy
    '''
    img_g = __makeGray(img)
    gy, gx = np.gradient(img_g)
    return np.sqrt(gy**2+gx**2)

def laplaceFunc(img):
    '''
    Calculates the energy by using Laplace function (second derivative)
    @param img The Image
    @return Numpy array with the energy
    '''
    return laplace_div(__makeGray(img))

export = {
    "AbsDiv": absEnergyFunc,
    "L2Gradient": l2gradientFunc, 
    'Laplace': laplaceFunc
    }

if withCV2:
    export['Corner Harris'] = cornerHarrisFunc
    export['Pre-Corner-Detect'] = preCornerDetectFunc