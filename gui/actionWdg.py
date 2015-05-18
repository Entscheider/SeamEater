# -*- coding: utf-8 -*-
try:
    from PyQt5 import QtGui as guig
    from PyQt5 import QtWidgets as gui
    from PyQt5 import QtOpenGL as gl
    from PyQt5 import QtCore
except:
    from PyQt4 import QtGui as gui

    guig = gui
    from PyQt4 import QtCore


class ActionWdg(gui.QWidget):
    def __init__(self, imgGetFunc, imgSetFunc, progressFunc, imgMaskGetFunc):
        '''
          imgGetFunc: -> NPArray => Where to get the picture
          imgSetFunc: NPArray -> => Where to set the picture
          progressFunc : int -> => How to emit progress
          imgMaskGetFunc: -> NPArray => Where to get the mask
        '''
        gui.QWidget.__init__(self)
        self.imgGetFunc = imgGetFunc
        self.imgSetFunc = imgSetFunc
        self.imgMaskGetFunc = imgMaskGetFunc
        self.progressFunc = progressFunc
        lay = gui.QVBoxLayout()
        self.stackWdg = gui.QStackedWidget()
        self.setLayout(lay)
        applyButton = self.applyButton = gui.QPushButton("Apply")
        applyButton.clicked.connect(self.__applyEffect)
        self.__actionBox = gui.QComboBox()
        self.workerThread = QtCore.QThread(self)
        self.workerThread.finished.connect(self.__restartThread, type=QtCore.Qt.QueuedConnection)
        self.workerThread.start()
        self.__actionBox.currentIndexChanged.connect(self.__actionBoxChanged)
        lay2 = gui.QHBoxLayout()
        lay2.addWidget(self.__actionBox)
        lay2.addWidget(applyButton)
        lay.addLayout(lay2)
        lay.addWidget(self.stackWdg)
        self.__selectedEnergyFunction = None
        self.effects = []
        self.__currentEffect = None

    def selectedEnergyFunction(self):
        return self.__selectedEnergyFunction

    def setCurrentEnergyFunction(self, func):
        self.__selectedEnergyFunction = func

    def __actionBoxChanged(self, inx):
        self.stackWdg.setCurrentIndex(inx)

    def __applyEffect(self):
        wdg = self.effects[self.stackWdg.currentIndex()]
        if (wdg is None):
            return
        npimg = self.imgGetFunc()
        maskImg = self.imgMaskGetFunc()
        if (not self.__selectedEnergyFunction is None):
            wdg.setEnergyBuildFunction(self.__selectedEnergyFunction)
        if (npimg is None):
            return
        self.__currentEffect = wdg
        datamap = {'img': npimg, 'mask': maskImg}
        QtCore.QMetaObject.invokeMethod(wdg, "applyEffect", QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG("PyQt_PyObject", datamap))

    def _lock(self):
        self.applyButton.setEnabled(False)

    def _unlock(self, res):
        if (not res is None):
            self.imgSetFunc(res)
        self.applyButton.setEnabled(True)
        self.progressFunc(0)
        self.__currentEffect = None

    def __updateProgess(self, prog):
        self.progressFunc(prog)

    def __restartThread(self):
        self.workerThread.deleteLater()
        self._unlock(None)
        self.workerThread = QtCore.QThread(self)
        self.workerThread.finished.connect(self.__restartThread, type=QtCore.Qt.QueuedConnection)
        self.workerThread.start()

    def stopAction(self):
       if (not self.__currentEffect is None):
           self.__currentEffect.quit()

    def addActionWdg(self, actionWdg):
        actionWdg.moveToThread(self.workerThread)
        actionWdg.started.connect(self._lock, type=QtCore.Qt.QueuedConnection)
        actionWdg.finished.connect(self._unlock, type=QtCore.Qt.QueuedConnection)
        actionWdg.progress.connect(self.__updateProgess, type=QtCore.Qt.QueuedConnection)
        self.stackWdg.addWidget(actionWdg.getWdg())
        self.effects.append(actionWdg)
        self.__actionBox.addItem(actionWdg.title())
