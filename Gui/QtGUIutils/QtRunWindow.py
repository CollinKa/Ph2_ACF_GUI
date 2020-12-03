from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox, QDateTimeEdit,
		QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget,
		QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
		QSlider, QSpinBox, QStyleFactory, QTableView, QTableWidget, QTabWidget, QTextEdit, QHBoxLayout,
		QVBoxLayout, QWidget, QMainWindow, QMessageBox, QSplitter)

import sys
import os
import subprocess
import threading
import time
import random
from subprocess import Popen, PIPE

from Gui.GUIutils.DBConnection import *
from Gui.GUIutils.guiUtils import *
#from Gui.QtGUIutils.QtStartWindow import *
from Gui.QtGUIutils.QtCustomizeWindow import *
from Gui.QtGUIutils.QtTableWidget import *
from Gui.QtGUIutils.QtMatplotlibUtils import *

class QtRunWindow(QWidget):
	def __init__(self,master, info):
		super(QtRunWindow,self).__init__()
		self.master = master
		self.info = info
		self.connection = self.master.connection
		self.GroupBoxSeg = [1, 10,  1]
		self.HorizontalSeg = [3, 5]
		self.VerticalSegCol0 = [1,3]
		self.VerticalSegCol1 = [2,2]
		self.processingFlag = False
		self.input_dir = ''
		self.output_dir = ''
		self.config_file = '' #os.environ.get('GUI_dir')+ConfigFiles.get(self.calibration, "None")
		self.rd53_file  = ''
		self.grade = -1
		self.currentTest = ""
		self.backSignal = False
		self.haltSignal = False
		self.finishSingal = False
		self.proceedSignal = False
		self.DisplayW = 450
		self.DisplayH = 450
		self.runNext = threading.Event()
		self.testIndexTracker = -1
		self.outputDirQueue = []
		#Fixme: QTimer to be added to update the page automatically
		self.grades = []

		self.mainLayout = QGridLayout()
		self.setLayout(self.mainLayout)

		self.setLoginUI()
		self.createHeadLine()
		self.createMain()
		self.createApp()
		self.occupied()

		self.run_process = QProcess(self)
		self.run_process.readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
		self.run_process.finished.connect(self.on_finish)

	def setLoginUI(self):
		self.setGeometry(100, 100, 1000, 1800)  
		self.setWindowTitle('Run Control Page')  
		self.show()

	def createHeadLine(self):
		self.HeadBox = QGroupBox()

		self.HeadLayout = QHBoxLayout()

		HeadLabel = QLabel('<font size="4"> Module: {0}  Test: {1} </font>'.format(self.info[0], self.info[1]))
		HeadLabel.setMaximumHeight(30)

		statusString, colorString = checkDBConnection(self.connection)
		StatusLabel = QLabel()
		StatusLabel.setText(statusString)
		StatusLabel.setStyleSheet(colorString)

		self.HeadLayout.addWidget(HeadLabel)
		self.HeadLayout.addStretch(1)
		self.HeadLayout.addWidget(StatusLabel)

		self.HeadBox.setLayout(self.HeadLayout)

		self.mainLayout.addWidget(self.HeadBox, 0, 0, self.GroupBoxSeg[0], 1)

	def destroyHeadLine(self):
		self.HeadBox.deleteLater()
		self.mainLayout.removeWidget(self.HeadBox)
	
	def createMain(self):
		self.testIndexTracker = 0
		self.MainBodyBox = QGroupBox()

		mainbodylayout = QHBoxLayout()

		kMinimumWidth = 120
		kMaximumWidth = 150
		kMinimumHeight = 30
		kMaximumHeight = 80

		# Splitters
		MainSplitter = QSplitter(Qt.Horizontal)
		LeftColSplitter = QSplitter(Qt.Vertical)
		RightColSplitter = QSplitter(Qt.Vertical)

		#Group Box for controller
		ControllerBox = QGroupBox()
		ControllerSP = ControllerBox.sizePolicy()
		ControllerSP.setVerticalStretch(self.VerticalSegCol0[0])
		ControllerBox.setSizePolicy(ControllerSP)

		self.ControlLayout = QGridLayout()

		self.CustomizedButton = QPushButton("&Customize...")
		self.CustomizedButton.clicked.connect(self.customizeTest)
		self.ResetButton = QPushButton("&Reset")
		self.ResetButton.clicked.connect(self.resetConfigTest)
		self.RunButton = QPushButton("&Run")
		self.RunButton.setDefault(True)
		self.RunButton.clicked.connect(self.runTest)
		#self.ContinueButton = QPushButton("&Continue")
		#self.ContinueButton.clicked.connect(self.sendProceedSignal)
		self.AbortButton = QPushButton("&Abort")
		self.AbortButton.clicked.connect(self.abortTest)
		self.SaveButton = QPushButton("&Save")
		self.SaveButton.clicked.connect(self.saveTest)

		self.ControlLayout.addWidget(self.CustomizedButton,0,0,1,2)
		self.ControlLayout.addWidget(self.ResetButton,0,2,1,1)
		self.ControlLayout.addWidget(self.RunButton,1,0,1,1)
		self.ControlLayout.addWidget(self.AbortButton,1,1,1,1)
		self.ControlLayout.addWidget(self.SaveButton,1,2,1,1)

		ControllerBox.setLayout(self.ControlLayout)

		#Group Box for ternimal display
		TerminalBox = QGroupBox("&Terminal")
		TerminalSP = TerminalBox.sizePolicy()
		TerminalSP.setVerticalStretch(self.VerticalSegCol0[1])
		TerminalBox.setSizePolicy(TerminalSP)
		TerminalBox.setMinimumWidth(400)

		ConsoleLayout = QGridLayout()
		
		self.ConsoleView = QTextEdit()
		self.ConsoleView.setStyleSheet("QTextEdit { background-color: rgb(10, 10, 10); color : white; }")

		ConsoleLayout.addWidget(self.ConsoleView)
		TerminalBox.setLayout(ConsoleLayout)

			

		#Group Box for output display
		OutputBox = QGroupBox("&Result")
		OutputBoxSP = OutputBox.sizePolicy()
		OutputBoxSP.setVerticalStretch(self.VerticalSegCol1[0])
		OutputBox.setSizePolicy(OutputBoxSP)

		OutputLayout = QGridLayout()
		self.DisplayTitle = QLabel('<font size="6"> Result: </font>')
		self.DisplayLabel = QLabel()
		self.DisplayView = QPixmap('test_plots/test_best1.png').scaled(QSize(self.DisplayW,self.DisplayH), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.DisplayLabel.setPixmap(self.DisplayView)
		self.ReferTitle = QLabel('<font size="6"> Reference: </font>')
		self.ReferLabel = QLabel()
		self.ReferView = QPixmap('test_plots/test_gain_refer.png').scaled(QSize(self.DisplayW,self.DisplayH), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.ReferLabel.setPixmap(self.ReferView)
		self.ListWidget = QListWidget()
		self.ListWidget.setMinimumWidth(150)
		self.ListWidget.insertItem(0, "Module_0_Chip_0")
		self.ListWidget.clicked.connect(self.clickedOutputItem)

		OutputLayout.addWidget(self.DisplayTitle,0,0,1,2)
		OutputLayout.addWidget(self.DisplayLabel,1,0,1,2)
		OutputLayout.addWidget(self.ReferTitle,0,2,1,2)
		OutputLayout.addWidget(self.ReferLabel,1,2,1,2)
		OutputLayout.addWidget(self.ListWidget,0,4,2,1)
		OutputBox.setLayout(OutputLayout)

		#Group Box for history
		self.HistoryBox = QGroupBox("&History")
		HistoryBoxSP = self.HistoryBox.sizePolicy()
		HistoryBoxSP.setVerticalStretch(self.VerticalSegCol1[1])
		self.HistoryBox.setSizePolicy(HistoryBoxSP)

		self.HistoryLayout = QGridLayout()

		# Display the table for module history
		#self.dataList = getLocalRemoteTests(self.connection, self.info[0])
		#self.proxy = QtTableWidget(self.dataList)
		#self.lineEdit       = QLineEdit()
		#self.lineEdit.textChanged.connect(self.proxy.on_lineEdit_textChanged)
		#self.view           = QTableView()
		#self.view.setSortingEnabled(True)
		#self.comboBox       = QComboBox()
		#self.comboBox.addItems(["{0}".format(x) for x in self.dataList[0]])
		#self.comboBox.currentIndexChanged.connect(self.proxy.on_comboBox_currentIndexChanged)
		#self.label          = QLabel()
		#self.label.setText("Regex Filter")

		#self.view.setModel(self.proxy)
		#self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

		self.HistoryLayout = QGridLayout()
		#self.HistoryLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
		#self.HistoryLayout.addWidget(self.view, 1, 0, 1, 3)
		#self.HistoryLayout.addWidget(self.comboBox, 0, 2, 1, 1)
		#self.HistoryLayout.addWidget(self.label, 0, 0, 1, 1)

		self.StatusCanvas = RunStatusCanvas(parent=self,width=5, height=4, dpi=100)
		self.HistoryLayout.addWidget(self.StatusCanvas)

		self.HistoryBox.setLayout(self.HistoryLayout)

		
		LeftColSplitter.addWidget(ControllerBox)
		LeftColSplitter.addWidget(TerminalBox)
		RightColSplitter.addWidget(OutputBox)
		RightColSplitter.addWidget(self.HistoryBox)


		LeftColSplitterSP = LeftColSplitter.sizePolicy()
		LeftColSplitterSP.setHorizontalStretch(self.HorizontalSeg[0])
		LeftColSplitter.setSizePolicy(LeftColSplitterSP)

		RightColSplitterSP = RightColSplitter.sizePolicy()
		RightColSplitterSP.setHorizontalStretch(self.HorizontalSeg[1])
		RightColSplitter.setSizePolicy(RightColSplitterSP)

		MainSplitter.addWidget(LeftColSplitter)
		MainSplitter.addWidget(RightColSplitter)

		mainbodylayout.addWidget(MainSplitter)
		#mainbodylayout.addWidget(ControllerBox, sum(self.VerticalSegCol0[:0]), sum(self.HorizontalSeg[:0]), self.VerticalSegCol0[0], self.HorizontalSeg[0])
		#mainbodylayout.addWidget(TerminalBox, sum(self.VerticalSegCol0[:1]), sum(self.HorizontalSeg[:0]), self.VerticalSegCol0[1], self.HorizontalSeg[0])
		#mainbodylayout.addWidget(OutputBox, sum(self.VerticalSegCol1[:0]), sum(self.HorizontalSeg[:1]), self.VerticalSegCol1[0], self.HorizontalSeg[1])
		#mainbodylayout.addWidget(HistoryBox, sum(self.VerticalSegCol1[:1]), sum(self.HorizontalSeg[:1]), self.VerticalSegCol1[1], self.HorizontalSeg[1])


		self.MainBodyBox.setLayout(mainbodylayout)
		self.mainLayout.addWidget(self.MainBodyBox, sum(self.GroupBoxSeg[0:1]), 0, self.GroupBoxSeg[1], 1)

	def destroyMain(self):
		self.MainBodyBox.deleteLater()
		self.mainLayout.removeWidget(self.MainBodyBox)

	def createApp(self):
		self.AppOption = QGroupBox()
		self.StartLayout = QHBoxLayout()

		self.ConnectButton = QPushButton("&Connect to DB")
		self.ConnectButton.clicked.connect(self.connectDB)

		self.BackButton = QPushButton("&Back")
		self.BackButton.clicked.connect(self.sendBackSignal)
		self.BackButton.clicked.connect(self.closeWindow)
		self.BackButton.clicked.connect(self.creatStartWindow)

		self.FinishButton = QPushButton("&Finish")
		self.FinishButton.setDefault(True)
		self.FinishButton.clicked.connect(self.closeWindow)

		self.StartLayout.addStretch(1)
		self.StartLayout.addWidget(self.ConnectButton)
		self.StartLayout.addWidget(self.BackButton)
		self.StartLayout.addWidget(self.FinishButton)
		self.AppOption.setLayout(self.StartLayout)

		self.mainLayout.addWidget(self.AppOption, sum(self.GroupBoxSeg[0:2]), 0, self.GroupBoxSeg[2], 1)

	def destroyApp(self):
		self.AppOption.deleteLater()
		self.mainLayout.removeWidget(self.AppOption)

	def closeWindow(self):
		self.close()

	def creatStartWindow(self):
		if self.backSignal == True:
			self.master.openNewTest()

	def occupied(self):
		self.master.ProcessingTest = True

	def release(self):
		self.run_process.kill()
		self.master.ProcessingTest = False
		self.master.NewTestButton.setDisabled(False)
		self.master.LogoutButton.setDisabled(False)
		self.master.ExitButton.setDisabled(False)

	def refreshHistory(self):
		self.dataList = getLocalRemoteTests(self.connection, self.info[0])
		self.proxy = QtTableWidget(self.dataList)
		self.view.setModel(self.proxy)
		self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.view.update()

	def sendBackSignal(self):
		self.backSignal = True

	def sendProceedSignal(self):
		self.proceedSignal = True
		self.runNext.set()

	def connectDB(self):
		pass

	def configTest(self):
		self.input_dir = ""
		if self.currentTest == "" and isCompositeTest(self.info[1]):
			testName = CompositeList[self.info[1]][0]
		elif self.currentTest ==  None:
			testName = self.info[1]
		else:
			testName = self.currentTest

		self.output_dir, self.input_dir = ConfigureTest(testName, self.info[0], self.output_dir, self.input_dir, self.connection)

		if self.input_dir == "":
			if self.config_file == "":
				config_file = os.environ.get('GUI_dir')+ConfigFiles.get(testName, "None")
				SetupXMLConfigfromFile(config_file,self.output_dir)
				#QMessageBox.information(None,"Noitce", "Using default XML configuration",QMessageBox.Ok)
			else:
				SetupXMLConfigfromFile(self.config_file,self.output_dir)
		else:
			if self.config_file != "":
				SetupXMLConfigfromFile(self.config_file,self.output_dir)
			else:
				SetupXMLConfig(self.input_dir,self.output_dir)

		if self.input_dir == "":
			if self.rd53_file == "":
				rd53_file = os.environ.get('Ph2_ACF_AREA')+"/settings/RD53Files/CMSIT_RD53.txt"
				SetupRD53ConfigfromFile(rd53_file,self.output_dir)
			else:
				SetupRD53ConfigfromFile(self.rd53_file,self.output_dir)
		else:
			if self.rd53_file == "":
				SetupRD53Config(self.input_dir,self.output_dir)
			else:
				SetupRD53ConfigfromFile(self.rd53_file,self.output_dir)

		self.rd53_file = ""
		self.config_file = ""
		return

	def customizeTest(self):
		print("Customize configuration")
		self.CustomizedButton.setDisabled(True)
		self.ResetButton.setDisabled(True)
		self.RunButton.setDisabled(True)
		self.CustomizedWindow = QtCustomizeWindow(self)
		self.CustomizedButton.setDisabled(False)
		self.ResetButton.setDisabled(False)
		self.RunButton.setDisabled(False)
		
	def resetConfigTest(self):
		self.input_dir = ""
		self.output_dir = ""
		self.config_file = ""
		self.rd53_file  = ""

	def runTest(self):
		#self.ControlLayout.removeWidget(self.RunButton)
		#self.RunButton.deleteLater()
		#self.ControlLayout.addWidget(self.ContinueButton,1,0,1,1)
		testName = self.info[1]

		self.input_dir = self.output_dir
		self.output_dir = ""

		if isCompositeTest(testName):
			#Fixme: threading make GUI freeze
			#self.runAllTests = threading.Thread(target=self.runCompositeTest(testName))
			#self.runAllTests.start()
			self.runCompositeTest(testName)
		elif isSingleTest(testName):
			self.runSingleTest(testName)
		else:
			QMessageBox.information(None, "Warning", "Not a valid test", QMessageBox.Ok)
			return

	def runCompositeTest(self,testName):
		if self.haltSignal:
			return
		if self.testIndexTracker == len(CompositeList[self.info[1]]):
			return
		testName = CompositeList[self.info[1]][self.testIndexTracker]
		self.runSingleTest(testName)


	def runSingleTest(self,testName):	
		self.currentTest = testName
		self.configTest()
		self.RunButton.setDisabled(True)
		#self.ContinueButton.setDisabled(True)
		#self.run_process.setProgram()
		self.run_process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
		self.run_process.start("ping",["-c","5","www.google.com"])
		#self.run_process.waitForFinished()
		self.displayResult()
		

		#Question = QMessageBox()
		#Question.setIcon(QMessageBox.Question)
		#Question.setWindowTitle('SingleTest Finished')
		#Question.setText('Save current result and proceed?')
		#Question.setStandardButtons(QMessageBox.No| QMessageBox.Save | QMessageBox.Yes)
		#Question.setDefaultButton(QMessageBox.Yes)
		#customizedButton = Question.button(QMessageBox.Save)
		#customizedButton.setText('Save Only')
		#reply  = Question.exec_()

		#if reply == QMessageBox.Yes or reply == QMessageBox.Save:
		#	self.saveTest()
		#if reply == QMessageBox.No or reply == QMessageBox.Save:
		#	self.haltSignal = True
		self.refreshHistory()
		self.finishSingal = False


	def abortTest(self):
		reply = QMessageBox.question(None, "Abort", "Are you sure to abort?", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)

		if reply == QMessageBox.Yes:
			self.run_process.kill()
			self.haltSignal = True
			self.sendProceedSignal()
		else:
			return

	def validateTest(self):
		self.grades.append(random.uniform(50, 100))
		self.StatusCanvas.renew()
		self.StatusCanvas.update()
		self.HistoryLayout.removeWidget(self.StatusCanvas)
		self.HistoryLayout.addWidget(self.StatusCanvas)


	def saveTest(self):
		#if self.parent.current_test_grade < 0:
		if self.run_process.state() == QProcess.Running:
			QMessageBox.critical(self,"Error","Process not finished",QMessageBox.Ok)
			return

		if isActive(self.connection):
			try:
				os.system("cp {0}/test/Results/Run*.root {1}/".format(os.environ.get("Ph2_ACF_AREA"),self.output_dir))
				getfile = subprocess.run('ls -alt {0}/test/Results/Run*.root'.format(self.output_dir), shell=True, stdout=subprocess.PIPE)
				filelist = getfile.stdout.decode('utf-8')
				outputfile = filelist.rstrip('\n').split('\n')[-1].split(' ')[-1]
				# Fixme. to be decided
				DQMFile = self.output_dir + "/" + outputfile
				time_stamp = datetime.fromisoformat(self.output_dir.split('_')[-2])

				testing_info = [self.info[0], self.parent.TryUsername, self.currentTest, time_stamp.strftime('%Y-%m-%d %H:%M:%S.%f'), self.grade, DQMFile]
				insertTestResult(self.connection, testing_info)
				# fixme 
				#database.createTestEntry(testing_info)
			except:
				QMessageBox.information(self,"Error","Unable to save to DB", QMessageBox.Ok)
				return
		self.refreshHistory()


	#######################################################################
	##  For result display
	#######################################################################
	def displayResult(self):
		#Fixme: remake the list
		updatePixmap = QPixmap("test_plots/pixelalive_ex.png").scaled(QSize(self.DisplayW,self.DisplayH), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.DisplayLabel.setPixmap(updatePixmap)

	def clickedOutputItem(self, qmodelindex):
		#Fixme: Extract the info from ROOT file
		item = self.ListWidget.currentItem()
		print(item.text())

	#######################################################################
	##  For real-time terminal display
	#######################################################################

	@QtCore.pyqtSlot()
	def on_readyReadStandardOutput(self):
		text = self.run_process.readAllStandardOutput().data().decode()
		self.ConsoleView.append(text)

	@QtCore.pyqtSlot()
	def on_finish(self):
		self.RunButton.setDisabled(False)
		self.RunButton.setText("&Continue")
		self.finishSingal = True
		self.testIndexTracker += 1
		if isCompositeTest(self.info[1]):
			if self.testIndexTracker == len(CompositeList[self.info[1]]):
				self.RunButton.setText("&Finish")
		#self.ContinueButton.setDisabled(False)
		self.validateTest()

	#######################################################################
	##  For real-time terminal display
	#######################################################################

	def closeEvent(self, event):
		if self.processingFlag == True:
			event.ignore()
		
		else:
			reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to quit the test?',
				QMessageBox.No | QMessageBox.Yes, QMessageBox.No)

			if reply == QMessageBox.Yes:
				self.release()
				event.accept()
			else:
				self.backSignal = False
				event.ignore()


		


		