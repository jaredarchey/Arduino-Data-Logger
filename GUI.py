import wx, os
from File import *
from Menubar import *
from PlotPanel import *
from PPanel import *

class Window(wx.Frame):

	def __init__(self, parent, title="Data Logger", size=(600,600)):
		wx.Frame.__init__(self, parent, title=title, size=size)

		self.Centre()
		
		self.directory = os.getcwd() + '/Data/'
		self.__file = None
		self.recorder = Recorder(port='/dev/ttyACM0', baud=115200) #Add a recorder object to the frame, has no ctrl so it cannot be used yet

		self.menu = Menubar(self, self.directory) #Handles file selection, creation, and recording
		self.graph = PPanel(self)
		#self.graph = PlotPanel(self)               #Handles the graphing of the selected file, has no access to change file

		self.Show()

	def setFile(self, file):
		"""This method is the only was to change the files for the recorder and the graph"""
		assert(isinstance(file, File)), "File must be an instance of a file object\nInstead recieved: " + str(file)

		self.__file = file
		self.recorder.setFile(file)
		if hasattr(file, "data"):
			self.graph.setFile(file)
		print "Current File: " + str(file.name)

	def saveFile(self):                       #Called from recCtrl
		file = self.recorder.save()
		self.setFile(file)
		self.menu.addFile(file.name)

	def getFile(self):
		return (self.__file if isinstance(self.__file, File) else False)

	def hasFile(self):
		return (True if isinstance(self.__file, File) else False)

app = wx.App()
Window(None)
app.MainLoop()