# -*- coding: utf-8 -*-
# If you do not want to use OpenGl for rendering the image:
# withGL = False instead of True
withGL = True
qtver = 5
try:
    from PyQt5 import QtGui as guig
    from PyQt5 import QtWidgets as gui

    if withGL:
        from PyQt5 import QtOpenGL as gl
    from PyQt5 import QtCore
except:
    qtver = 4
    from PyQt4 import QtGui as gui
    from PyQt4 import QtCore

    guig = gui
    from PyQt4 import QtOpenGL as gl

    withGL = True
import gui.QtTool as tool


class ImgEntry:
    def __init__(self):
        self.pixmap = None
        self.paintingPixmap = None
        self.imgNP = None

    def getPixmap(self):
        return self.pixmap

    def getNPArray(self):
        if (self.imgNP is None):
            return tool.qimage2numpy(self.pixmap.toImage())
        return self.imgNP

    def setPixmap(self, pixmap):
        self.pixmap = pixmap

    def setNpArray(self, array):
        self.imgNP = array

    def setPaintingPixmap(self, pixmap):
        self.paintingPixmap = pixmap

    def getPaintingPixmap(self):
        return self.paintingPixmap


class PainableItem(gui.QGraphicsPixmapItem):
    def __init__(self):
        gui.QGraphicsPixmapItem.__init__(self)
        self.__pressing = False
        self.__painter = None
        self.__radius = 5
        self.__pixmap = None

    def setRadius(self, r):
        self.__radius = r

    def getRadius(self):
        return self.__radius

    def mousePressEvent(self, event):
        if (self.__pixmap):
            self.__pressing = True
            self.__painter = guig.QPainter(self.__pixmap)
            self.__painter.setBrush(guig.QBrush(guig.QColor(0, 0, 0)))

    def setInternPixmap(self, pixmap):
        self.setPixmap(pixmap)
        self.__pixmap = pixmap

    def mouseMoveEvent(self, ev):
        if (self.__pressing and self.__painter and self.__pixmap):
            x = int(ev.pos().x())
            y = int(ev.pos().y())
            r = self.__radius
            self.__painter.save()
            self.__painter.drawEllipse(x - r, y - r, 2 * r, 2 * r)
            self.__painter.restore()
            self.setPixmap(self.__pixmap)

    def mouseReleaseEvent(self, ev):
        self.__pressing = False
        self.__painter = None


class ImgShowWdg(gui.QGraphicsView):
    sizeChanged = QtCore.pyqtSignal(['int', 'int'])  

    def __init__(self, parent=None):
        gui.QGraphicsView.__init__(self, parent)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scene = gui.QGraphicsScene()
        self.__pixmapItem = gui.QGraphicsPixmapItem()
        scene.addItem(self.__pixmapItem)
        self.__maskPixmapItem = PainableItem()
        scene.addItem(self.__maskPixmapItem)
        self.setScene(scene)
        if (withGL):
            self.setViewport(gl.QGLWidget())
        gui.QApplication.instance().aboutToQuit.connect(self.deleteLater)
        self.__undoCount = 10
        self.__imgEntries = []
        self.__currentImgEntry = -1

    def resizeEvent(self, ev):
        gui.QGraphicsView.resizeEvent(self, ev)
        self.fitInView(self.__pixmapItem, QtCore.Qt.KeepAspectRatio)

    def __currentEntry(self):
        if (self.__currentImgEntry < 0):
            return None
        return self.__imgEntries[self.__currentImgEntry]

    def __newEntry(self):
        self.__imgEntries = self.__imgEntries[:self.__currentImgEntry + 1]  
        entry = ImgEntry()
        self.__imgEntries.append(entry)
        self.__currentImgEntry += 1
        diff = len(self.__imgEntries) - self.__undoCount
        if (diff > 0):
            self.__imgEntries = self.__imgEntries[diff:]
            self.__currentImgEntry -= diff
        return entry

    def undo(self):
        if (self.__currentImgEntry > 0):
            self.__currentImgEntry = self.__currentImgEntry - 1
            self.__emitSizeChanged()
            self.updatePixmaps()

    def redo(self):
        if (self.__currentImgEntry + 1 >= len(self.__imgEntries)):
            return
        self.__currentImgEntry = self.__currentImgEntry + 1
        self.__emitSizeChanged()
        self.updatePixmaps()

    def updatePixmaps(self):
        entry = self.__currentEntry()
        if (entry):
            self.__pixmapItem.setPixmap(entry.getPixmap())
            self.__maskPixmapItem.setInternPixmap(entry.getPaintingPixmap())
            self.fitInView(self.__pixmapItem, QtCore.Qt.KeepAspectRatio)

    def getPixmap(self):
        entry = self.__currentEntry()
        if (entry is None):
            return None
        return entry.getPixmap()

    def getNPArray(self):
        entry = self.__currentEntry()
        if (entry is None):
            return None
        nparray = entry.getNPArray()
        if (nparray is None):
            return tool.qimage2numpy(entry.getPixmap().toImage())
        return nparray

    def setImageFromNP(self, nparray, entry=None):
        if (entry is None):
            entry = self.__newEntry()
        self.setQImage(tool.numpy2qimage(nparray), entry)
        entry.setNpArray(nparray)

    def setQImage(self, image, entry=None):
        if (entry is None):
            entry = self.__newEntry()
        self.setPixmap(guig.QPixmap.fromImage(image), entry)
        entry.setNpArray(None)

    def __clearPaintingPixmap(self):
        entry = self.__currentEntry()
        if (entry is None):
            return
        if (entry.getPixmap()):
            pixmap = guig.QPixmap(entry.getPixmap().width(), entry.getPixmap().height())
            pixmap.fill(guig.QColor(0, 0, 0, 1)) 
            entry.setPaintingPixmap(pixmap)
            self.__maskPixmapItem.setInternPixmap(pixmap)
        else:
            print ("No Pixmap __clearPaintintPixmap-ImgShowWdg")
            entry.setPaintingPixmap(None)

    def clearPaintingPixmap(self):
        self.__clearPaintingPixmap()
        self.updatePixmaps()

    def getPaintingPixmap(self):
        entry = self.__currentEntry()
        if (entry is None):
            return None
        return entry.getPaintingPixmap()

    def getPaintintNPImage(self):
        entry = self.__currentEntry()
        if (entry is None or entry.getPaintingPixmap() is None):
            return None
        npimg = tool.qimage2numpy(entry.getPaintingPixmap().toImage().convertToFormat(guig.QImage.Format_ARGB32))
        return (npimg[:, :, 3] > 1).astype("uint8")

    def setPainterRadius(self, rad=5):
        self.__maskPixmapItem.setRadius(rad)

    def painterRadius(self):
        return self.__maskPixmapItem.getRadius()

    def __emitSizeChanged(self):
        entry = self.__currentEntry()
        if (entry and entry.getPixmap()):
            self.sizeChanged.emit(entry.getPixmap().width(), entry.getPixmap().height())

    def setPixmap(self, pixmap, entry=None):
        if (entry is None):
            entry = self.__newEntry()
        entry.setPixmap(pixmap)
        self.__pixmapItem.setPixmap(pixmap)
        self.__emitSizeChanged()
        self.__clearPaintingPixmap()
        self.updatePixmaps()
