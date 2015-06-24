import wx
from File import *

class NewFile_Window(wx.Frame):

	def __init__(self, parent, title="New File", size=(200,100)):
		wx.Frame.__init__(self, parent, title=title, size=size)
		self.parent = parent

		self.name = None
		self.columns = None

		sizer = wx.BoxSizer(wx.VERTICAL)
		panel = wx.Panel(self)
		self.valueEntry = wx.TextCtrl(panel, value='File Name', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.columnEntry = wx.TextCtrl(panel, value='Column Names', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER|wx.TE_MULTILINE)
		self.createNew = wx.Button(panel, label='Create File')
		self.valueEntry.Bind(wx.EVT_SET_FOCUS, self.erase)
		self.valueEntry.Bind(wx.EVT_TEXT_ENTER, self.giveName)
		self.columnEntry.Bind(wx.EVT_SET_FOCUS, self.erase)
		self.columnEntry.Bind(wx.EVT_TEXT_ENTER, self.giveCol)
		self.createNew.Bind(wx.EVT_BUTTON, self.createFile)
		self.createNew.Enable(False)

		sizer.Add(self.valueEntry, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.columnEntry, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.createNew, proportion=1, flag=wx.EXPAND)

		panel.SetSizer(sizer)

		self.Centre()

		self.Show()

	def erase(self, evt):
		evt.EventObject.SetValue('')

	def giveName(self, evt):
		value = evt.EventObject.GetValue()
		if self.__nameCheck(value):
			self.name = value + '.csv'
		else:
			self.name = None
		evt.EventObject.SetValue('')
		self.canCreate() 

	def giveCol(self, evt):
		value = evt.EventObject.GetValue()
		cols = value.split(' ')
		self.columns = cols
		evt.EventObject.SetValue('')
		self.canCreate()

	def createFile(self, evt):
		file = File(self.parent.dataDirectory + self.name)
		file.newFile(self.columns)
		self.parent.updateFiles(file)
		self.parent.panel.Labels.resetAxes()
		self.parent.hasData = file.hasData()
		self.Close()

	def canCreate(self):
		if self.name != None and self.columns != None:
			self.createNew.Enable(True)
			return True
		else:
			self.createNew.Enable(False)
			return False

	def __nameCheck(self, name):
		if ' ' in name:
			return False
		else:
			return True