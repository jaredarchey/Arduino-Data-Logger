import wx, re
import numpy as np
from Axis_Range import *
from File import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class PlotPanel(wx.Panel):

	def __init__(self, window):
		wx.Panel.__init__(self, window)

		sizer = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		vbox1 = wx.BoxSizer(wx.VERTICAL)
		vbox2 = wx.BoxSizer(wx.VERTICAL)
		space = wx.BoxSizer(wx.HORIZONTAL)

		plotBox = wx.BoxSizer(wx.VERTICAL)
		ctrlBox = wx.BoxSizer(wx.HORIZONTAL)

		self.toggleParams = {
							 "grid":False,
							 "error":False,
							 "stats":False,
							 "poly":False,
							 "corr":False
							}
		self.graphParams = {
							"file":None,
							"plot":'Scatter',
							"xLabel":None,
							"yLabel":None,
							"xRange":[0,1],
							"yRange":[0,1]
						   }

		self.__polyVal = None

		self.__file = None
		self.__plotType = 'Scatter'
		self.__xLabel = None 
		self.__yLabel = None
		self.__xRange = [0,1]
		self.__yRange = [0,1]

		self.figure = plt.Figure(figsize=(2,2))
		self.axes = self.figure.add_subplot(111)
		self.statusLabels = ["\tStatus_Box", "File: None", "Has_Data: False", "PlotType: Scatter", 
						     "xLabel: None", "yLabel: None", "xLimit: None", "yLimit: None"]

		self.canvas = FigureCanvas(self, -1, self.figure)

		self.xLimit = Axis_Range(self, 'x', self.__xRange[0], self.__xRange[1]) 
		self.yLimit = Axis_Range(self, 'y', self.__yRange[0], self.__yRange[1]) 
		self.xLabel = wx.ComboBox(self, value="X-Axis", choices=[])
		self.yLabel = wx.ComboBox(self, value="Y-Axis", choices=[])
		self.plotChoices = wx.RadioBox(self, label='Graph Style', choices=['Scatter', 'Line', 'Bar'])
		self.toggleGrid = wx.CheckBox(self, label="Toggle Grid")
		self.toggleErr = wx.CheckBox(self, label="Toggle Error: Line Only")
		self.toggleStats = wx.CheckBox(self, label="Toggle Stats: Bar Only")
		self.togglePoly = wx.CheckBox(self, label="Polyfit: Scatter Only")
		self.toggleCorr = wx.CheckBox(self, label="Correlate: Scatter Only")

		self.status = wx.ListBox(self, choices=self.statusLabels)

		self.plotChoices.Bind(wx.EVT_RADIOBOX, self.updateStyle)
		self.xLabel.Bind(wx.EVT_COMBOBOX, self.setX)
		self.yLabel.Bind(wx.EVT_COMBOBOX, self.setY)
		self.toggleGrid.Bind(wx.EVT_CHECKBOX, self.__gridToggle)
		self.toggleErr.Bind(wx.EVT_CHECKBOX, self.__errorToggle)
		self.toggleStats.Bind(wx.EVT_CHECKBOX, self.__statsToggle)
		self.togglePoly.Bind(wx.EVT_CHECKBOX, self.__polyToggle)
		self.toggleCorr.Bind(wx.EVT_CHECKBOX, self.__corrToggle)

		hbox1.Add(self.yLimit, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.canvas, proportion=12, flag=wx.EXPAND)
		plotBox.Add(hbox1, proportion=8, flag=wx.EXPAND)
		hbox2.Add(space, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.xLimit, proportion=12, flag=wx.EXPAND)
		plotBox.Add(hbox2, proportion=1, flag=wx.EXPAND)
		ctrlBox.Add(self.status, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.toggleGrid, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.toggleErr, proportion=1, flag=wx.EXPAND) 
		vbox1.Add(self.toggleStats, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.togglePoly, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.toggleCorr, proportion=1, flag=wx.EXPAND)
		ctrlBox.Add(vbox1, proportion=1, flag=wx.EXPAND)   
		vbox2.Add(self.plotChoices, proportion=1, flag=wx.EXPAND)
		vbox2.Add(self.xLabel, proportion=1, flag=wx.EXPAND)
		vbox2.Add(self.yLabel, proportion=1, flag=wx.EXPAND)
		ctrlBox.Add(vbox2, proportion=1, flag=wx.EXPAND)

		sizer.Add(plotBox, proportion=2, flag=wx.EXPAND)
		sizer.Add(ctrlBox, proportion=1, flag=wx.EXPAND)

		self.SetSizer(sizer)	

	def __gridToggle(self, evt):
		self.toggleParams["grid"] = not self.toggleParams["grid"]
		if self.__canPlot():
			self.__getData()

	def __errorToggle(self, evt):
		self.toggleParams["error"] = not self.toggleParams["error"]
		if self.__canPlot():
			self.__getData()

	def __statsToggle(self, evt):
		self.toggleParams["stats"] = not self.toggleParams["stats"]
		if self.__canPlot():
			self.__getData()

	def __polyToggle(self, evt):
		pass

	def __corrToggle(self, evt):
		pass

	def setRange(self): #Called by sliders and get data, this is the only place __updatePlot is called
		self.__xRange = self.xLimit.getRange()
		self.__yRange = self.yLimit.getRange()
		self.__updateStatus("xLimit", str(self.__xRange))
		self.__updateStatus("yLimit", str(self.__yRange))
		self.__updatePlot()

	def updateStyle(self, evt): #Everytime radiobox changes
		self.__plotType = evt.EventObject.GetStringSelection()
		self.__updateStatus("Plot", self.__plotType)
		if self.__canPlot():
			self.__getData()

	def setX(self, evt): #Everytime x Combo changes
		self.__xLabel = evt.EventObject.GetStringSelection()
		self.__updateStatus("xLabel", self.__xLabel)
		if self.__canPlot():
			self.__getData()

	def setY(self, evt): #Everytime y Combo changes
		self.__yLabel = evt.EventObject.GetStringSelection()
		self.__updateStatus("yLabel", self.__yLabel)
		if self.__canPlot():
			self.__getData()

	def setFile(self, file):
		self.__file = file
		self.graphParams["file"] = file
		self.__updateStatus("File", file.name)
		self.__updateDataLabels()
		self.__xLabel = None
		self.__yLabel = None
		self.__xRange = [0,1]
		self.__yRange = [0,1]
		self.xLabel.SetValue("X-Axis")
		self.yLabel.SetValue("Y-Axis")

	def __updateDataLabels(self):
		if isinstance(self.__file, File):
			self.xLabel.SetItems('')
			self.yLabel.SetItems('')
			self.xLabel.Append('testIndex')
			self.yLabel.Append('testIndex')
			for column in self.__file.columns:
				self.xLabel.Append(column)
				self.yLabel.Append(column)

	def __getData(self): #Only called if the plot is ready
		if self.__xLabel and self.__yLabel == 'testIndex':
			self.__x = list(self.__file.data.index.values)
			self.__y = list(self.__file.data.index.values)
		elif self.__xLabel == 'testIndex':
			self.__x = list(self.__file.data.index.values)
			self.__y = list(self.__file.data[self.__yLabel])
		elif self.__yLabel == 'testIndex':
			self.__x = list(self.__file.data[self.__xLabel])
			self.__y = list(self.__file.data.index.values)
		else:
			self.__x = list(self.__file.data[self.__xLabel])
			self.__y = list(self.__file.data[self.__yLabel])

		if self.__plotType == 'Line': #Line charts plot the average y values for each x value and has an option to show errorbars
			self.__x, self.__y, self.__err = self.__meanYforX()
		elif self.__plotType == 'Bar':
			self.__x, self.__y = self.__freqX()

		self.xLimit.setRange([np.min(self.__x),np.max(self.__x)])
		self.yLimit.setRange([np.min(self.__y),np.max(self.__y)])
		self.setRange() #Updates plot also

	def __updatePlot(self): #Everything below here is for plotting
		"""This is where all the plotting happens"""
		if not self.__canPlot(): return
		self.axes.clear()
		if self.__plotType == 'Scatter':
			self.axes.scatter(self.__x, self.__y)
		elif self.__plotType == 'Line':
			self.axes.plot(self.__x, self.__y) if not self.toggleParams["error"] else self.axes.errorbar(self.__x, self.__y, yerr=self.__err)
		elif self.__plotType == 'Bar':
			self.axes.bar(self.__x, self.__y)
			if self.toggleParams["stats"]: self.axes.text(self.__xRange[1]*0.5, self.__yRange[1]*0.9, 
				r'$\mu=%s,\ \sigma=%s$'%(np.around(np.average(self.__x), decimals=2),np.around(np.std(self.__x), decimals=2)))
		self.axes.axis([self.__xRange[0], self.__xRange[1], self.__yRange[0], self.__yRange[1]])
		if self.toggleParams["grid"]:
			self.axes.grid()
		self.canvas.draw()

	def __meanYforX(self):
		xDist = []
		yDist = []
		for i in range(len(self.__x)):
			if self.__x[i] not in xDist: xDist.append(self.__x[i])
			if self.__y[i] not in yDist: yDist.append(self.__y[i])
		lineX = []
		lineY = []
		deviations = []
		for value in sorted(xDist):
			lineX.append(value)
			yList = []
			indexList = []
			for i, val in enumerate(self.__x):
				if self.__x[i] == value:
					indexList.append(i)
			for num in indexList:
				yList.append(self.__y[num])
			lineY.append(np.average(yList))
			deviations.append(np.std(yList))
		return lineX, lineY, deviations

	def __freqX(self):
		xDist = []
		for i in range(len(self.__x)):
			if self.__x[i] not in xDist: xDist.append(self.__x[i])
		freq = [0]*len(xDist)
		for i, num in enumerate(xDist):
			for val in self.__x:
				if val == num: freq[i] += 1
		return xDist, freq

	def __updateStatus(self, parameter, label):
		key = self.__getKey()
		assert(parameter in key.keys()), "Parameter needs to be " + str(key.keys())
		self.status.SetString(self.status.FindString(key[parameter]), key[parameter].split(' ')[0] + ' ' + label)

	def getFile(self):
		return self.__file

	def __getKey(self):
		return {"File":self.status.GetString(1),
				"Data":self.status.GetString(2), 
			    "Plot":self.status.GetString(3), 
		        "xLabel":self.status.GetString(4), 
			    "yLabel":self.status.GetString(5), 
			    "xLimit":self.status.GetString(6),
			    "yLimit": self.status.GetString(7)}

	def __canPlot(self):
		if self.__plotType == 'Bar':
			return (True if self.__xLabel != None else False)
		else:
			return (True if self.__xLabel and self.__yLabel != None else False)