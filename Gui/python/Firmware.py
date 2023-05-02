from Gui.GUIutils.settings import *

class QtChip():
	def __init__(self):
		self.__chipID = ""
		self.__chipLane = ""
	
	def setID(self, id):
		self.__chipID = str(id)

	def getID(self):
		return self.__chipID

	def setLane(self, lane):
		self.__chipLane = str(lane)
	
	def getLane(self):
		return self.__chipLane


# Dedicated for OpticalGroup and 
class QtModule():
	def __init__(self, **kwargs):
		self.__moduleName = "SerialNumber1"
		self.__moduleID =  "0"
		self.__moduleType = "SingleSCC"
		self.__FMCID = "0"
		self.__OGID = "0"
		self.__chipDict = {}
		for key,value in kwargs.items():
			if key == "id":
				self.__moduleID = str(value)
			if key == "type":
				self.__moduleType = str(value)

		self.setupChips()
	
	def setModuleName(self, name):
		self.__moduleName = name

	def getModuleName(self):
		return self.__moduleName

	def setModuleID(self, id):
		self.__moduleID = id
	
	def getModuleID(self):
		return self.__moduleID

	def setFMCID(self, fmcId):
		self.__FMCID = fmcId

	def getFMCID(self):
		return self.__FMCID

	def setOpticalGroupID(self, ogId):
		self.__OGID = ogId

	def getOpticalGroupID(self):
		return self.__OGID

	def setModuleType(self, fwType):
		if fwType in ModuleType.values():
			self.__moduleType = fwType
		else:
			self.__moduleType = "SingleSCC"
		self.setupChips() 

	def getModuleType(self):
		return self.__moduleType

	def setupChips(self, **kwargs):
		self.__chipDict = {}
		if "chips" in kwargs.keys():
			pass
			return
		for i in ModuleLaneMap[self.__moduleType].keys():
			FEChip = QtChip()
			#FEChip.setID(8)
			LaneID = str(i)
			FEChip.setID(ModuleLaneMap[self.__moduleType][LaneID])
			FEChip.setLane(LaneID)
			self.__chipDict[i] = FEChip
	
	def getChips(self):
		return self.__chipDict

class QtOpticalGroup():
	def __init__(self):
		self.__FMCID = "0"
		self.__OGID = "0"
		self.__moduleDict = {}

	def setFMCID(self, fmcId):
		self.__FMCID = fmcId

	def getFMCID(self):
		return self.__FMCID

	def setOpticalGroupID(self, ogId):
		self.__OGID = ogId

	def getOpticalGroupID(self):
		return self.__OGID

	def setupModule(self, **kwargs):
		self.__moduleDict = {}
		if "module" in kwargs.keys():
			pass
			return
		for i in ModuleLaneMap[self.__moduleType].keys():
			FEChip = QtChip()
			#FEChip.setID(8)
			FEChip.setID(i)
			FEChip.setLane(i)
			self.__chipDict[i] = FEChip
	
	def getChips(self):
		return self.__chipDict

	

class QtBeBoard():
	def __init__(self, boardName = ""):
		self.__boardName= ""
		self.__ipAddress = "0.0.0.0"
		self.__moduleDict = {}
		self.__fpgaConfigName = ""

	def setBoardName(self, name):
		self.__boardName = name

	def getBoardName(self):
		return self.__boardName

	def setIPAddress(self, ipAddress):
		self.__ipAddress = ipAddress
		
	def getIPAddress(self):
		return self.__ipAddress

	def setFPGAConfig(self, fpgaConfig):
		self.__fpgaConfigName = fpgaConfig
		return True
	
	def addModule(self, key, module):
		if module not in self.__moduleDict.values():
			self.__moduleDict[key] = module
			return True
		else:
			return False

	def getAllModules(self):
		return self.__moduleDict

	def getModuleByIndex(self, key):
		if key in self.__moduleDict.keys():
			return self.__moduleDict[key]
		else:
			return None

	def removeModule(self, module):
		for key, item in self.__moduleDict.items():
			if module == item:
				self.__moduleDict.pop(key)
				return  True
		return False

	def removeModuleByKey(self, removeKey):
		for key in self.__moduleDict.keys():
			if removeKey == key:
				self.__moduleDict.pop(key)
				return True
		return False

	def removeAllModule(self):
		self.__moduleDict.clear()
		