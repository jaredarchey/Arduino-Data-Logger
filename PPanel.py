import wx, re
import numpy as np
from Axis_Range import *
from File import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class PPanel(wx.Panel):

	def __init__(self, window):
		wx.Panel.__init__(self, window)

		self.__toggleParams = {
							 "grid":False,
							 "error":False,
							 "stats":False,
							 "polyfit":False,
							 "correlate":False
							}
		self.__graphParams = {
							  "file":None,
						  	  "plot":'Scatter',
							  "xLabel":None,
							  "yLabel":None,
							  "xRange":[0,1],
							  "yRange":[0,1],
							  "polyVal": 1
						     }
		self.dataChanged = True

		self.__createWidgets()
		self.__bindWidgets()
		self.__addWidgets()

	def __createWidgets(self):
		self.figure = plt.Figure(figsize=(2,2))
		self.axes = self.figure.add_subplot(111)
		self.canvas = FigureCanvas(self, -1, self.figure)

		self.xLimit = Axis_Range(self, 'x', self.__graphParams["xRange"][0], self.__graphParams["xRange"][1]) 
		self.yLimit = Axis_Range(self, 'y', self.__graphParams["yRange"][0], self.__graphParams["yRange"][1]) 
		self.xLabel = wx.ComboBox(self, value="X-Axis", choices=[])
		self.yLabel = wx.ComboBox(self, value="Y-Axis", choices=[])
		self.plotChoices = wx.RadioBox(self, label='Graph Style', choices=['Scatter', 'Line', 'Bar'])
		self.axisChoices = wx.RadioBox(self, label='Axis', choices=['X','Y'])
		self.customRange = wx.TextCtrl(self, value='Range', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.polyDegree = wx.TextCtrl(self, value='Poly Degree', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.statusButton = wx.Button(self, label='Print Status')
		self.toggleGrid = wx.CheckBox(self, label="Toggle Grid")
		self.toggleErr = wx.CheckBox(self, label="Toggle Error (Line Only)")
		self.toggleStats = wx.CheckBox(self, label="Toggle Stats (Bar Only)")
		self.togglePoly = wx.CheckBox(self, label="Polyfit (Scatter Only)")
		self.toggleCorr = wx.CheckBox(self, label="Correlate (Scatter Only)")

	def __bindWidgets(self):
		for checkBox in [self.toggleGrid, self.toggleErr, self.toggleStats, self.togglePoly, self.toggleCorr]:
			checkBox.Bind(wx.EVT_CHECKBOX, self.__toggle)

		for textCtrl in [self.customRange, self.polyDegree]:
			textCtrl.Bind(wx.EVT_SET_FOCUS, self.__erase)

		self.plotChoices.Bind(wx.EVT_RADIOBOX, self.__updateStyle)
		self.customRange.Bind(wx.EVT_TEXT_ENTER, self.__custom_range)
		self.polyDegree.Bind(wx.EVT_TEXT_ENTER, self.__updateDegree)
		self.xLabel.Bind(wx.EVT_COMBOBOX, self.__setXlabel)
		self.yLabel.Bind(wx.EVT_COMBOBOX, self.__setYlabel)
		self.statusButton.Bind(wx.EVT_BUTTON, self.__showStatus)

	def __addWidgets(self):
		sizer = wx.BoxSizer(wx.VERTICAL)
		plotBox = wx.BoxSizer(wx.VERTICAL)
		ctrlBox = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		space = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		vbox1 = wx.BoxSizer(wx.VERTICAL)
		vbox2 = wx.BoxSizer(wx.VERTICAL)
		vbox3 = wx.BoxSizer(wx.VERTICAL)
		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5 = wx.BoxSizer(wx.HORIZONTAL)

		hbox1.Add(self.yLimit, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.canvas, proportion=12, flag=wx.EXPAND)
		plotBox.Add(hbox1, proportion=8, flag=wx.EXPAND)
		hbox2.Add(space, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.xLimit, proportion=12, flag=wx.EXPAND)
		plotBox.Add(hbox2, proportion=1, flag=wx.EXPAND)

		hbox3.Add(self.xLabel, proportion=1, flag=wx.EXPAND)
		hbox3.Add(self.yLabel, proportion=1, flag=wx.EXPAND)
		hbox3.Add(self.plotChoices, proportion=1, flag=wx.EXPAND)
		ctrlBox.Add(hbox3, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.toggleGrid, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.toggleErr, proportion=1, flag=wx.EXPAND) 
		vbox1.Add(self.toggleStats, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.togglePoly, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.toggleCorr, proportion=1, flag=wx.EXPAND)
		hbox5.Add(self.customRange, proportion=1, flag=wx.EXPAND)
		hbox5.Add(self.axisChoices, proportion=1, flag=wx.EXPAND)
		vbox2.Add(hbox5, proportion=1, border=10, flag=wx.EXPAND|wx.TOP|wx.BOTTOM)
		vbox2.Add(self.polyDegree, border=10, flag=wx.EXPAND|wx.TOP|wx.BOTTOM)
		vbox2.Add(self.statusButton, border=10, flag=wx.EXPAND|wx.TOP|wx.BOTTOM)
		hbox4.Add(vbox1, proportion=1, flag=wx.EXPAND)
		hbox4.Add(vbox3, proportion=1, flag=wx.EXPAND)
		hbox4.Add(vbox2, proportion=1, flag=wx.EXPAND)
		ctrlBox.Add(hbox4, proportion=4, flag=wx.EXPAND)

		sizer.Add(plotBox, proportion=2, flag=wx.EXPAND)
		sizer.Add(ctrlBox, proportion=1, flag=wx.EXPAND)

		self.SetSizer(sizer)

	def setFile(self, file): #Sets the file and resets the plot state
		self.__graphParams["file"] = file
		self.__updateDataLabels()
		self.__resetGraphParams()
		self.axes.clear()
		self.canvas.draw()

	def getFile(self):
		return self.__graphParams["file"]

	def __updateStyle(self, evt):
		self.__graphParams["plot"] = evt.EventObject.GetStringSelection()
		self.dataChanged = True
		if self.__canPlot():
			self.__getData()

	def __setXlabel(self, evt):
		self.__graphParams["xLabel"] = evt.EventObject.GetStringSelection()
		self.dataChanged = True
		if self.__canPlot():
			self.__getData()

	def __setYlabel(self, evt):
		self.__graphParams["yLabel"] = evt.EventObject.GetStringSelection()
		self.dataChanged = True
		if self.__canPlot():
			self.__getData()

	def __toggle(self, evt):
		label = evt.EventObject.GetLabel().split(' ')
		toggle = (label[1] if label[0] == 'Toggle' else label[0])
		self.__toggleParams[toggle.lower()] = not self.__toggleParams[toggle.lower()]
		if self.__canPlot():
			self.__getData()

	def __custom_range(self, evt):
		newRange = evt.EventObject.GetValue().split(' ')
		evt.EventObject.SetValue('')
		if len(newRange) != 2: 
			return
		for value in newRange:
			if not value.isdigit():
				return
		axisToSet = self.axisChoices.GetStringSelection()
		Range = [int(val) for val in newRange]
		if axisToSet == 'X': 
			self.__graphParams["xRange"] = Range
			self.xLimit.setRange(self.__graphParams["xRange"])
		else:
			self.__graphParams["yRange"] = Range
			self.yLimit.setRange(self.__graphParams["yRange"])
		if self.__canPlot():
			self.__getData()

	def __updateDegree(self, evt):
		opts = [str(i) for i in range(1, 10)]
		degree = evt.EventObject.GetValue()
		evt.EventObject.SetValue('')
		if not degree.isdigit() or degree not in opts:
			return
		self.__graphParams["polyVal"] = int(degree)
		if self.__canPlot():
			self.__toggleSettings()
			self.canvas.draw()

	def __updateDataLabels(self):
		if isinstance(self.getFile(), File):
			columns = self.getFile().data.columns.values
			self.xLabel.SetItems(['Index'])
			self.yLabel.SetItems(['Index'])
			for label in columns:
				self.xLabel.Append(label)
				self.yLabel.Append(label)
			self.xLabel.SetValue("X-Axis")
			self.yLabel.SetValue("Y-Axis")
		self.dataChanged = True

	def __resetGraphParams(self):
		self.__graphParams["xLabel"] = None
		self.__graphParams["yLabel"] = None
		self.__graphParams["xRange"] = [0,1]
		self.__graphParams["yRange"] = [0,1]

	def setRange(self):
		self.__graphParams["xRange"] = self.xLimit.getRange()
		self.__graphParams["yRange"] = self.yLimit.getRange()
		self.__formatAxis()
		if self.__toggleParams["stats"] and self.__graphParams["plot"] == 'Bar':
				self.__barStats()
		if self.__graphParams["plot"] == 'Scatter':
			if self.__toggleParams["correlate"]:
				self.__scatterCorr()
			if self.__toggleParams["polyfit"]:
				self.__curveFit()
		self.canvas.draw()

	def __canPlot(self):
		x, y = self.__graphParams["xLabel"], self.__graphParams["yLabel"]
		if self.__graphParams["plot"] == 'Bar':
			return (True if x != None else False)
		else:
			return (True if x and y != None else False)

	def __getData(self): #This is the most important function, it updates the plot, gathers the data, and does checkbox commands
		print "Plotting..."
		file = self.__graphParams["file"]
		if self.dataChanged == True:
			if self.__graphParams["xLabel"] == 'Index' and self.__graphParams["yLabel"] == 'Index':
				self.x = list(file.data.index.values)
				self.y = list(file.data.index.values)
			elif self.__graphParams["xLabel"] == 'Index':
				self.x = list(file.data.index.values)
				self.y = list(file.data[self.__graphParams["yLabel"]])
			elif self.__graphParams["yLabel"] == 'Index':
				self.x = list(file.data[self.__graphParams["xLabel"]])
				self.y = list(file.data.index.values)
			else:
				self.x = list(file.data[self.__graphParams["xLabel"]])
				self.y = list(file.data[self.__graphParams["yLabel"]])
			if self.__graphParams["plot"] == 'Line':
				self.__getLineData()
			elif self.__graphParams["plot"] == 'Bar':
				self.__getBarData()
			self.__graphParams["xRange"] = [np.min(self.x), np.max(self.x)]
			self.__graphParams["yRange"] = [np.min(self.y), np.max(self.y)]
			self.xLimit.setRange(self.__graphParams["xRange"])
			self.yLimit.setRange(self.__graphParams["yRange"])
		self.__updatePlot()
		self.dataChanged = False
		print "Plotted " + str(len(self.y)) + " Data Points!"

	def __getLineData(self):
		xDist = self.__getListValues(self.x)
		indeces = []
		for val in xDist:
			indeces.append([i for i, num in enumerate(self.x) if self.x[i] == val])
		y = []
		self.err = []
		for indexList in indeces:
			vals = [self.y[index] for index in indexList]
			y.append(np.average(vals))
			self.err.append(np.std(vals))
		self.x = xDist
		self.y = y

	def __getBarData(self):
		xDist = self.__getListValues(self.x)
		freq = [self.x.count(val) for val in xDist]
		self.x = xDist
		self.y = freq

	def __updatePlot(self):
		self.axes.clear()

		if self.__graphParams["plot"] == 'Scatter':
			self.axes.scatter(self.x, self.y)
		elif self.__graphParams["plot"] == 'Line':
			if self.__toggleParams["error"]:
				self.axes.errorbar(self.x, self.y, yerr=self.err)
			else:
				self.axes.plot(self.x, self.y)
		elif self.__graphParams["plot"] == 'Bar':
			self.axes.bar(self.x, self.y)

		self.__addedText()
		self.__toggleSettings()
		self.__formatAxis()
		self.canvas.draw()

	def __addedText(self):
		if self.__graphParams["plot"] == 'Scatter':
			self.corrText = self.axes.text(0.8, 0.8, '', bbox=dict(facecolor='red',alpha=0.8),
					                       transform=self.axes.transAxes)
			self.curveText = self.axes.text(0, 0, '', bbox=dict(facecolor='red',alpha=0.8),
					  					    transform=self.axes.transAxes, fontsize=10)
		elif self.__graphParams["plot"] == 'Bar':
			self.statsText = self.axes.text(0.5, 0.9, '', bbox=dict(facecolor='red',alpha=0.8),
					  					    transform=self.axes.transAxes)

	def __toggleSettings(self):
		if self.__graphParams["plot"] == 'Scatter':
			if self.__toggleParams["correlate"]:
				self.__scatterCorr()
			if self.__toggleParams["polyfit"]:
				self.__curveFit()
		elif self.__graphParams["plot"] == 'Bar':
			if self.__toggleParams["stats"]:
				self.__barStats()
		if self.__toggleParams["grid"]: 
			self.axes.grid()

	def __formatAxis(self):
		self.axes.set_title(self.__graphParams["xLabel"] + " vs. " + self.__graphParams["yLabel"])
		self.axes.set_xlabel(self.__graphParams["xLabel"])
		self.axes.set_ylabel(self.__graphParams["yLabel"])
		self.axes.axis([self.__graphParams["xRange"][0], self.__graphParams["xRange"][1],
						self.__graphParams["yRange"][0], self.__graphParams["yRange"][1]])

	def __barStats(self):
		x, y = self.__getPointsInRange(self.x, self.y)
		data =  []
		for i, v in enumerate(x):
			data.extend([v]*y[i])
		self.statsText.set_text(r'$\mu=%s,\ \sigma=%s$'%(np.around(np.average(data), decimals=2),np.around(np.std(data), decimals=2)))

	def __curveFit(self):
		if hasattr(self, "fit"):
			try:
				self.fit[0].remove()
			except: pass
		x, y = self.__getPointsInRange(self.x, self.y)
		xDist = self.__getListValues(x)
		coeffs = np.polyfit(x, y, self.__graphParams["polyVal"])
		func = np.poly1d(coeffs)
		fitY = []
		for val in xDist:
			fitY.append(np.polyval(func, val))
		self.curveText.set_text(str(func))
		self.fit = self.axes.plot(xDist, fitY, linewidth=5, linestyle='--', color='red')

	def __scatterCorr(self):
		x, y = self.__getPointsInRange(self.x, self.y)
		self.corrText.set_text(r'$\rho=%s$'%np.around(np.corrcoef(x, y)[0][1], decimals=3))

	def __getPointsInRange(self, x, y):
		xLim = self.__graphParams["xRange"]
		yLim = self.__graphParams["yRange"]
		inXrange = np.arange(xLim[0],xLim[1]+1)
		inYrange = np.arange(yLim[0],yLim[1]+1)
		points = list(zip(x, y))
		pointsInRange = [pair for tick in inXrange for pair in points if (pair[0] == tick and pair[1] in inYrange)]
		xx, yy = [], []
		for pair in pointsInRange:
			xx.append(pair[0])
			yy.append(pair[1])
		return xx, yy
		
	def __getListValues(self, List):
		assert(type(List) == list), "Argument must be a list"
		values = []
		values.extend(val for val in List if val not in values)
		return sorted(values)

	def __showStatus(self, evt):
		if isinstance(self.getFile(), File):
			print "\nFile: " + self.getFile().name + "\nxLabel: " + str(self.__graphParams["xLabel"]) + "\nyLabel: "  \
							 +  str(self.__graphParams["yLabel"]) + "\nxRange: " + str(self.__graphParams["xRange"]) \
							 + "\nyRange: " + str(self.__graphParams["yRange"]) + "\n"

	def __erase(self, evt):
		evt.EventObject.SetValue('')