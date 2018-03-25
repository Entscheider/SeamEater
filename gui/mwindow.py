# -*- coding: utf-8 -*-
qtver = 5
try:
    from PyQt5 import QtGui as guig
    from PyQt5 import QtWidgets as gui
except:
    from PyQt4 import QtGui as gui

    qtver = 4
    guig = gui
from gui.imgshowwdg import ImgShowWdg
from gui.actionWdg import ActionWdg
import numpy as np

from scipy.misc import imsave as imwrite
#from scipy.ndimage import imread


class MainWindow(gui.QMainWindow):
    def __init__(self):
        gui.QMainWindow.__init__(self)
        self.setWindowTitle("SeamEater")
        self.setAcceptDrops(True)
        self.setUnifiedTitleAndToolBarOnMac(True)
        mwdg = gui.QWidget()
        self.setCentralWidget(mwdg)
        self.imgwdg = ImgShowWdg(self)
        self.imgwdg.sizeChanged.connect(lambda w, h: self.__infoText.setText("w: %d,h: %d" % (w, h)))
        lay = gui.QVBoxLayout()
        mwdg.setLayout(lay)
        lay.addWidget(self.imgwdg)
        self.addDockWidget(0x2, self.__initDockWidget())
        self.__initToolBar()
        self.__energyFunctions = {}

    def getEnergyFactoryMap(self):
        return self.__energyFunctions

    def setEnergyFactoryMap(self, map):
        self.__energyFunctions = list(map.values())
        for key in map:
            val = map[key]
            self.__choosenFunctionBox.addItem(key, val)
        self.__choosenFunctionBox.setCurrentIndex(0)

    def dragEnterEvent(self, e):
        if (e.mimeData().hasUrls()):
            e.acceptProposedAction()

    def dropEvent(self, e):
        if (qtver==4):
            self.loadImage(str(e.mimeData().urls()[0].toLocalFile()))
        else:
            self.loadImage(e.mimeData().urls()[0].toLocalFile())
    def addActionWdg(self, actionWdg):
        '''
          actionWdg.title: -> String
          actionWdg.applyImage: nparray -> nparray
        '''
        self.actionWdg.addActionWdg(actionWdg)

    def __initDockWidget(self):
        actionDockWdg = gui.QDockWidget("Actions")
        self.actionWdg = ActionWdg(self.imgwdg.getNPArray, self.imgwdg.setImageFromNP, self.__updateProgress,
                                   self.imgwdg.getPaintintNPImage)
        actionDockWdg.setWidget(self.actionWdg)
        return actionDockWdg

    def __initToolBar(self):
        toolbar = self.addToolBar("main")
        currentStyle = gui.QApplication.instance().style()
        toolbar.addAction(currentStyle.standardIcon(gui.QStyle.SP_DialogOpenButton), "Load...", self.__onLoadImage)
        toolbar.addAction(currentStyle.standardIcon(gui.QStyle.SP_DialogSaveButton), "Save as...", self.__onSaveImage)
        toolbar.addSeparator()
        toolbar.addAction(currentStyle.standardIcon(gui.QStyle.SP_ArrowLeft), "Undo", self.imgwdg.undo)
        toolbar.addAction(currentStyle.standardIcon(gui.QStyle.SP_ArrowRight), "Redo", self.imgwdg.redo)

        toolbar = self.addToolBar("Work")
        toolbar.addAction(currentStyle.standardIcon(gui.QStyle.SP_DialogDiscardButton), "Clear",
                          self.imgwdg.clearPaintingPixmap)
        spinbox = gui.QSpinBox()
        spinbox.setValue(self.imgwdg.painterRadius())
        spinbox.valueChanged.connect(self.imgwdg.setPainterRadius)
        toolbar.addWidget(spinbox)

        toolbar = self.addToolBar("Functions")
        self.__choosenFunctionBox = gui.QComboBox()
        toolbar.addWidget(self.__choosenFunctionBox)
        toolbar.addAction(currentStyle.standardIcon(gui.QStyle.SP_BrowserStop),"Stop",self.actionWdg.stopAction)
        self.__choosenFunctionBox.currentIndexChanged.connect(
            lambda idx: self.actionWdg.setCurrentEnergyFunction(self.__energyFunctions[idx]))

        statusBar = self.statusBar()
        self.__infoText = gui.QLabel()
        self.__progressBar = gui.QProgressBar()
        self.__progressBar.setTextVisible(True)
        statusBar.addPermanentWidget(self.__infoText)
        statusBar.addPermanentWidget(self.__progressBar)

    def __updateProgress(self, p):
        self.__progressBar.setValue(p)

    def __onLoadImage(self):
        filename = gui.QFileDialog.getOpenFileName(self)
        if (qtver == 5):
            filename = filename[0]
        else:
            filename = str(filename)
        if (len(filename) == 0):
            return
        self.loadImage(filename)

    def loadImage(self, filename):
        ## Use Qt for image loading
        img = guig.QImage(filename)
        self.imgwdg.setQImage(img)
        ## Use Scipy for image loading
        # img = imread(filename)
        # self.imgwdg.setImageFromNP(img)


    def __onSaveImage(self):
        filename = gui.QFileDialog.getSaveFileName()
        if (qtver == 5):
            filename = filename[0]
        else:
            filename = str(filename)
        if (len(filename) == 0):
            return
        #self.imgwdg.getPixmap().save(filename) # Use Qt for saving images.
        imwrite(filename, self.imgwdg.getNPArray()) # Use Scipy for saving images.
