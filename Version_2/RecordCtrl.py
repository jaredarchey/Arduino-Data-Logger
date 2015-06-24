import wx

class RecordCtrl(wx.Frame):
	"""This page is responsible for recording data to a file 
	   created by the new file page or a file in the /Data/ folder"""

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, title="Record Data", size=(200,200))

		self.parent = parent
		self.panel = wx.Panel(self)
                                     
		sizer = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)

		"""Set attributes parameter, value, and test index to recorder object"""

		self.paramSelection = wx.RadioBox(self.panel, label='Recording Type', choices=['Seconds', 'Data Points'], style=wx.RA_SPECIFY_ROWS)
		self.valueEntry = wx.TextCtrl(self.panel, value='Value', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.indexEntry = wx.TextCtrl(self.panel, value='Index', style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
		self.record = wx.Button(self.panel, label="Record")
		self.saveRec = wx.Button(self.panel, label="Save")

		self.paramSelection.Bind(wx.EVT_RADIOBOX, self.updateParameter)
		self.valueEntry.Bind(wx.EVT_TEXT_ENTER, self.addValue)
		self.valueEntry.Bind(wx.EVT_SET_FOCUS, self.erase) 
		self.indexEntry.Bind(wx.EVT_TEXT_ENTER, self.addIndex)
		self.indexEntry.Bind(wx.EVT_SET_FOCUS, self.erase) 
		self.record.Bind(wx.EVT_BUTTON, self.beginRecording)
		self.saveRec.Bind(wx.EVT_BUTTON, self.save)
		self.record.Enable(False)
		self.saveRec.Enable(False)
		self.hasData()

		sizer.Add(self.paramSelection, proportion=2, flag=wx.EXPAND)
		hbox1.Add(self.valueEntry, proportion=1, flag=wx.EXPAND)
		hbox1.Add(self.indexEntry, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.record, proportion=1, flag=wx.EXPAND)
		hbox2.Add(self.saveRec, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox1, proportion=1, flag=wx.EXPAND)
		sizer.Add(hbox2, proportion=1, flag=wx.EXPAND)

		self.panel.SetSizer(sizer)

		self.Centre()
		self.Show()

	def updateParameter(self, evt):
		self.parent.recorder.setParameter(evt.EventObject.GetStringSelection())
		self.parent.recorder.setValue(None)
		self.isReady()
		self.hasData()

	def addValue(self, evt):
		textEntry = evt.EventObject
		if str(textEntry.GetValue()).isdigit():
			self.parent.recorder.setValue(str(textEntry.GetValue()))
		textEntry.SetValue('')
		self.isReady()
		self.hasData()

	def addIndex(self, evt):
		textEntry = evt.EventObject
		self.parent.recorder.setIndex(str(textEntry.GetValue()))
		self.isReady()
		self.hasData()
		evt.EventObject.SetValue('')

	def beginRecording(self, evt):
		self.parent.recorder.dataTransfer()

	def save(self, evt):
		self.parent.recorder.save()

	def isReady(self):
		if self.parent.recorder.canRecord():
			self.record.Enable(True)
		else:
			self.record.Enable(False)

	def hasData(self):
		if hasattr(self.parent.recorder.file, "data"):
			self.saveRec.Enable(True)
		else:
			self.saveRec.Enable(False)

	def erase(self, evt):
		evt.EventObject.SetValue('')