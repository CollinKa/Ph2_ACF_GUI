# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from cgi import test
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import *
from Gui.python.Peltier import PeltierController
import time

class Peltier(QWidget):
    def __init__(self, dimension):
        super(Peltier, self).__init__()
        # self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi()
        self.show()

    def setupUi(self):
        # MainWindow.setObjectName("MainWindow")
        # MainWindow.resize(400, 300)

        # self.centralwidget = QtWidgets.QWidget(MainWindow)
        # self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.currentSetTemp = QtWidgets.QLabel("The temperature is currently set to: ", self)
        self.gridLayout.addWidget(self.currentSetTemp, 2,1,1,1)
        self.startButton = QtWidgets.QPushButton("Start Peltier Controller", self)
        self.startButton.clicked.connect(self.setup)
        self.gridLayout.addWidget(self.startButton, 0,0,1,1)
        self.currentTempDisplay = QtWidgets.QLCDNumber(self)
        self.gridLayout.addWidget(self.currentTempDisplay, 3, 0, 1, 2)
        self.setTempButton = QtWidgets.QPushButton("Set Temperature", self)
        self.setTempButton.setEnabled(False)
        self.gridLayout.addWidget(self.setTempButton, 1, 1, 1, 1)
        self.setTempInput = QtWidgets.QDoubleSpinBox(self)
        self.gridLayout.addWidget(self.setTempInput, 1, 0, 1, 1)
        self.currentTempLabel = QtWidgets.QLabel(self)
        self.gridLayout.addWidget(self.currentTempLabel, 2, 0, 1, 1)

        self.polarityButton = QtWidgets.QPushButton("Change Polarity", self)
        self.polarityButton.setEnabled(False)
        self.gridLayout.addWidget(self.polarityButton, 2, 1, 1, 1)
        self.polarityButton.clicked.connect(self.changePolarity)
        self.polarityLabel = QtWidgets.QLabel("N/a", self)
        self.gridLayout.addWidget(self.polarityLabel, 0, 2, 1, 1)

        self.powerStatus = QtWidgets.QLabel(self)
        self.powerStatusLabel = QtWidgets.QLabel("Power Status of Peltier: ", self)
        self.powerButton = QtWidgets.QPushButton("Peltier Power On/Off")
        self.powerButton.setEnabled(False)
        self.powerButton.clicked.connect(self.powerSignal)
        self.gridLayout.addWidget(self.powerButton, 0, 2, 1, 1)

        self.gridLayout.addWidget(self.powerStatusLabel, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.powerStatus, 1, 3, 1, 1)
        # self.currentSetTempLabel = QtWidgets.QLabel(self)
        # self.gridLayout.addWidget(self.currentSetTempLabel, 0,1,1,1)
        # self.setTempButton.clicked.connect(self.printSetTemp)
        self.setTempButton.clicked.connect(self.setTemp)
        self.setLayout(self.gridLayout)
    ###############################################################################
    # def retranslateUi(self, MainWindow):                                        #
    #     _translate = QtCore.QCoreApplication.translate                          #
    #     MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))       #
    #     self.label.setText(_translate("MainWindow", "Set Temperature"))         #
    #     self.setTempButton.setText(_translate("MainWindow", "Set Temp"))        #
    #     self.currentTempLabel.setText(_translate("MainWindow", "Current Temp")) #
    ###############################################################################

    def setup(self):
        self.pelt = PeltierController('/dev/ttyUSB0',9600)
        self.timer = QTimer()
        self.powerTimer = QTimer()
        self.timer.timeout.connect(self.showTemp)
        self.powerTimer.timeout.connect(self.setPowerStatus)
        self.timer.start(500) # Will check the temperature every 500ms
        self.powerTimer.start(1000) # Will check the power every second
        self.image = QtGui.QPixmap()
        redledimage = QtGui.QImage("../icons/led-red-on.png").scaled(QtCore.QSize(60,10), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.redledpixmap = QtGui.QPixmap.fromImage(redledimage)
        greenledimage = QtGui.QImage("../icons/green-led-on.png").scaled(QtCore.QSize(60,10), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.greenledpixmap = QtGui.QPixmap.fromImage(greenledimage)

    def powerSignal(self):
        print(self.power)
        if self.power == '0':
            self.pelt.powerController('1')
            print("Turning on controller")
        elif self.power =='1':
            self.pelt.powerController('0')
            print('Turning off controller')
        time.sleep(0.5) 
        self.getPower()

    def printSetTemp(self):
        time.sleep(0.050)
        setTemp = self.pelt.readSetTemperature()
        self.currentSetTempLabel.setText(f'The Peltier is currently set to {setTemp}')

    def setTemp(self):
        self.pelt.setTemperature(self.setTempInput.value())
        self.currentSetTemp.setText(f"The temperature is currently set to: {self.setTempInput.value()}")
        # Send temperature reading to device

    def changePolarity(self):
        polarity = self.pelt.changePolarity()
        self.polarityLabel.setText(f"Change Polarity: {polarity}")

    def getPower(self):
        self.power = self.pelt.checkPower()
    
    def setPowerStatus(self):
        self.getPower()
        if self.power == '0':
            self.powerStatus.setPixmap(self.redledpixmap)
        elif self.power =='1':
            self.powerStatus.setPixmap(self.greenledpixmap)

        
    def getTemp(self):
        return self.pelt.readTemperature()

    def showTemp(self):
        temp = self.getTemp()
        self.currentTempDisplay.display(temp)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Peltier(500)
    sys.exit(app.exec_())
