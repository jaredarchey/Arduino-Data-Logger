import wx, wx.grid

class View(wx.Frame):     

	def __init__(self, parent, title, size):
		wx.Frame.__init__(self, parent, title=title, size=size)

		self.Centre()													

		self.panel = wx.Panel(self)
		self.sheet = wx.grid.Grid(self.panel) 
		sizer = wx.BoxSizer(wx.HORIZONTAL)   
		sizer.Add(self.sheet, proportion=1, flag=wx.EXPAND|wx.ALL) 

		self.panel.SetSizer(sizer)

		self.Show()

	def giveData(self, data):
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
