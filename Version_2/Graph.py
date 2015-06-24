import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class Graph(object):

	def __init__(self, panel):
		self.panel = panel

		self.figure = plt.Figure(figsize=(2,2))
		self.axes = self.figure.add_subplot(111)
		self.canvas = FigureCanvas(self.panel, -1, self.figure)

	def setPlotType(self, plotType):
		self.plotType = plotType

	def setFile(self, file):
		self.file = file

	def setXlabel(self, label):
		self.xLabel = label

	def setYlabel(self, label):
		self.yLabel = label

	def setXrange(self, range):
		self.xRange = range

	def setYrange(self, range):
		self.yRange = range

	def updatePlot(self):
		self.axes.clear()
		if self.plotType != 'Bar':
			x,y = self.__getCoords()
			if x == None and y == None:
				self.canvas.draw()
				return
			if self.plotType == 'Scatter':
				self.axes.scatter(x,y)
			elif self.plotType == 'Line':
				pass

			self.axes.axis([int(self.xRange[0]), int(self.xRange[1]), int(self.yRange[0]), int(self.yRange[1])])

		elif self.plotType == 'Bar':
			pass

		self.canvas.draw()

	def canPlot(self):
		if self.plotType == 'Bar':
			if self.xLabel != None:
				return True
			else:
				return False
		else:
			if self.xLabel != None and self.yLabel != None:
				return True
			else:
				return False

	def __getCoords(self):
		columns = ['testIndex']
		for val in self.file.columns:
			columns.append(val)
		if self.xLabel in columns and self.yLabel in columns:
			if self.xLabel == 'testIndex':
				x = self.__toFloat(self.file.data.index.values)
			else:
				x = self.__toFloat(self.file.data[str(self.xLabel)])
			if self.yLabel == 'testIndex':
				y = self.__toFloat(self.file.data.index.values)
			else:
				y = self.__toFloat(self.file.data[str(self.yLabel)])
			return x , y
		else:
			return None, None

	def __toFloat(self, data):
		values = []
		for val in data:
			values.append(float(val))
		return values

	def __str__(self):
		return "Plot: " + self.plotType + '\nFile: ' + str(self.file) + '\nxLabel: ' + str(self.xLabel) + '\nxRange: ' + str(self.xRange) +'\nyLabel: ' + str(self.yLabel) + '\nyRange: ' + str(self.yRange)

	def addObj(self):
		return self.canvas