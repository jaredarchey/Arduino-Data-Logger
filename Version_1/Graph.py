import wx, re, os, File
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class Graph(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent.frame.panel)
		self.parent = parent
		self.directory = self.parent.directory

		sizer = wx.BoxSizer(wx.VERTICAL)
   
		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.updateBook)

		sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)

		self.SetSizer(sizer)

	def updateBook(self, evt):
		pass

	def add(self, File, plotType, xLabel, yLabel):
		self.notebook.AddPage(Graph_Page(self), File.name)
		for tab in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab) == File.name:
				self.notebook.SetSelection(tab)
		page = self.notebook.GetPage(self.notebook.GetSelection())
		page.plot(File, plotType, xLabel, yLabel)

	def getPage(self):
		return self.notebook.GetPage(self.notebook.GetSelection())

class Graph_Page(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent.notebook)

		self.parent = parent
		self.notebook = self.parent.notebook
		self.sizer = wx.BoxSizer(wx.VERTICAL)

		self.figure = plt.Figure(figsize=(2,2))
		self.axes = self.figure.add_subplot(111)
		self.canvas = FigureCanvas(self, -1, self.figure)

		self.sizer.Add(self.canvas, proportion=1, flag=wx.EXPAND)
		self.SetSizer(self.sizer)

	def plot(self, File, plotType, xLabel, yLabel):
		self.file = File
		self.plotType = plotType
		self.xLabel = xLabel
		self.yLabel = yLabel

		if self.xLabel == 'testIndex':
			self.x = File.data.index.values
		elif self.xLabel != 'testIndex':
			self.x = File.data[xLabel]
		if self.yLabel == 'testIndex':
			self.y = File.data.index.values
		elif self.yLabel != 'testIndex':
			self.y = File.data[yLabel]

		if self.plotType == 'Scatter':
			self.axes.scatter(self.x,self.y)
		elif self.plotType == 'Line':
			pass
		elif self.plotType == 'Bar':
			pass
		self.axes.set_xlabel(xLabel)
		self.axes.set_ylabel(yLabel)
		self.axes.set_title(xLabel + ' vs. ' + yLabel)
		self.axes.grid()

	def updateAxes(self, xlim, ylim):
		self.parent.add(self.file, self.plotType, self.xLabel, self.yLabel)
		self.notebook.DeletePage(self.notebook.GetSelection())
		

