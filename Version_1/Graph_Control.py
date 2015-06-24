import wx, re, os, File, Graph
import numpy as np
import pandas as pd

class GraphCtrl(wx.Panel): #Made of several objects (Custom widgets)

	def __init__(self, frame, directory):
		self.frame = frame
		wx.Panel.__init__(self, self.frame.panel)
		self.directory = directory
		self.dataExt = '/Data/'

		self.xTitle = "\t\t  X-Axis"
		self.yTitle = "\t\t  Y-Axis"
		sizer = wx.BoxSizer(wx.VERTICAL)
                  
		self.xLabel = None                     
		self.yLabel = None                    
		self.plotStyle = 'Scatter'             


		self.file = None            #Given as a parameter for new graph

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		space = wx.BoxSizer(wx.VERTICAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		vbox1 = wx.BoxSizer(wx.VERTICAL)

		self.yLimit = Axis_Range(self, wx.HORIZONTAL)
		self.graph = Graph.Graph(self)
		self.xLimit = Axis_Range(self, wx.VERTICAL)
		self.xLabels = wx.ListBox(self, choices=[self.xTitle])
		self.yLabels = wx.ListBox(self, choices=[self.yTitle])
		self.fileSystem = wx.ComboBox(self, choices=os.listdir(self.directory + "/Data/"), 
		   						      style=wx.CB_READONLY, value="Select File")
		self.plotType = wx.RadioBox(self, label='Graph Style', choices=['Scatter', 'Line', 'Bar'], style=wx.RA_SPECIFY_ROWS)
		self.addNew = wx.Button(self, label="New")
		self.delGraph = wx.Button(self, label="Delete")
		self.addNew.Enable(False)

		self.fileSystem.Bind(wx.EVT_COMBOBOX, self.selectFile)
		self.plotType.Bind(wx.EVT_RADIOBOX, self.setPlot)
		self.xLabels.Bind(wx.EVT_LISTBOX, self.setLabels)
		self.yLabels.Bind(wx.EVT_LISTBOX, self.setLabels)

		self.addNew.Bind(wx.EVT_BUTTON, self.newPlot)
		self.delGraph.Bind(wx.EVT_BUTTON, self.delPlot)
		
		hbox1.Add(self.yLimit, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.graph, proportion=12, flag=wx.EXPAND)
		hbox2.Add(space, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.xLimit, proportion=12, flag=wx.EXPAND)
		hbox3.Add(self.xLabels, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.fileSystem, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.plotType, proportion=2, flag=wx.EXPAND)
		vbox1.Add(self.addNew, proportion=1, flag=wx.EXPAND)
		vbox1.Add(self.delGraph, proportion=1, flag=wx.EXPAND)
		hbox3.Add(vbox1, proportion=1, flag=wx.EXPAND)
		hbox3.Add(self.yLabels, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox1, proportion=10, flag=wx.EXPAND)
		sizer.Add(hbox2, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox3, proportion=8, flag=wx.EXPAND)

		self.SetSizer(sizer)

	def selectFile(self, evt): #Reset x and y labels and x and y range
		self.file = File.File(evt.EventObject.GetValue(), self.directory)
		self.file.getData()
		self.xLabels.SetItems('')
		self.yLabels.SetItems('')
		xList = [self.xTitle, "testIndex"]
		yList = [self.yTitle, "testIndex"]
		for val in self.file.data.columns.values:
			xList.append(val)
			yList.append(val)
		self.xLabels.SetItems(xList)
		self.yLabels.SetItems(yList)
		self.isReady()

	def setPlot(self, evt):
		self.plotStyle = str(evt.EventObject.GetStringSelection())

	def setLabels(self, evt):
		if "X-Axis" in evt.EventObject.GetItems()[0]:
			self.xLabel = evt.EventObject.GetStringSelection()
		elif "Y-Axis" in evt.EventObject.GetItems()[0]:
			self.yLabel = evt.EventObject.GetStringSelection()
		else:
			self.xLabel = None
			self.yLabel = None
		self.isReady()

	def newPlot(self, evt):
		self.graph.add(self.file, self.plotStyle, self.xLabel, self.yLabel)
		page = self.graph.getPage()
		xMin, xMax, yMin, yMax = np.min(page.x), np.max(page.x), np.min(page.y), np.max(page.y)
		self.xLimit.setRange(int(xMin), int(xMax))   
		self.yLimit.setRange(int(yMin), int(yMax))   

	def delPlot(self, evt):
		pass

	def __str__(self):
		return "File: " + str(self.file) + "\nPlot: " + self.plotStyle + "\nxLabel: " + str(self.xLabel) + "\nyLabel: " + str(self.yLabel)

	def setAxes(self): 
		"""Adjusts the axes of the graph on the current graph page"""
		page = self.graph.getPage()
		page.updateAxes([self.xLimit.minVal, self.xLimit.maxVal],[self.yLimit.minVal, self.yLimit.maxVal])

	def isReady(self):
		if isinstance(self.file, File.File) and self.xLabel != None and self.yLabel != None:
			self.addNew.Enable(True)
		else:
			self.addNew.Enable(False)

	def getAxisLabels(self, evt): #Combobox event, fills the listboxes
		"""This should be called whenever the file is changed to update the 
		   axis labels in the listboxes"""
		self.file.setName(evt.EventObject.GetValue())
		self.file.getData()

		index = self.file.data.index.values
		self.header = self.file.data.columns.values
		self.heading = ["testIndex"]
		for head in self.header:
			self.heading.append(head)

		self.data = np.hstack((index.reshape((len(index),1)), self.file.data.as_matrix()))
		self.data2 = pd.DataFrame(data=self.data, columns=self.heading)

		self.axisLabels.setAxes(self.header) #Fills the listbox

		self.xLabel = None
		self.yLabel = None
		self.x = None
		self.y = None 

class Axis_Range(wx.Panel):

	def __init__(self, parent, orientation):
		wx.Panel.__init__(self, parent)

		self.parent = parent
		if orientation == wx.VERTICAL:
			style = wx.SL_HORIZONTAL
		elif orientation == wx.HORIZONTAL:
			style = wx.SL_VERTICAL
		else:
			raise ValueError, "Axis_Range: Orientation needs to be wx.VERTICAL or wx.HORIZONTAL"

		self.sizer = wx.BoxSizer(orientation)

		self.minVal = 0
		self.maxVal = 100

		self.min = wx.Slider(self, value=0, minValue=0, maxValue=100, style=style)
		self.max = wx.Slider(self, value=100, minValue=0, maxValue=100, style=style)
		self.min.Bind(wx.EVT_SCROLL, self.setAxes)
		self.max.Bind(wx.EVT_SCROLL, self.setAxes)

		self.sizer.Add(self.min, proportion=1, flag=wx.EXPAND)
		self.sizer.Add(self.max, proportion=1, flag=wx.EXPAND)

		self.SetSizer(self.sizer)

	def setRange(self, Min, Max):
		self.min.SetMax(1000000)
		self.min.SetMin(0)
		self.max.SetMax(1000000)
		self.max.SetMin(0)
		self.min.SetMax(Max)
		self.min.SetMin(Min)
		self.min.SetValue(Min)
		self.max.SetMax(Max)
		self.max.SetMin(Min)
		self.max.SetValue(Max)

	def setAxes(self, evt):
		self.__adjustAxes()
		self.minVal = self.min.GetValue()
		self.maxVal = self.max.GetValue()
		self.parent.setAxes()

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
		self.xAxis.Bind(wx.EVT_LISTBOX, self.selectAxes)
		self.yAxis.Bind(wx.EVT_LISTBOX, self.selectAxes)
		self.sizer.Add(self.xAxis, proportion=1, flag=wx.EXPAND)
		self.sizer.Add(self.yAxis, proportion=1, flag=wx.EXPAND)

		self.xAxis.Bind(wx.EVT_LISTBOX, self.selectAxes)
		self.yAxis.Bind(wx.EVT_LISTBOX, self.selectAxes)

		self.SetSizer(self.sizer)

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

