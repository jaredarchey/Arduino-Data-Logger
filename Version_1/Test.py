import wx, os, sys, serial
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class Main_Frame(wx.Frame):
	"""Main Window of the data logger application"""

	def __init__(self, parent, title, size):
		wx.Frame.__init__(self, parent, title=title, size=size)
		self.Centre()
		self.dataDirectory = os.getcwd() + '/Data/'

		self.recorder = Recorder(self, port='/dev/ttyACM0', baud=115200)

		self.lastFile = None
		self.currentFile = None
		self.hasData = False
	
		self.Menus()			

		Main_Panel(self)

		self.Show()


	def Menus(self):
	    self.menubar = wx.MenuBar()

	    self.fileMenu = wx.Menu()
	    self.openMenu = wx.Menu()

	    for i, file in enumerate(os.listdir(self.dataDirectory)):
	    	added = self.openMenu.Append(201+i, file, file)
	    	self.Bind(wx.EVT_MENU, self.selectFile, added)

	    self.fileMenu.AppendMenu(101, 'Open', self.openMenu) #Add the open submenu to the file menu of the menubar
	    self.fileNew = self.fileMenu.Append(103, 'New')
	    self.fileView = self.fileMenu.Append(102, 'View')
	    self.fileRecord = self.fileMenu.Append(104, 'Record')

	    self.Bind(wx.EVT_MENU, self.newFile, self.fileNew)
	    self.Bind(wx.EVT_MENU, self.viewFile, self.fileView)
	    self.Bind(wx.EVT_MENU, self.recordFile, self.fileRecord)

	    self.menubar.Append(self.fileMenu, 'File') #Add the file menu to menubar

	    self.SetMenuBar(self.menubar)

	def newFile(self, evt): #File > New
		self.updateFiles(None)
		NewFile_Window(self)

	def addFile(self, file): #When a new file is created and saved, it is then added to the file list
		added = self.openMenu.Append(201+self.openMenu.GetMenuItemCount(), file)
		self.Bind(wx.EVT_MENU, self.selectFile, added)

	def selectFile(self, evt): #Selects the current file
		fileName = self.GetMenuBar().FindItemById(evt.GetId()).GetLabel()
		path = self.dataDirectory + fileName
		self.updateFiles(File(path))   #Sets the current file type None, Data, New
		self.recorder.setFile(self.currentFile) #Give the recorder the current file
		print self.currentFile

	def updateFiles(self, file):
		assert (isinstance(file, File) or file == None), "File must be file object of NoneType"
		self.lastFile = self.currentFile
		if str(file) != "None":
			try:
				file.openFile()     #Opens the current file
			except TypeError:
				pass
		self.currentFile = file
		if isinstance(file, File):
			self.hasData = file.hasData()
		else:
			self.hasData = False

	def viewFile(self, evt):
		if self.currentFile != None:
			if self.currentFile.hasData():
				view = View(self)
				view.giveData(self.currentFile.data)

	def recordFile(self, evt):
		if isinstance(self.currentFile, File):
			record = Recording(self)

	def getFile(self):
		return self.currentFile

class Main_Panel(wx.Panel): #This is where all widgets are going to be placed

	def __init__(self, parent):

		wx.Panel.__init__(self, parent)

		self.graph = Graph(self)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.graph.addObj(), proportion=12, flag=wx.EXPAND)
		self.SetSizer(sizer)
		self.Fit()

class Graph(object):

	def __init__(self, panel):
		self.panel = panel

		self.figure = plt.Figure(figsize=(2,2))
		self.axes = self.figure.add_subplot(111)
		self.canvas = FigureCanvas(self.panel, -1, self.figure)

	def setFile(self, file):
		#Check file for File instance and 
		self.lastFile = self.currentFile
		self.currentFile = file

	def setXaxis(self, lim):
		pass

	def setYaxis(self, lim):
		pass

	def setPlotType(self, plotType):
		pass

	def checkState(self):
		pass

	def addObj(self):
		return self.canvas

class File_Selection(object):

	def __init__(self, panel):
		self.panel = panel

		self.selector = wx.ComboBox(self.panel, choices=["~~New File"] + os.listdir(os.getcwd() + '/Data/'), #current directory
								    style=wx.CB_READONLY, value="Select a file to record to")
		self.selector.Bind(wx.EVT_COMBOBOX, self.selectFile)

	def addObj(self):
		return self.selector

	def selectFile(self, evt):
		pass

class File(object):

	def __init__(self, path):

		self.path = path
		self.name = self.path.split('/')[-1]
		self.type = "Empty"

	def openFile(self):
		try:
			self.data = pd.DataFrame.from_csv(self.path)
			self.type = "Data"
		except IOError:
			raise TypeError, 'File ' + self.name + ' has no data\nIf file was newly created use file.newFile(columns)'

	def hasData(self):
		if self.type == "Data":
			return True
		else:
			return False

	def newFile(self, columns):
		self.type = "New"
		self.columns = columns
		self.numColumns = len(self.columns)

	def setIndex(self, index):
		self.index = index

	def canRecord(self):
		pass

	def addData(self, data):
		pass

	def save(self):
		if isinstance(self.data, pd.DataFrame):
			self.data.to_csv(self.path)

	def __str__(self):
		return self.path

	"""def getData(self):
		if self.name in os.listdir(self.directory + self.dataExt):
			self.data = pd.DataFrame.from_csv(self.directory + self.dataExt + str(self.name));
			self.columns =  []
			setCol = ['sendTime', 'receiveTime', 'dataPoints']
			for value in self.data.columns.values:
				if value not in setCol:
					self.columns.append(value)
		else:
			self.data = None"""

class Recorder(object): 
	"""Initializing binds the wx.Timer objects to the wx.Frame object,
	   assigns communication constants, opens serial port """

	def __init__(self, frame, port='/dev/ttyACM0', baud=115200):

		self.frame = frame 
		self.file = None
		self.value = None
		self.parameter = None
		self.index = None

		self.port = port
		self.baud = baud

		self.statHeader = ['sendTime', 'receiveTime', 'dataPoints']
		try:
			self.ser = serial.Serial(self.port, self.baud, timeout=1)
		except serial.SerialException:
			self.ser = None
		self.initDelay = 5.0
		self.initChar = "s"
		self.msg = { "send" : "0", "end" : "1" }

		self.sendTimer = wx.Timer(self.frame)
		self.receiveTimer = wx.Timer(self.frame)

		self.frame.Bind(wx.EVT_TIMER, self.send, self.sendTimer) #These events handle transmission of the data buffer
		self.frame.Bind(wx.EVT_TIMER, self.receive, self.receiveTimer)

	def dataTransfer(self):
		"""File has to be file object with test index, columns, name, value needs to be int"""
		if self.ser == None:
			print "No open serial port" + " " + self.port + " at " + str(self.baud) + " baudrate"
			return
		self.busy = wx.BusyCursor()
		self.sendTime = []
		self.receiveTime = []
		self.dataPoints = []
		self.__dataStr = ''
		self.pointsReceived = 0
		if len(self.file.columns) > 10:
			self.transmitDelay = 2.0
		if len(self.file.columns) <= 10:
			self.transmitDelay = 1.0

		self.ser.write(self.initChar)
		self.startTime = time.time() + (self.initDelay / 1000.0)
		self.sendTimer.Start(self.initDelay) #Begins initial transmission

	def send(self, evt):
		recTime = time.time() - self.startTime #Sends and receives data for value seconds
		if self.parameter == 'Seconds':
			if recTime < int(self.value):
				self.ser.write(self.msg["send"])
				self.sendTime.append(recTime)
				self.receiveTimer.Start(self.transmitDelay)

			elif recTime >= int(self.value):
				self.ser.write(self.msg["end"])
				data = self.toDataFrame()
				self.file.addData(data)               #Save file after this
				del self.busy

		elif self.parameter == 'Data Points': #Runs until value data points are received
			if self.pointsReceived < int(self.value):
				self.ser.write(self.msg["send"])
				self.sendTime.append(recTime)
				self.receiveTimer.Start(self.transmitDelay)

			elif self.pointsReceived >= int(self.value):
				self.ser.write(self.msg["end"])
				data = self.toDataFrame()
				self.file.addData(data)
				del self.busy

		self.sendTimer.Stop()

	def receive(self, evt): #Reads from arduino and adds to a string which is a private attribute
		received = self.ser.read(self.ser.inWaiting())
		self.receiveTime.append(time.time() - self.startTime)
		self.__dataStr += str(received)
		self.pointsReceived = len(re.findall('\r\n', self.__dataStr))
		self.dataPoints.append(self.pointsReceived)

		self.sendTimer.Start(self.transmitDelay)
		self.receiveTimer.Stop()

	def toDataFrame(self):
		self.str = self.__dataStr.split('\r\n')
		arduino = []
		for packet in self.str:
			pack = packet.split('|')
			if not '' in pack and len(pack) == len(self.file.columns):
				arduino.append(pack)
		if len(arduino) > 0:
			self.receiveTime = self.receiveTime[0:len(arduino)] 
			self.sendTime = self.sendTime[0:len(arduino)] 
			self.dataPoints = self.dataPoints[0:len(arduino)]
			if not len(self.receiveTime) == len(self.sendTime) == len(self.dataPoints) == len(arduino):
				arduino = arduino[0:len(self.sendTime)]
			trueData = []
			for i, row in enumerate(arduino):
				part = row
				part.append(self.sendTime[i])
				part.append(self.receiveTime[i])
				part.append(self.dataPoints[i])
				trueData.append(part)
			data = pd.DataFrame(data=trueData, index=[self.index]*len(arduino), columns=self.file.columns + self.statHeader)
			return data
		else:
			print 'File columns do not match columns received, check if arduino is sending ' + str(len(self.file.columns)) + ' columns.'
			self.ser.read(self.ser.inWaiting())
			return None

	def save(self):
		self.file.save()

	def setParameter(self, parameter):
		self.parameter = parameter

	def setValue(self, value):
		self.value = value

	def setIndex(self, index):
		self.index = index

	def setFile(self, file):
		self.file = file

	def __str__(self):
		return str(self.file) + "\nParameter: " + str(self.parameter) + "\nValue: " + str(self.value) + "\nPort: " + str(self.port) + "\nBaud: " + str(self.baud)

	def canRecord(self):
		if isinstance(self.file, File) and self.value != None and self.parameter != None and self.index != None:
			return True
		else:
			return False

class NewFile_Window(wx.Frame):

	def __init__(self, parent, title="New File", size=(200,100)):
		wx.Frame.__init__(self, parent, title=title, size=size)
		self.parent = parent

		self.name = None
		self.columns = None

		sizer = wx.BoxSizer(wx.VERTICAL)
		panel = wx.Panel(self)
		self.valueEntry = wx.TextCtrl(panel, value='File Name', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.columnEntry = wx.TextCtrl(panel, value='Column Names', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER|wx.TE_MULTILINE)
		self.createNew = wx.Button(panel, label='Create File')
		self.valueEntry.Bind(wx.EVT_SET_FOCUS, self.erase)
		self.valueEntry.Bind(wx.EVT_TEXT_ENTER, self.giveName)
		self.columnEntry.Bind(wx.EVT_SET_FOCUS, self.erase)
		self.columnEntry.Bind(wx.EVT_TEXT_ENTER, self.giveCol)
		self.createNew.Bind(wx.EVT_BUTTON, self.createFile)
		self.createNew.Enable(False)

		sizer.Add(self.valueEntry, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.columnEntry, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.createNew, proportion=1, flag=wx.EXPAND)

		panel.SetSizer(sizer)

		self.Centre()

		self.Show()

	def erase(self, evt):
		evt.EventObject.SetValue('')

	def giveName(self, evt):
		value = evt.EventObject.GetValue()
		if self.__nameCheck(value):
			self.name = value
		else:
			self.name = None
		evt.EventObject.SetValue('')
		self.canCreate() 

	def giveCol(self, evt):
		value = evt.EventObject.GetValue()
		cols = value.split(' ')
		self.columns = cols
		evt.EventObject.SetValue('')
		self.canCreate()

	def createFile(self, evt):
		self.parent.updateFiles(File(self.parent.dataDirectory + self.name))
		self.parent.currentFile.newFile(self.columns)
		self.parent.addFile(self.parent.currentFile.name)
		self.Close()

	def canCreate(self):
		if self.name != None and self.columns != None:
			self.createNew.Enable(True)
			return True
		else:
			self.createNew.Enable(False)
			return False

	def __nameCheck(self, name):
		if ' ' in name:
			return False
		else:
			return True

class View(wx.Frame):     

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, title="View Data", size=(600,600))

		self.Centre()													

		self.panel = wx.Panel(self)
		self.sheet = wx.grid.Grid(self.panel) 
		sizer = wx.BoxSizer(wx.HORIZONTAL)   
		sizer.Add(self.sheet, proportion=1, flag=wx.EXPAND|wx.ALL) 

		self.panel.SetSizer(sizer)

		self.Show()

	def giveData(self, data):
		assert(isinstance(data, pd.DataFrame)), "Data must be in a pandas dataframe to use giveData"
		self.clear()
		self.sheet.CreateGrid(len(data.index.values), len(data.columns.values))
		for i, header in enumerate(data.columns.values):
			self.sheet.SetColLabelValue(i, str(header))
		for i, index in enumerate(data.index.values):
			self.sheet.SetRowLabelValue(i, str(index))
		for i, row in enumerate(data.as_matrix()):
			for j, num in enumerate(row):
				self.sheet.SetCellValue(i, j, str(num))

	def clear(self):
		self.sheet.ClearGrid()

class Recording(wx.Frame):
	"""This page is responsible for recording data to a file 
	   created by the new file page or a file in the /Data/ folder"""

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, title="Record Data", size=(200,200))

		self.parent = parent
		self.panel = wx.Panel(self)
                                     
		sizer = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)

		"""Set attributes parameter, value, and test index to recorder object"""

		self.paramSelection = wx.RadioBox(self.panel, label='Recording Type', choices=['Seconds', 'Data Points'], style=wx.RA_SPECIFY_ROWS)
		self.valueEntry = wx.TextCtrl(self.panel, value='Value', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.indexEntry = wx.TextCtrl(self.panel, value='Index', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.record = wx.Button(self.panel, label="Record")
		self.saveRec = wx.Button(self.panel, label="Save")

		self.paramSelection.Bind(wx.EVT_RADIOBOX, self.updateParameter)
		self.valueEntry.Bind(wx.EVT_TEXT_ENTER, self.addValue)
		self.valueEntry.Bind(wx.EVT_SET_FOCUS, self.erase) 
		self.indexEntry.Bind(wx.EVT_TEXT_ENTER, self.addIndex)
		self.indexEntry.Bind(wx.EVT_SET_FOCUS, self.erase) 
		self.record.Bind(wx.EVT_BUTTON, self.beginRecording)
		self.saveRec.Bind(wx.EVT_BUTTON, self.save)
		self.record.Enable(False)
		self.saveRec.Enable(False)
		self.hasData()

		sizer.Add(self.paramSelection, proportion=2, flag=wx.EXPAND)
		hbox1.Add(self.valueEntry, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.indexEntry, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.record, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.saveRec, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox1, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox2, proportion=1, flag=wx.EXPAND)

		self.panel.SetSizer(sizer)

		self.Centre()
		self.Show()

	def updateParameter(self, evt):
		self.parent.recorder.setParameter(evt.EventObject.GetStringSelection())
		self.parent.recorder.setValue(None)
		self.isReady()
		self.hasData()

	def addValue(self, evt):
		textEntry = evt.EventObject
		if str(textEntry.GetValue()).isdigit():
			self.parent.recorder.setValue(str(textEntry.GetValue()))
		textEntry.SetValue('')
		self.isReady()
		self.hasData()

	def addIndex(self, evt):
		textEntry = evt.EventObject
		self.parent.recorder.setIndex(str(textEntry.GetValue()))
		self.isReady()
		self.hasData()
		evt.EventObject.SetValue('')

	def beginRecording(self, evt):
		self.recorder.dataTransfer()

	def save(self, evt):
		self.recorder.save()

	def isReady(self):
		if self.parent.recorder.canRecord():
			self.record.Enable(True)
		else:
			self.record.Enable(False)

	def hasData(self):
		if isinstance(self.parent.recorder.file.data, pd.DataFrame):
			self.saveRec.Enable(True)
		else:
			self.saveRec.Enable(False)

	def erase(self, evt):
		evt.EventObject.SetValue('')

app = wx.App()
Main_Frame(None, "Test", (1000,600))
app.MainLoop()