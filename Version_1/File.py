import os
import pandas as pd

class File(object):

	def __init__(self, name, directory):

		self.name = name
		self.directory = directory

		self.data = None
		self.columns = None
		self.testIndex = None
		self.dataExt = '/Data/'

	def getData(self):
		if self.name in os.listdir(self.directory + self.dataExt):
			self.data = pd.DataFrame.from_csv(self.directory + self.dataExt + str(self.name));
			self.columns =  []
			setCol = ['sendTime', 'receiveTime', 'dataPoints']
			for value in self.data.columns.values:
				if value not in setCol:
					self.columns.append(value)
		else:
			self.data = None

	def setName(self, newName):
		self.name = newName

	def setColumns(self, columns):
		self.columns = columns

	def setIndex(self, index):
		self.testIndex = index

	def addData(self, data):
		if isinstance(self.data, pd.DataFrame):
			self.data = self.data.append(data)
		else:
			self.data = data 

	def save(self):
		if isinstance(self.data, pd.DataFrame):
			self.data.to_csv(self.directory + self.dataExt + str(self.name))

	def __str__(self):
		return "Data: " +str(self.data) + "\nColumns: " + str(self.columns) + "\nIndex: " + str(self.testIndex)