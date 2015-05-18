# -*- coding: utf-8 -*-
try:
    from PyQt5 import QtGui as guig
    from PyQt5 import QtWidgets as gui
    from PyQt5 import QtCore
except:
    from PyQt4 import QtGui as gui

    guig = gui
    from PyQt4 import QtCore
import numpy as np
import ImgLib.MyLib as ML
import ImgLib.MyLibTool as MLT
import matplotlib

from abc import ABCMeta, abstractmethod



class StdEffect(QtCore.QObject):
    '''
    StdEffect describes an effect for the gui.
    Is contains methods for getting gui elements and apply an effect.
    Things to do for implementing an effect:
    - Making a subclass
    - Generate some graphical elements (see self._addWdg, self.lay, self._addStretch, self._addDiscription)
    - For working with energy functions use self.getEnergyFunction
    - Implementing _applyImage(...)
        - Make use of the progress signal and use them for your effect
        - self._haveToQuit() return true if the effect should stop.
    '''
    _metaclass__ = ABCMeta
    '''
        Signal for notifying the progress of the effect. 
        The first argument is the progress as int.
    '''
    progress = QtCore.pyqtSignal(['int'])

    '''
        Signal which notifies when the effect is done.
        It will be emitted automatically.
    '''
    finished = QtCore.pyqtSignal(['PyQt_PyObject'])
    
    '''
        Signal notifies the start of the effect.
        It will be emitted automatically.
    '''
    started = QtCore.pyqtSignal([])

    def __init__(self, title):
        '''
        @param title the title of the effect
        '''
        QtCore.QObject.__init__(self)
        self.mainWdg = gui.QWidget()
        self.lay = gui.QVBoxLayout()
        self.mainWdg.setLayout(self.lay)
        self.__title = title
        self.__energyfunction = self.__stdEnergyFunction
        self.__quitting = False

    def quit(self):
        '''
            Set a flag for cancel work. 
        '''
        self.__quitting = True

    def _haveToQuit(self):
        '''
            Returns true when the effect should cancel.
            @return true if yes, false otherwise.
        '''
        return self.__quitting

    def getEnergyFunction(self, img): # Delete and pass through argument by apply_image?
        '''
            Returns the energy function.
            @param img The picture for building the energy-function.
            @return A numpy-array hopefully with the size of img
        '''
        return self.__energyfunction(img)


    def setEnergyBuildFunction(self, func):  
        '''
            Sets the energy function for this effect.
            @param func A function of the form img => nparray
        '''
        self.__energyfunction = func

    def __stdEnergyFunction(self, img):
        img_g = img
        if (np.ndim(img) == 3):
            img_g = img[:, :, 1]
            for p in xrange(1, img.shape[2]):
                img_g = img_g + img[:, :, p]
            img_g = img_g / img.shape[2]
        img_div = ML.absDivergence(img_g)
        return lambda y, x: img_div[y, x]

    def _addDiscription(self,text):
        '''
            Adds a description to the mainWdg
            @param text The description text
        '''
        label = gui.QLabel(text.decode("utf-8"))
        label.setWordWrap(True)
        sizePoly = label.sizePolicy()
        sizePoly.setHorizontalPolicy(gui.QSizePolicy.Ignored)
        label.setSizePolicy(sizePoly)
        checkbox = gui.QCommandLinkButton()
        checkbox.setText("Description")
        checkbox.setIcon(guig.QIcon())
        checkbox.setCheckable(True)
        checkbox.toggled.connect(label.setVisible)
        self.lay.addWidget(checkbox)
        checkbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        label.setVisible(False)
        self.lay.addWidget(label)


    def _addStretch(self):
        '''
            Adds a stretch. 
        '''
        self.lay.addStretch()

    def getWdg(self):
        '''
            Returns the widget that is used for this effect.
            @return the widget
        ''' 
        return self.mainWdg


    def _addWdg(self, title, wdg):
        '''
            Adds a widget with text.
            @param title The title text
            @param wdg The widget
        '''        
        lay2 = gui.QHBoxLayout()
        lay2.addWidget(gui.QLabel(title))
        lay2.addWidget(wdg)
        self.lay.addLayout(lay2)
    @QtCore.pyqtSlot('PyQt_PyObject')
    def applyEffect(self, data):
        '''
        This method should be called if an effect should be applied.
        Also the signals for starting and finishing will be emit.
        This function should not be overridden. 
        The use case for this method is primary for threads.
        @see _applyImage
        @param data A map of the data for this functions. 
                E.g. data['img'] contains the Image 
                and data['mask'] contains an optional mask used for isolate the effect area.
        '''
        self.__quitting = False
        self.started.emit()
        QtCore.QCoreApplication.processEvents()
        res = data['img']
        try:
            res = self._applyImage(data)
        finally:
            self.finished.emit(res)

    @abstractmethod
    def _applyImage(self,data):
        '''
            This method should be overridden by subclasses.
            It apply the effect.
            @param data A map of the data for this functions. 
                   E.g. data['img'] contains the Image 
                   and data['mask'] contains an optional mask used for isolate the effect area.
            @return The image where the effect is applied
        '''
        pass

    def title(self):
        '''
        Returns the title
        @return The title as string
        '''
        return self.__title


class BWEffect(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "Gray")
        lay = self.lay
        self.chR = gui.QCheckBox("Red")
        lay.addWidget(self.chR)
        self.chB = gui.QCheckBox("Blue")
        lay.addWidget(self.chB)
        self.chG = gui.QCheckBox("Green")
        lay.addWidget(self.chG)
        self._addDiscription("Convert the picture into a grayscale one.")
        self._addStretch()

    def _applyImage(self, data):
        img = data['img']
        div = 0
        if (not np.ndim(img) == 3):
            return img
        res = 0
        if (self.chR.isChecked()):
            res = res + img[:, :, 0]
            div = div + 1
        if (self.chG.isChecked()):
            res = res + img[:, :, 1]
            div = div + 1
        if (self.chB.isChecked()):
            res = res + img[:, :, 2]
            div = div + 1
        if (div == 0):
            return img;
        return res / div;


class CurrentFunc(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "CurrentFunc")
        self._addDiscription("Convert the energy function into a viewable image")
        self._addStretch()

    def _applyImage(self, data):
        img = data['img']
        res = self.getEnergyFunction(img)
        max = res.max()
        min = res.min()
        res = (res - min) * 1.0 / (max - min) * 255
        return res.astype("uint8")


class RotateImage(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "Rotate-Mirror")
        self._addDiscription("Rotate and mirrors (=transpose) the picture.")
        self._addStretch()

    def _applyImage(self, data):
        img = data['img']
        return ML.rotateMirror(img)


class ShowSeams(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "Show Seams")
        self.sbox = gui.QSpinBox()
        self.sbox.setMaximum(100)
        self.sbox.setMinimum(0)
        self._addWdg("Seamcount:", self.sbox)
        self._addDiscription("Calculate and show the seams with the current energy function.")
        self._addStretch()

    def _findSeams(self, img, mask):
        h, w = (0, 0)
        if (np.ndim(img) == 3):
            h, w, p = img.shape
        elif np.ndim(img) == 2:
            h, w = img.shape
        else:
            return None  # Picture cannot be edit
        efunc = self.getEnergyFunction(img)
        diff = mask.sum(axis=0)
        diff = (diff > 0).sum().astype("int")
        if (diff == 0):
            return []

        efunc = efunc * h * w
        efunc[mask > 0] = -abs(efunc.max()) * h * w

        return ML.findTopDisjointSeams( efunc, diff, lambda s: self.progress.emit(s),stopFunc=self._haveToQuit)

    def _applyImage(self, data):
        img = data['img']
        h, w = (0, 0)
        if (np.ndim(img) == 3):
            h, w, p = img.shape
        elif np.ndim(img) == 2:
            h, w = img.shape
        else:
            return None  # Picture cannot be edit
        seams = None
        if (data.has_key('mask')):
            mask = data['mask']
            seams = self._findSeams(img, mask)
            if (not len(seams) == 0):
                return MLT.drawSeamsInImage(img, seams)  # Let's use the drawing area.
        diff = self.sbox.value()
        s = self.getEnergyFunction(img)
        seams = ML.findTopDisjointSeams(s, diff, lambda s: self.progress.emit(s),stopFunc=self._haveToQuit)
        return MLT.drawSeamsInImage(img, seams)

class ContentAmplification(StdEffect):
    def __init__(self):
        StdEffect.__init__(self,"Content amplification")
        self.xbox = gui.QSpinBox()
        self.xbox.setValue(1)
        self.xbox.setMaximum(100)
        self.xbox.setMinimum(0)
        self.ybox = gui.QSpinBox()
        self.ybox.setValue(1)
        self.ybox.setMaximum(100)
        self.ybox.setMinimum(0)
        self._addWdg("Amplification X", self.xbox)
        self._addWdg("Amplification Y",self.ybox)
        self._addDiscription("Content Amplification."+
                             "Resize the important areas of the picture by increasing the  "
                             +"image with nearest neighbor and decreasing with seam carving to the original size")
        self._addStretch()
    def _applyImage(self,data):
        img = data['img']
        xCount = self.xbox.value()
        yCount = self.ybox.value()
        h = img.shape[0]
        w = img.shape[1]
        img2 = ML.resizeConventional(img,w+xCount,h+yCount)
        return ML.retargetingImage(img2,xCount,yCount,self.getEnergyFunction,lambda k: self.progress.emit(k),stopFunc=self._haveToQuit)

class BiggerImage(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "Add Seams")
        self.sbox = gui.QSpinBox()
        self.sbox.setMaximum(100)
        self.sbox.setMinimum(0)
        self._addWdg("Seamcount:", self.sbox)
        self._addDiscription("Increase the picture by duplicating (and interpolating) low energy seams")
        self._addStretch()

    def _applyImage(self, data):
        img = data['img']
        diff = self.sbox.value()
        h, w = (0, 0)
        if (np.ndim(img) == 3):
            h, w, p = img.shape
        elif np.ndim(img) == 2:
            h, w = img.shape
        else:
            return None  # Picture cannot be edit
        s = self.getEnergyFunction(img)
        seams = ML.findTopDisjointSeams(s, diff, lambda s: self.progress.emit(s),stopFunc=self._haveToQuit)
        return ML.duplicateSeams(img, seams)


class RemoveSeamImage(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "Remove Seams")
        self.sbox = gui.QSpinBox()
        self.sbox.setValue(1)
        self.sbox.setMaximum(100)
        self.sbox.setMinimum(0)
        self._addWdg("Seamcount:", self.sbox)
        self._addDiscription("Remove low energy seams."
                             +"The number of seams in seamcount will be use. "
                             +"But if there is something drawn seamcount will be ignored " 
                             +"and the marked area will be removed.")
        self._addStretch()

    def _applyImage(self, data):
        img = data['img']
        diff = self.sbox.value()
        res = None
        if (data.has_key('mask')):
            mask = data['mask']
            res = self._maskremove(img, mask, ML.removeSeams)
        if (res is None):
            res = self._wholeremove(img, diff, ML.removeSeams)
        if (len(res) == 0):
            return None
        return res

    def _maskremove(self, img, mask, removeAction):
        diff = mask.sum(axis=0)
        diff = (diff > 0).sum().astype("int")
        if (diff == 0):
            return None
        h, w = (0, 0)
        if (np.ndim(img) == 3):
            h, w, p = img.shape
        elif np.ndim(img) == 2:
            h, w = img.shape
        else:
            return None  # Picture cannot be edit
        efunc = self.getEnergyFunction(img)
        efunc[mask > 0] = -abs(efunc.max()) * h * w # Be as little as possible so it cannot be reached otherwise.

        res = img
        for i in xrange(diff):
            self.progress.emit(i * 100 / diff)
            QtCore.QCoreApplication.processEvents()
            seam = ML.findOptimalSeam(efunc,stopFunc=self._haveToQuit)
            if (self._haveToQuit()):
                return []
            res = removeAction(res, seam)
            efunc = ML.removeSeams(efunc, seam)
        return res

    def _wholeremove(self, img, diffcount, removeAction):
        h, w = (0, 0)
        if (np.ndim(img) == 3):
            h, w, p = img.shape
        elif np.ndim(img) == 2:
            h, w = img.shape
        else:
            return None  # Picture cannot be edit
        res = img
        s = self.getEnergyFunction(img)
        for i in xrange(diffcount):
            if (self._haveToQuit()):
                return
            self.progress.emit(i * 100 / diffcount)
            QtCore.QCoreApplication.processEvents()
            seam = ML.findOptimalSeam(s,stopFunc=self._haveToQuit)
            res = removeAction(res, seam)
            s = self.getEnergyFunction(res)
        return res

class RetargetingImage(StdEffect):
    def __init__(self):
        StdEffect.__init__(self,"Retargeting Image")
        self.xbox = gui.QSpinBox()
        self.xbox.setValue(1)
        self.xbox.setMaximum(100)
        self.xbox.setMinimum(0)
        self.ybox = gui.QSpinBox()
        self.ybox.setValue(1)
        self.ybox.setMaximum(100)
        self.ybox.setMinimum(0)
        self._addWdg("Removing in X", self.xbox)
        self._addWdg("Removing in Y",self.ybox)
        self._addDiscription("Retargeting with optimal seam order. "
                             +"Decrease the image by finding an optimal order (vertical or horizontal) to remove seams.")
        self._addStretch()

    def _applyImage(self,data):
        img = data['img']
        xCount = self.xbox.value()
        yCount = self.ybox.value()
        return ML.retargetingImage(img,xCount,yCount,self.getEnergyFunction,lambda k: self.progress.emit(k),stopFunc=self._haveToQuit)



# class RemoveSeamGradient(RemoveSeamImage):
class RemoveSeamGradient(ShowSeams):
    def __init__(self):
        StdEffect.__init__(self, "Remove in Gradient")
        self.sbox = gui.QSpinBox()
        self.sbox.setValue(1)
        self.sbox.setMaximum(100)
        self.sbox.setMinimum(1)
        self.itbox = gui.QSpinBox()
        self.itbox.setMinimum(0)
        self.itbox.setMaximum(200)
        self.itbox.setValue(20)
        self.olbox = gui.QSpinBox()
        self.olbox.setValue(15)
        self.olbox.setMinimum(3)
        self.olbox.setMaximum(100)
        self._addWdg("Seamcount:", self.sbox)
        self._addWdg("Iterations:", self.itbox)
        self._addWdg("Overlapping:", self.olbox)
        self._addDiscription("Remove seams with the lowest energy from the gradient and "
                             +"reconstruct the picture from that gradient. "
                             + "The number of seams will be set with Seamcount "
                             + "or will be ignored if there is marked something. "
                             + "Iterations is the number of iterations for solving the  linear system of equations. "
                             + "If the number is 0 then an exact solution will be used. "
                             + "Overlapping is the number of pixel that will be deleted around the seams and mixed with the original picture.")
        self._addStretch()

    def _applyImage(self, data):
        img = data['img']
        itera = self.itbox.value()
        overl = self.olbox.value()

        seams = []
        if (data.has_key('mask')):
            mask = data['mask']
            seams = self._findSeams(img, mask)
        if self._haveToQuit():
            return None
        if (len(seams) == 0): # No Masking
            diff = self.sbox.value()
            h, w = (0, 0)
            if (np.ndim(img) == 3):
                h, w, p = img.shape
            elif np.ndim(img) == 2:
                h, w = img.shape
            else:
                return None # Picture cannot be edit
            res = img
            s = self.getEnergyFunction(img)
            seams = ML.findTopDisjointSeams(s, diff, lambda i: self.progress.emit(i),stopFunc=self._haveToQuit)
            if (self._haveToQuit()):
                return None
            res = ML.removeSeamsInGradient(res, seams, itera, overl,progressFunc=lambda i: self.progress.emit(i),stopFunc=self._haveToQuit)
            return res
        else:
            return ML.removeSeamsInGradient(img, seams, itera, overl,progressFunc=lambda i: self.progress.emit(i),stopFunc=self._haveToQuit)


class HistoEqu(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "HistoEqu")
        self._addDiscription("Histogram equalization")
        self._addStretch()

    def __apply1dim(self, img):
        h, w = img.shape
        hist, other = np.histogram(img, 256)
        cm = np.round(256.0 * hist.cumsum() / (h * w)).astype("uint8")
        img = img.astype("uint8")
        return cm[img]

    def __applyhsv(self, img):
        h, w = img.shape
        img = (img * 255).astype("uint8")
        hist, other = np.histogram(img, 256)
        cm = np.round(255 * hist.cumsum() / (h * w)).astype("uint8")
        img = img.astype("uint8")
        img = cm[img]
        return img * 1.0 / 255.0

    def _applyImage(self, data):
        img = data['img']
        if (np.ndim(img) == 2):
            return self.__apply1dim(img)
        h, w, p = img.shape
        if (p == 4):
            img = np.delete(img, 3, 2)
        hsvimg = matplotlib.colors.rgb_to_hsv(img * 1.0 / 255.0)
        hsvimg[:, :, 2] = self.__applyhsv(hsvimg[:, :, 2])
        return (matplotlib.colors.hsv_to_rgb(hsvimg) * 255).astype("uint8")


class ShowMaskOnly(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "ShowMaskOnly")
        self._addDiscription("Shows the marked area.")
        self._addStretch()

    def _applyImage(self, data):
        if (data.has_key('mask')):
            mask = data['mask']
            return (255 * mask).astype("uint8")
        return data['img']


from numpy.fft import fft2, fftshift


class ShowFFT(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "ShowFFT")
        self._addDiscription("Shows the Fourier transformation (absolute).")
        self._addStretch()

    def _applyImage(self,data):
        img = data['img']
        img_g = img
        if (np.ndim(img) == 3):
            img_g = (img[:, :, 0] + img[:, :, 1] + img[:, :, 2]) / 3
        return np.log10(np.abs(fftshift(fft2(img_g)))) * 255


class ResizingNormal(StdEffect):
    def __init__(self):
        StdEffect.__init__(self, "Resize Common")
        self.sboxW = gui.QSpinBox()
        self.sboxW.setMaximum(3000)
        self.sboxW.setMinimum(50)
        self.sboxH = gui.QSpinBox()
        self.sboxH.setMaximum(3000)
        self.sboxH.setMinimum(50)
        self._addWdg("Width:", self.sboxW)
        self._addWdg("Height:", self.sboxH)
        self._addDiscription("Resize the picture using Nearest Neighbor.")
        self._addStretch()

    def _applyImage(self, data):
        img = data['img']
        width = self.sboxW.value()
        height = self.sboxH.value()
        return ML.resizeConventional(img, width, height)


debug = [ShowSeams, ShowMaskOnly, ShowFFT, CurrentFunc]
export = [RemoveSeamImage, BiggerImage, RemoveSeamGradient, RetargetingImage, ContentAmplification, ResizingNormal, RotateImage, BWEffect, HistoEqu] + debug
