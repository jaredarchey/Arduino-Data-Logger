import wx, wx.grid
import pandas as pd

class View(wx.Frame):     

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, title="View Data", size=(600,600))

		self.Centre()													

		self.panel = wx.Panel(self)
		self.sheet = wx.grid.Grid(self.panel) 
		sizer = wx.BoxSizer(wx.HORIZONTAL)   
		sizer.Add(self.sheet, proportion=1, flag=wx.EXPAND|wx.ALL) 

		self.panel.SetSizer(sizer)

		self.Show()

	def giveData(self, data):
		assert(isinstance(data, pd.DataFrame)), "Data must be in a pandas dataframe to use giveData"
		self.clear()
		self.sheet.CreateGrid(len(data.index.values), len(data.columns.values))
		for i, header in enumerate(data.columns.values):
			self.sheet.SetColLabelValue(i, str(header))
		for i, index in enumerate(data.index.values):
			self.sheet.SetRowLabelValue(i, str(index))
		for i, row in enumerate(data.as_matrix()):
			for j, num in enumerate(row):
				self.sheet.SetCellValue(i, j, str(num))

	def clear(self):
		self.sheet.ClearGrid()