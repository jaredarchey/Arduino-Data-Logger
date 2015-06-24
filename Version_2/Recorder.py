import serial, wx, time, re
import pandas as pd
import numpy as np
from File import *

class Recorder(object): 
	"""Initializing binds the wx.Timer objects to the wx.Frame object,
	   assigns communication constants, opens serial port """

	def __init__(self, frame, port='/dev/ttyACM0', baud=115200):

		self.frame = frame 
		self.file = None
		self.value = None
		self.parameter = 'Seconds'
		self.index = None

		self.port = port
		self.baud = baud

		self.statHeader = ['receiveTime']
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
				if isinstance(data, pd.DataFrame):
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
				if isinstance(data, pd.DataFrame):
					self.file.addData(data)               #Save file after this
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
			if self.__checkPack(pack):
				arduino.append(pack) #Check each value in the packet

		if len(arduino) > 0: #If this is false, an incorrect number of columns was sent
			self.receiveTime = self.receiveTime[0:len(arduino)]
			if not len(self.receiveTime) == len(arduino):
				arduino = arduino[0:len(self.receiveTime)]
			self.__fixTime() #Convert time column to milliseconds

			trueData = [] #Add time column to arduino data
			for i, row in enumerate(arduino):
				part = row
				part.append(self.receiveTime[i])
				trueData.append(part)

			if self.statHeader in self.file.columns: #Find the header of the data frame
				header = self.file.columns
			else:
				header = self.file.columns + self.statHeader

			data = pd.DataFrame(data=trueData, index=[self.index]*len(arduino), columns=header)
			return data

		else:
			print 'File columns do not match columns received, check if arduino is sending ' + str(len(self.file.columns)) + ' columns.'
			self.ser.read(self.ser.inWaiting())
			return None

	def __checkPack(self, pack):
		safe = True
		for val in pack:
			if not val.isdigit() or len(pack) < len(self.file.columns)-1:
				safe = False
		return safe

	def __fixTime(self):
		fixed = []
		for val in self.receiveTime:
			fixed.append(int(np.around(val, decimals=3)*1000))
		self.receiveTime = fixed

	def save(self):
		self.file.save(self.frame)

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