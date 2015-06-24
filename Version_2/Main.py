import wx, os
from File import *
from Main_Panel import *
from Recorder import *
from New_File import *
from View import *
from RecordCtrl import *

class Main_Frame(wx.Frame):
	"""Main Window of the data logger application"""

	def __init__(self, parent, title, size):
		wx.Frame.__init__(self, parent, title=title, size=size)
		self.Centre()
		self.dataDirectory = os.getcwd() + '/Data/'

		self.recorder = Recorder(self, port='/dev/ttyACM0', baud=115200)

		self.lastFile = None
		self.currentFile = None
		self.hasData = False
	
		self.Menus()			

		self.panel = Main_Panel(self)

		self.Show()


	def Menus(self):
	    self.menubar = wx.MenuBar()

	    self.fileMenu = wx.Menu()
	    self.openMenu = wx.Menu()
	    self.viewMenu = wx.Menu()
	    self.recordMenu = wx.Menu()

	    for i, file in enumerate(os.listdir(self.dataDirectory)):
	    	added = self.openMenu.Append(201+i, file, file)
	    	self.Bind(wx.EVT_MENU, self.selectFile, added)

	    self.fileMenu.AppendMenu(101, 'Open', self.openMenu) #Add the open submenu to the file menu of the menubar
	    self.fileNew = self.fileMenu.Append(wx.ID_NEW, 'New')
	    self.fileView = self.viewMenu.Append(wx.ID_PASTE, 'View')
	    self.fileRecord = self.recordMenu.Append(wx.ID_OPEN, 'Record')

	    self.Bind(wx.EVT_MENU, self.newFile, self.fileNew)
	    self.Bind(wx.EVT_MENU, self.viewFile, self.fileView)
	    self.Bind(wx.EVT_MENU, self.recordFile, self.fileRecord)

	    self.menubar.Append(self.fileMenu, 'File') #Add the file menu to menubar
	    self.menubar.Append(self.viewMenu, 'View')
	    self.menubar.Append(self.recordMenu, 'Record')

	    self.SetMenuBar(self.menubar)

	def newFile(self, evt): #File > New
		NewFile_Window(self)

	def addFile(self, file): #When a new file is created and saved, it is then added to the file list
	    labels = []
	    for i in range(self.openMenu.GetMenuItemCount()):
	    	labels.append(self.openMenu.FindItemByPosition(i).GetLabel())
	    if file not in labels:
			added = self.openMenu.Append(201+self.openMenu.GetMenuItemCount(), file)
			self.Bind(wx.EVT_MENU, self.selectFile, added)
			self.panel.Labels.setAxes(self.currentFile.columns)

	def selectFile(self, evt): #Selects the current file from the menu
		fileName = self.GetMenuBar().FindItemById(evt.GetId()).GetLabel()
		path = self.dataDirectory + fileName
		self.updateFiles(File(path))   #Sets the current file type None, Data, New
		self.panel.Labels.setAxes(self.currentFile.columns)
		self.panel.updateStatus("File", str(self.currentFile.name))
		self.panel.updateStatus("Data", str(self.hasData))
		self.hasData = self.currentFile.hasData()
		self.panel.updateGraphParameters()                    #Update graph file

	def updateFiles(self, file):
		assert (isinstance(file, File)), "File must be file object of NoneType"
		self.lastFile = self.currentFile
		self.currentFile = file
		self.recorder.setFile(file)
		self.hasData = file.hasData()
		if hasattr(self.currentFile, "name"):
			self.hasData = self.currentFile.hasData()
			self.panel.updateStatus("File", str(self.currentFile.name))
		self.panel.updateStatus("Data", str(self.hasData))

	def viewFile(self, evt):
		if self.currentFile != None:
			if self.currentFile.hasData():
				view = View(self)
				view.giveData(self.currentFile.data)

	def recordFile(self, evt):
		if isinstance(self.currentFile, File):
			record = RecordCtrl(self)

	def getFile(self):
		return self.currentFile

app = wx.App()
Main_Frame(None, "Test", (600,600))
app.MainLoop()