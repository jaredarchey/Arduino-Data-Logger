import wx
import numpy as np
from Graph import *

class Main_Panel(wx.Panel): #This is where all widgets are going to be placed

	def __init__(self, parent):

		wx.Panel.__init__(self, parent)

		self.statusLabels = ["\tStatus_Box", "File: None", "Has_Data: False", "PlotType: Scatter", 
						     "xLabel: None", "yLabel: None", "xLimit: None", "yLimit: None"]
		self.parent = parent
		self.style = 'Scatter'
		self.x_axis_label = None
		self.y_axis_label = None
		self.x_axis_range = [0,1]
		self.y_axis_range = [0,1]

		self.graph = Graph(self)                      #Graph Object
		self.yLimit = Axis_Range(self, wx.HORIZONTAL) #Axis Object
		self.xLimit = Axis_Range(self, wx.VERTICAL)   #Axis Object
		self.Labels = Axis_Labels(self)               #Axis Object
		self.status = wx.ListBox(self, choices=self.statusLabels)
		self.plotType = wx.RadioBox(self, label='Graph Style', choices=['Scatter', 'Line', 'Bar'], style=wx.RA_SPECIFY_ROWS)

		self.plotType.Bind(wx.EVT_RADIOBOX, self.updateStyle)

		sizer = wx.BoxSizer(wx.VERTICAL)
		space = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		vbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.yLimit, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.graph.addObj(), proportion=14, flag=wx.EXPAND)
		sizer.Add(hbox1, proportion=6, flag=wx.EXPAND)
		hbox2.Add(space, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.xLimit, proportion=14, flag=wx.EXPAND)
		vbox.Add(self.status, proportion=1, flag=wx.EXPAND)
		vbox.Add(self.plotType, proportion=1, flag=wx.EXPAND)
		vbox.Add(self.Labels, proportion=2, flag=wx.EXPAND)
		sizer.Add(hbox2, proportion=1, flag=wx.EXPAND)
		sizer.Add(vbox, proportion=4, border=40, flag=wx.EXPAND|wx.LEFT|wx.RIGHT)
		self.SetSizer(sizer)

		self.Fit()

	def updateStyle(self, evt):
		self.style = evt.EventObject.GetStringSelection()
		self.updateGraphParameters()

	def updateGraphParameters(self):
		self.updateStatus("Plot", self.style)
		self.updateStatus("xLabel", str(self.x_axis_label))
		self.updateStatus("yLabel", str(self.y_axis_label))
		self.updateStatus("xLimit",str(self.xLimit.getRange()))
		self.updateStatus("yLimit",str(self.yLimit.getRange()))
		self.graph.setFile(self.getFile())
		self.graph.setPlotType(self.style)
		self.graph.setXlabel(self.x_axis_label)
		self.graph.setYlabel(self.y_axis_label)
		self.graph.setXrange(self.xLimit.getRange())
		self.graph.setYrange(self.yLimit.getRange())
		if self.graph.canPlot():
			self.graph.updatePlot()

	def updatePlot(self):
		pass

	def updateStatus(self, parameter, label):
		key = self.getKey()
		assert(parameter in key.keys()), "Parameter needs to be " + str(key.keys())
		self.status.SetString(self.status.FindString(key[parameter]), key[parameter].split(' ')[0] + ' ' + label)

	def getKey(self):
		return {"File":self.status.GetString(1),
				"Data":self.status.GetString(2), 
			    "Plot":self.status.GetString(3), 
		        "xLabel":self.status.GetString(4), 
			    "yLabel":self.status.GetString(5), 
			    "xLimit":self.status.GetString(6),
			    "yLimit": self.status.GetString(7)}

	def getFile(self):
		return self.parent.currentFile


class Axis_Range(wx.Panel):

	def __init__(self, parent, orientation):
		wx.Panel.__init__(self, parent)

		self.parent = parent
		if orientation == wx.VERTICAL:
			style = wx.SL_HORIZONTAL
			type1 = wx.TOP
			type2 = wx.BOTTOM
		elif orientation == wx.HORIZONTAL:
			style = wx.SL_VERTICAL
			type1 = wx.LEFT
			type2 = wx.RIGHT
		else:
			raise ValueError, "Axis_Range: Orientation needs to be wx.VERTICAL or wx.HORIZONTAL"

		self.sizer = wx.BoxSizer(orientation)

		self.minVal = 0
		self.maxVal = 1

		self.min = wx.Slider(self, value=0, minValue=0, maxValue=1, style=style)
		self.max = wx.Slider(self, value=1, minValue=0, maxValue=1, style=style)
		self.min.Bind(wx.EVT_SCROLL, self.setValues)
		self.max.Bind(wx.EVT_SCROLL, self.setValues)

		self.sizer.Add(self.min, proportion=1, border=10, flag=wx.EXPAND|type1)
		self.sizer.Add(self.max, proportion=1, border=10, flag=wx.EXPAND|type2)

		self.SetSizer(self.sizer)

	def setRange(self, Min, Max):
		if Min == Max:
			Max += 1
		self.min.SetMin(0)
		self.max.SetMin(0)
		self.min.SetMax(Max)
		self.min.SetMin(Min)
		self.min.SetValue(Min)
		self.max.SetMax(Max)
		self.max.SetMin(Min)
		self.max.SetValue(Max)
		self.minVal = Min
		self.maxVal = Max

	def setValues(self, evt):
		self.__adjustAxes()
		self.minVal = self.min.GetValue()
		self.maxVal = self.max.GetValue()
		self.parent.updateGraphParameters()

	def getRange(self):
		return [self.minVal, self.maxVal]

	def __adjustAxes(self):
		if self.min.GetValue() > self.max.GetValue():
			self.min.SetValue(self.max.GetValue())
			self.max.SetValue(self.min.GetValue())

class Axis_Labels(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.parent = parent

		self.xTitle = "\t\t  X-Axis"
		self.yTitle = "\t\t  Y-Axis"
		self.xAxis = wx.ListBox(self, choices=[self.xTitle])
		self.yAxis = wx.ListBox(self, choices=[self.yTitle])
		self.sizer.Add(self.xAxis, proportion=1, flag=wx.EXPAND)
		self.sizer.Add(self.yAxis, proportion=1, flag=wx.EXPAND)

		self.xAxis.Bind(wx.EVT_LISTBOX, self.selectAxes)
		self.yAxis.Bind(wx.EVT_LISTBOX, self.selectAxes)

		self.SetSizer(self.sizer)

	def selectAxes(self, evt):
		selection = evt.EventObject.GetStringSelection()
		if "-Axis" in selection or selection not in evt.EventObject.GetItems():
			return

		if selection == 'testIndex':
			data = self.parent.getFile().data.index.values
		else:
			data = self.parent.getFile().data[selection]
		dataRange = [int(np.min(data)), int(np.max(data))]

		if "X-Axis" in evt.EventObject.GetItems()[0]:
			self.parent.x_axis_label = selection
			self.parent.x_axis_range = dataRange
			self.parent.xLimit.setRange(dataRange[0], dataRange[1])
		elif "Y-Axis" in evt.EventObject.GetItems()[0]:
			self.parent.y_axis_label = selection
			self.parent.y_axis_range = dataRange
			self.parent.yLimit.setRange(dataRange[0], dataRange[1])

		self.parent.updateGraphParameters()

	def setAxes(self, labels):
		xLabel = [self.xTitle, "testIndex"]
		yLabel = [self.yTitle, "testIndex"]
		for i in range(len(labels)):
			xLabel.append(labels[i])
			yLabel.append(labels[i])
		self.xAxis.SetItems('')
		self.yAxis.SetItems('')
		self.xAxis.SetItems(xLabel)
		self.yAxis.SetItems(yLabel)

	def resetAxes(self):
		self.xAxis.SetItems('')
		self.yAxis.SetItems('')
		self.xAxis.SetItems([self.xTitle])
		self.yAxis.SetItems([self.yTitle])