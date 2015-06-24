import wx, os, serial
import pandas as pd
import File, Recording, View

class RecordCtrl(wx.Panel):
	"""This panel handles the interaction between python and arduino
	   only input required is a frame object, this panel needs to be placed
	   in a wx.BoxSizer object because size is not explicitly stated"""

	def __init__(self, frame, directory): #current directory
		self.frame = frame
		wx.Panel.__init__(self, self.frame.panel)
		self.directory = directory
		self.dataExt = '/Data/'
		self.currentPage = None
 
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)

		self.notebook = wx.Notebook(self)
		self.fileSelection = wx.ComboBox(self, choices=["~~New File"] + os.listdir(self.directory + self.dataExt), #current directory
								     style=wx.CB_READONLY, value="Select a file to record to")
		self.delPage = wx.Button(self, label="Delete Page")

		self.fileSelection.Bind(wx.EVT_COMBOBOX, self.selectFile)          
		self.delPage.Bind(wx.EVT_BUTTON, self.delete)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.updateBook)

		self.hbox.Add(self.fileSelection, proportion=1, flag=wx.EXPAND)     
		self.hbox.Add(self.delPage, proportion=1, flag=wx.EXPAND)
		self.sizer.Add(self.notebook, proportion=6, flag=wx.EXPAND)
		self.sizer.Add(self.hbox, proportion=1, flag=wx.EXPAND)
		
		self.SetSizer(self.sizer)

	def updateBook(self, evt): 
		page = evt.EventObject.GetPage(evt.EventObject.GetSelection())
		self.currentPage = page
		comboBox = self.fileSelection
		name = str(page.file.name)

		if isinstance(page, Record_Page):
			comboBox.SetStringSelection(name)			
			page.file.getData()									

		elif isinstance(page, New_File_Page):
			comboBox.SetStringSelection("~~" + name)

	def selectFile(self, evt):
		"""Creates new notebook page based on file selected in comboBox"""

		fileName = self.fileSelection.GetValue()
		notebook = self.notebook

		if fileName[0] == "~":
			if not self.isRepeat("New File"):
				self.notebook.AddPage(New_File_Page(self, self.frame), fileName)
		else:
			if not self.isRepeat(fileName):
				self.notebook.AddPage(Record_Page(self, self.frame), fileName)

		for tab in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab) == fileName:
				self.notebook.SetSelection(tab)

	def isRepeat(self, tabName):
		for page in range(self.notebook.GetPageCount()):
				if self.notebook.GetPageText(page) == tabName:
					return True
		return False

	def delete(self, evt):
		self.fileSelection.SetItems(["~~New File"] + os.listdir(self.directory + self.dataExt))
		if self.notebook.GetPageCount() > 0:
			self.notebook.DeletePage(self.notebook.GetSelection())
			if self.notebook.GetPageCount() == 0:
				self.fileSelection.SetValue("Select a file to record to")
				self.currentPage = None

	def erase(self, evt):
		evt.GetEventObject().SetValue('')

class Record_Page(wx.Panel):
	"""This page is responsible for recording data to a file 
	   created by the new file page or a file in the /Data/ folder"""

	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent.notebook)

		self.parent = parent
		self.frame = frame
                                     
		sizer = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)

		self.file = File.File(parent.fileSelection.GetValue(), parent.directory)  ##### Parameters sent to recorder, these change ####
		self.file.getData()
		self.recorder = Recording.RecordObject(self, self.file)

		self.paramSelection = wx.RadioBox(self, label='Recording Type', choices=['Seconds', 'Data Points'])
		self.valueEntry = wx.TextCtrl(self, value='Recording Value', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.indexEntry = wx.TextCtrl(self, value='Test Index', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.record = wx.Button(self, label="Record")
		self.viewRec = wx.Button(self, label="View")
		self.saveRec = wx.Button(self, label="Save")

		self.paramSelection.Bind(wx.EVT_RADIOBOX, self.updateParameter)
		self.valueEntry.Bind(wx.EVT_TEXT_ENTER, self.addValue)
		self.valueEntry.Bind(wx.EVT_SET_FOCUS, self.parent.erase) 
		self.indexEntry.Bind(wx.EVT_TEXT_ENTER, self.addIndex)
		self.indexEntry.Bind(wx.EVT_SET_FOCUS, self.parent.erase) 
		self.record.Bind(wx.EVT_BUTTON, self.beginRecording)
		self.viewRec.Bind(wx.EVT_BUTTON, self.view)
		self.saveRec.Bind(wx.EVT_BUTTON, self.save)
		self.record.Enable(False)
		self.viewRec.Enable(False)
		self.saveRec.Enable(False)
		self.hasData()

		sizer.Add(self.paramSelection, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.valueEntry, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.indexEntry, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.viewRec, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.record, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.saveRec, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox1, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox2, proportion=1, flag=wx.EXPAND)

		self.SetSizer(sizer)

	def updateParameter(self, evt):
		self.recorder.updateValue(None)
		self.recorder.updateParameter(str(self.paramSelection.GetStringSelection()))
		self.isReady()
		self.hasData()

	def addValue(self, evt):
		textEntry = evt.EventObject
		self.recorder.updateValue(str(textEntry.GetValue()))
		try:
			int(textEntry.GetValue())
		except:
			textEntry.SetValue('')
			self.recorder.updateValue(None)
		textEntry.SetValue('')
		self.isReady()
		self.hasData()

	def addIndex(self, evt):
		textEntry = evt.EventObject
		self.recorder.updateIndex(str(textEntry.GetValue()))
		self.isReady()
		self.hasData()
		evt.EventObject.SetValue('')

	def beginRecording(self, evt):
		self.recorder.dataTransfer()

	def view(self, evt):
		viewObj = View.View(None, title=self.recorder.file.name, size=(600,600))
		viewObj.giveData(self.recorder.file.data)

	def save(self, evt):
		self.recorder.save()

	def isReady(self):
		self.record.Enable(self.recorder.ready)

	def hasData(self):
		if isinstance(self.recorder.file.data, pd.DataFrame):
			self.viewRec.Enable(True)
			self.saveRec.Enable(True)
		else:
			self.viewRec.Enable(False)
			self.saveRec.Enable(False)

class New_File_Page(wx.Panel):
	"""Creates a new file with a name and column names then 
	   creates a control page with the newly created file """

	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent.notebook)

		self.parent = parent
		self.frame = frame                #Frame is needed for creating new control page
		self.file = File.File(None, parent.directory)
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.valueEntry = wx.TextCtrl(self, value='Enter File Name', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.columnEntry = wx.TextCtrl(self, value='Enter Column Names', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.createNew = wx.Button(self, label='Create File')

		self.valueEntry.Bind(wx.EVT_SET_FOCUS, self.parent.erase)
		self.valueEntry.Bind(wx.EVT_TEXT_ENTER, self.giveName)
		self.columnEntry.Bind(wx.EVT_SET_FOCUS, self.parent.erase)
		self.columnEntry.Bind(wx.EVT_TEXT_ENTER, self.giveCol)
		self.createNew.Bind(wx.EVT_BUTTON, self.newFile)
		self.createNew.Enable(False)
		self.createNew.SetFocus()

		sizer.Add(self.valueEntry, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.columnEntry, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.createNew, proportion=1, flag=wx.EXPAND)

		self.SetSizer(sizer)

	def giveName(self, evt):

		textEntry = evt.EventObject
		fileName = textEntry.GetValue()

		if ' ' not in fileName:
			self.file.setName(str(fileName) + ".csv")
			self.isReady()
		textEntry.SetValue('')

	def giveCol(self, evt):

		textEntry = evt.EventObject
		columns = textEntry.GetValue().split(' ')

		self.file.setColumns(columns)
		textEntry.SetValue('')

		self.isReady()

	def newFile(self, evt):
		notebook = self.parent.notebook
		comboBox = self.parent.fileSelection

		comboBox.SetItems(comboBox.GetItems() + [self.file.name]) 
		comboBox.SetStringSelection(self.file.name) 

		newPage = Record_Page(self.parent, self.frame)
		newPage.recorder.file = self.file

		notebook.AddPage(newPage, self.file.name)
		notebook.SetSelection(notebook.GetPageCount()-1)

		for tab in range(notebook.GetPageCount()):
			if notebook.GetPageText(tab) == "~~New File":
				notebook.DeletePage(tab)
				break

	def isReady(self):
		if self.file.name != None and self.file.columns != None:
			self.createNew.Enable(True)
