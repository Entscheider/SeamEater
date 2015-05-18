# -*- coding: utf-8 -*-
import numpy as np

def __myfilter_enlarge(array,newShape):
    '''
    Increases the image to the shape newShape by adding zeros 
    to the image. 
    @param array The image
    @param newShape The new size
    @return The resized image
    @see myfilter
    '''
    h,w = array.shape
    res = np.zeros(newShape)
    res[:h,:w]=array
    return res

def myfilter(img, mask):
    '''
    Apply the filter described by mask to the image (convolution).
    @param img The image 
    @param mask The mask
    @return The image where the filter was applied.
    '''
    def myfilter_intern(img_g):
        h,w = img_g.shape
        newimg = __myfilter_enlarge(img_g,(2*h,2*w))
        newmatrix = __myfilter_enlarge(mask,((2*h,2*w)))
        newimg_fft = np.fft.fftshift(np.fft.fft2(newimg))
        newmatrix_fft = np.fft.fftshift(np.fft.fft2(newmatrix))
        res_fft = newimg_fft * newmatrix_fft;
        res = np.real(np.fft.ifft2((np.fft.fftshift(res_fft))))
        return res[:h,:w]
    if (np.ndim(img)==3):
        h,w,p = img.shape
        res = np.zeros((h,w,p))
        for j in xrange(p):
            res[:,:,j] = myfilter_intern(img[:,:,j])
        return res
    else:
        return myfilter_intern(img)
