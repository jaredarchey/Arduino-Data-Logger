import pandas as pd

class File(object):

	def __init__(self, path):

		self.path = path
		self.name = self.path.split('/')[-1]
		try:
			self.data = pd.DataFrame.from_csv(self.path)
			self.columns = self.data.columns.values
		except IOError:
			pass

	def openFile(self):
		try:
			self.data = pd.DataFrame.from_csv(self.path)
			self.columns = self.data.columns.values
		except IOError:
			raise IOError, 'File ' + self.name + ' has no data\nIf file was newly created use file.newFile(columns)'

	def hasData(self):
		if hasattr(self, "data"):
			return True
		else:
			return False

	def newFile(self, columns):
		self.columns = columns
		self.numColumns = len(self.columns)

	def setIndex(self, index):
		self.index = index

	def addData(self, data):
		if hasattr(self, "data"):
			self.data = self.data.append(data)
		else:
			self.data = data

	def save(self, mainFrame):
		if isinstance(self.data, pd.DataFrame):
			self.data.to_csv(self.path)
		mainFrame.addFile(self.name)

	def __str__(self):
		return self.path