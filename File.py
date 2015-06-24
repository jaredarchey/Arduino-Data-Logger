import pandas as pd

class File(object):

	def __init__(self, path, style='Reg', columns=None):

		self.path = path
		self.name = self.path.split('/')[-1]
		self.style = style
		if self.style == 'Reg':
			self.data = pd.DataFrame.from_csv(self.path)
			self.columns = self.data.columns.values
		elif self.style == 'New':
			if columns == None: raise IOError, "New files need a list of columns"
			self.columns = columns

	def openFile(self):
		self.data = pd.DataFrame.from_csv(self.path)
		self.columns = self.data.columns.values

	def addData(self, data):
		self.data = (self.data.append(data) if hasattr(self, "data") else data)
		self.style = "Reg"

	def save(self):
		self.data.to_csv(self.path)
		self.openFile()
		print "Saved " + self.name + "\n" + str(len(self.data.index.values)) + " rows and " + str(len(self.columns)) + " columns\n"
		return self

	def __str__(self):
		return self.path