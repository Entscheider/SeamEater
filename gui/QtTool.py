# -*- coding: utf-8 -*-
# Converting QImage <=> NumPy 
import numpy as np
qt_ver=5
try:
    from PyQt5.QtGui import QImage, qRgb, QColor

except:
    from PyQt4.QtGui import QImage, qRgb, QColor
    qt_ver=4


def qimage2numpy(qimg):
    h = qimg.height()
    w = qimg.width()
    ow = qimg.bytesPerLine() * 8 // qimg.depth()
    d = 0
    if qimg.format() in (QImage.Format_ARGB32_Premultiplied,
                           QImage.Format_ARGB32,
                           QImage.Format_RGB32):
        d = 4
    elif qimg.format() == QImage.Format_Indexed8:
        d = 1
    else:
        raise ValueError("unsupported qimage format")

    if (qt_ver==4):
        buf = qimg.bits().asstring(qimg.numBytes())
    else:
        buf = qimg.bits().asstring(qimg.byteCount())

    res = np.frombuffer(buf, 'uint8')
    res = res.reshape((h,ow,d)).copy()
    if w != ow:
        res = res[:,:w]
    if d >= 3:
        if qimg.format() == QImage.Format_RGB32:
            res = res[:,:,:3]
        tmp = res[:,:,0].copy()
        res[:,:,0] = res[:,:,2]
        res[:,:,2] = tmp
    return res

def numpy2qimage(array):
    if np.ndim(array) == 2:
        img = np.zeros([array.shape[0],array.shape[1],3], dtype=np.uint8)
        img[:,:,0] = array
        img[:,:,1] = array
        img[:,:,2] = array
        array = img
    if np.ndim(array) == 3:
        h,w,d = array.shape
        nd = d
        if nd == 3: nd = 4
        if nd == 1: nd = 3
        img = np.zeros([h,w,nd],np.uint8, 'C')
        if d == 1:
            img[:,:,0] = array[:,:,0]
            img[:,:,1] = array[:,:,0]
            img[:,:,2] = array[:,:,0]
        else:
            img[:,:,:3] = array[:,:,(2,1,0)]
            if d == 4:
                img[:,:,3] = array[:,:,3]
            else:
                img[:,:,3] = 255
    else:
        raise ValueError("can only convert 2D and 3D arrays")

    if img.shape[2] == 3:
        fmt = QImage.Format_RGB32
    elif img.shape[2] == 4:
        fmt = QImage.Format_ARGB32
    else:
        raise ValueError("unsupported image depth")

    res = QImage(img.data, img.shape[1], img.shape[0], fmt)
    res.ndarray = img
    return res


