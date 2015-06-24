import wx, serial, time, re
import numpy as np
from File import *

class Recorder(object): 
	"""Initializing binds the wx.Timer objects to the wx.Frame object,
	   assigns communication constants, opens serial port """

	def __init__(self, port='/dev/ttyACM0', baud=115200):
		"""The file can only be set by the menubar, value parameter and index are only on the recorder ctrl
		   The recorder object needs to be an attribute of the main window"""

		self.__file = None
		self.__value = None
		self.__parameter = 'Seconds'
		self.__index = 0

		self.port = port
		self.baud = baud
		self.hasData = False
		self.initDelay = 5.0
		self.initChar = "s"
		self.msg = { "send" : "0", "end" : "1" }
		self.ser = self.__checkSerial()
		self.statHeader = ['receiveTime']

	def attach(self, ctrl): #RecordCtrl attaches itself to the recorder on initialization
		assert(isinstance(ctrl, RecordCtrl))
		self.ctrl = ctrl
		self.sendTimer = wx.Timer(self.ctrl)
		self.receiveTimer = wx.Timer(self.ctrl)
		self.ctrl.Bind(wx.EVT_TIMER, self.__send, self.sendTimer) #These events handle transmission of the data buffer
		self.ctrl.Bind(wx.EVT_TIMER, self.__receive, self.receiveTimer)

	def setParameter(self, parameter):
		self.__parameter = parameter

	def setValue(self, value):
		self.__value = value

	def setIndex(self, index):
		self.__index = index

	def setFile(self, file):
		self.__file = file
		if hasattr(file, "data"):
			self.hasData = True
			self.__index = np.max(self.__file.data.index.values) + 1
		else:
			self.hasData = False
			self.__index = 0

	def canRecord(self): #For recorCtrl
		if isinstance(self.__file, File) and self.__value != None and self.__parameter != None and self.ser != None:
			return True
		else:
			return False

	def canSave(self): #For recordCtrl
		return self.hasData

	def save(self):
		file = self.__file.save()
		return file

	def begin(self):
		"""Begins the initial transmission of data after value and index are specified"""
		if not self.canRecord(): return

		self.receiveTime = []
		self.__dataStr = ''
		self.pointsReceived = 0
		self.transmitDelay = (1.0 if len(self.__file.columns) <= 10 else 2.0)

		self.ser.write(self.initChar)
		self.startTime = time.time() + (self.initDelay / 1000.0)
		self.sendTimer.Start(self.initDelay) #Begins initial transmission

	def __send(self, evt):
		if self.__parameter == 'Seconds':
			self.__sendMsg() if time.time()-self.startTime < int(self.__value) else self.__endMsg()
		elif self.__parameter == 'Data Points':
			self.__sendMsg() if self.pointsReceived < int(self.__value) else self.__endMsg()

		self.sendTimer.Stop()

	def __sendMsg(self):
		self.ser.write(self.msg["send"])
		self.receiveTimer.Start(self.transmitDelay)

	def __endMsg(self):
		self.ser.write(self.msg["end"])
		data = self.__toDataFrame()
		if isinstance(data, pd.DataFrame):
			self.__file.addData(data)               #Save file after this
			self.hasData = True
			if hasattr(self, "ctrl"): 
				self.ctrl.adjustButtons()
				del self.ctrl.busy
			print "Recording index '" + str(self.__index) + "' complete"
			self.__index += 1
		else:
			print 'File columns do not match columns received, check if arduino is sending ' + str(len(self.__file.columns)) + ' columns.'

	def __receive(self, evt): #Reads from arduino and adds to a string which is a private attribute
		self.receiveTime.append(time.time() - self.startTime)
		self.__dataStr += str(self.ser.read(self.ser.inWaiting()))
		self.pointsReceived = len(re.findall('\r\n', self.__dataStr))

		self.sendTimer.Start(self.transmitDelay)
		self.receiveTimer.Stop()

	def __checkSerial(self): #Checks to see if a serial port is open
		try:
			ser = serial.Serial(self.port, self.baud, timeout=1)
			print "\nRecorder initialized\n\nPort: " + self.port + "\nBaudrate: " + str(self.baud)
		except serial.SerialException:
			print "\nNo open serial port" + " " + self.port + " at " + str(self.baud) + " baudrate"
			ser = None
		return ser

	def __toDataFrame(self): #Converts the dataStr to a dataframe and adds receive time column
		arduino = []
		for packet in self.__dataStr.split('\r\n'):
			pack = packet.split('|')
			if self.__checkPack(pack):
				arduino.append(pack) #Check each value in the packet
		if len(arduino) > 0: #If this is false, an incorrect number of columns was sent
			data = pd.DataFrame(data=arduino, index=[self.__index]*len(arduino), columns=self.__file.columns)
			return data
		else:
			self.ser.read(self.ser.inWaiting())
			return None

	def __checkPack(self, pack): #Checks each packet of data sent from arduino
		safe = True
		for val in pack:
			if not val.isdigit() or len(pack) < len(self.__file.columns):
				safe = False
		return safe

	def __str__(self):
		return str(self.__file) + "\nParameter: " + str(self.parameter) + "\nValue: " + str(self.value) + "\nPort: " + str(self.port) + "\nBaud: " + str(self.baud)

class RecordCtrl(wx.Frame):
	"""These are the widgets which interact with the parameters of the recorder"""

	def __init__(self, parent):
		assert (isinstance(parent, wx.Frame)), "Parent must be a wx.Frame object"
		assert (hasattr(parent, "recorder")), "Window must have a recorder object named recorder"
		wx.Frame.__init__(self, parent, title="Record Data", size=(200,200))

		self.parent = parent
		self.recorder = self.parent.recorder
		self.panel = wx.Panel(self)
                                     
		sizer = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)

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
		self.adjustButtons()

		sizer.Add(self.paramSelection, proportion=2, flag=wx.EXPAND)
		hbox1.Add(self.valueEntry, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.indexEntry, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.record, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.saveRec, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox1, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox2, proportion=1, flag=wx.EXPAND)

		self.panel.SetSizer(sizer)

		self.recorder.attach(self)
		self.Bind(wx.EVT_CLOSE, self.onClose, self)
		self.Centre()
		self.Show()

	def onClose(self, evt):
		self.recorder.setValue(None)
		self.Destroy()

	def updateParameter(self, evt):
		self.recorder.setParameter(evt.EventObject.GetStringSelection())
		self.recorder.setValue(None)
		self.adjustButtons()

	def addValue(self, evt):
		textEntry = evt.EventObject
		if str(textEntry.GetValue()).isdigit():
			self.recorder.setValue(str(textEntry.GetValue()))
		textEntry.SetValue('')
		self.adjustButtons()

	def addIndex(self, evt):
		textEntry = evt.EventObject
		self.recorder.setIndex(str(textEntry.GetValue()))
		self.adjustButtons()
		evt.EventObject.SetValue('')

	def beginRecording(self, evt): #Begins the recording if the parameters are set
		self.busy = wx.BusyCursor()
		self.recorder.begin()

	def save(self, evt):        #Called through the parent to update the currentFile and the graph file
		self.parent.saveFile() 
		self.parent.setFile(self.parent.getFile())

	def adjustButtons(self):
		if self.recorder.canRecord():
			self.record.Enable(True)
		else:
			self.record.Enable(False)
		if self.recorder.canSave():
			self.saveRec.Enable(True)
		else:
			self.saveRec.Enable(False)

	def erase(self, evt):
		evt.EventObject.SetValue('')
