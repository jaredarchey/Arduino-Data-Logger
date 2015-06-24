import wx

class Status(wx.BoxSizer):

	def __init__(self, frame, orientation):
		wx.BoxSizer.__init__(self, orientation)

		self.frame = frame                        #Object attributes
		self.vboxR = wx.BoxSizer(wx.VERTICAL)

		labels = ['\t\tStatus Box', 'Current_File: None', 'Columns: None', 'Has_Data: False', 'Parameter: Seconds', 'Value: None', 'Test_Index: None', 'Recording: False', 'Plot_Type: None']
		self.list = wx.ListBox(self.frame.panel, choices=labels)

		self.vboxR.Add(self.list, proportion=1, flag=wx.EXPAND)
		self.Add(self.vboxR, proportion=1, flag=wx.EXPAND)

	def getKey(self):
		return {"title":self.list.GetString(0),
				"name":self.list.GetString(1), 
			    "columns":self.list.GetString(2), 
		        "hasData":self.list.GetString(3), 
			    "recType":self.list.GetString(4), 
			    "recValue":self.list.GetString(5),
			    "index": self.list.GetString(6),
			    "isRecording":self.list.GetString(7),
			    "plotType":self.list.GetString(8)}

	def changeLabel(self, label, newLabel):
		key = self.getKey()
		self.list.SetString(self.list.FindString(key[label]), key[label].split(' ')[0] + ' ' + newLabel)


