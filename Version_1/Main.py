import wx, os
import RecordCtrl, Graph, Graph_Control

class Main_Frame(wx.Frame):
	"""Main Window of the data logger application"""

	def __init__(self, parent, title, size):
		wx.Frame.__init__(self, parent, title=title, size=size)

		self.Centre()													

		self.panel = wx.Panel(self)	
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		leftSizer = wx.BoxSizer(wx.VERTICAL)			
		rightSizer = wx.BoxSizer(wx.VERTICAL)	
		space = wx.BoxSizer(wx.VERTICAL)

		self.recorder = RecordCtrl.RecordCtrl(self, os.getcwd())
		self.graphControl = Graph_Control.GraphCtrl(self, os.getcwd())

		rightSizer.Add(space, proportion=1, flag=wx.EXPAND)
		rightSizer.Add(self.recorder, proportion=1, flag=wx.EXPAND)
		leftSizer.Add(self.graphControl, proportion=1, flag=wx.EXPAND)
		sizer.Add(leftSizer, proportion=4, flag=wx.EXPAND)
		sizer.Add(rightSizer, proportion=3, flag=wx.EXPAND)

		self.panel.SetSizer(sizer)

		self.Show()

def main():
	app = wx.App()
	Main_Frame(None, "Data_Logger", (1000,600))
	app.MainLoop()

if __name__ == "__main__":
	main()