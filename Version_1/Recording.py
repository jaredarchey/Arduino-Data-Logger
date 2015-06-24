import File, wx, serial, time, re
import numpy as np
import pandas as pd

class RecordObject(object): 
	"""Initializing binds the wx.Timer objects to the wx.Frame object,
	   assigns communication constants, opens serial port """

	def __init__(self, parent, File, port='/dev/ttyACM0', baud=115200):

		self.ready = False
		self.parent = parent
		self.frame = self.parent.frame
		self.file = File
		self.port = port
		self.baud = baud
		self.parameter = 'Seconds'
		self.value = None

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
				self.parent.hasData()
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
				self.parent.hasData()
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
			data = pd.DataFrame(data=trueData, index=[self.file.testIndex]*len(arduino), columns=self.file.columns + self.statHeader)
			return data
		else:
			print 'File columns do not match columns received, check if arduino is sending ' + str(len(self.file.columns)) + ' columns.'
			self.ser.read(self.ser.inWaiting())
			return None

	def save(self):
		self.file.save()

	def updateParameter(self, parameter):
		self.parameter = parameter
		self.isReady()

	def updateValue(self, value):
		self.value = value
		self.isReady()

	def updateIndex(self, index):
		self.file.setIndex(index)
		self.isReady()

	def isReady(self):
		if self.value != None and self.file.testIndex != None:
			self.ready = True
		else: 
			self.ready = False


	def __str__(self):
		return str(self.file) + "\nParameter: " + str(self.parameter) + "\nValue: " + str(self.value) + "\nPort: " + str(self.port) + "\nBaud: " + str(self.baud)

	def __checkInput(self):
		try:
			if isinstance(self.file, File.File):
				str(len(self.file.columns))
				self.file.testIndex
			else:
				raise ValueError, "File Argument Isnt File Object"
			int(self.value)
			self.parameter in ['Seconds', 'Data Points']
		except:
			raise ValueError, "Incorrect inputs to Recording.dataTransfer"





		
		