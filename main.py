try:
    from PyQt5 import QtGui as guig
    from PyQt5 import QtWidgets as qgui
except:
    from PyQt4 import QtGui as qgui
    guig=qgui
import sys
import StdEffects as Effects
import EnergyFunction as Functions
from gui.mwindow import MainWindow

app = qgui.QApplication(sys.argv)
app.setWindowIcon(guig.QIcon("pic/logo.png"))
win = MainWindow()
for effectWdg in Effects.export:
    win.addActionWdg(effectWdg())
win.setEnergyFactoryMap(Functions.export)
win.resize(600,300)
win.show()
win.loadImage("pic/logo.png")
app.exec_()
