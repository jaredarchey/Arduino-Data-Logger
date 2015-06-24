import serial, time, re, wx, os
import pandas as pd
import numpy as np
from Recorder import *
from New_File import *
from File import *
from View import *

class Menubar(object):

	def __init__(self, window, directory):

		self.window = window
		self.directory = directory

		self.__menubar = wx.MenuBar()

		self.fileMenu = wx.Menu()    #File > Open|New
		self.openMenu = wx.Menu()    #File > Open
		for i, file in enumerate(os.listdir(self.directory)):
			added = self.openMenu.Append(201+i, file, file)
			self.window.Bind(wx.EVT_MENU, self.selectFile, added)
		self.editMenu = wx.Menu()    #File > Edit
		self.viewMenu = wx.Menu()    #View
		self.recordMenu = wx.Menu()  #Record

		self.fileMenu.AppendMenu(101, 'Open', self.openMenu) #Add the open submenu to the file menu of the menubar
		self.fileNew = self.fileMenu.Append(wx.ID_NEW, 'New')
		self.fileEdit = self.editMenu.Append(wx.ID_PASTE, 'Edit')
		self.fileView = self.viewMenu.Append(wx.ID_PASTE, 'View')
		self.fileRecord = self.recordMenu.Append(wx.ID_OPEN, 'Record')

		self.__menubar.Append(self.fileMenu, 'File') #Add the file menu to menubar
		self.__menubar.Append(self.editMenu, 'Edit') #Add the file menu to menubar
		self.__menubar.Append(self.viewMenu, 'View')
		self.__menubar.Append(self.recordMenu, 'Record')

		self.window.Bind(wx.EVT_MENU, self.newFile, self.fileNew)
		self.window.Bind(wx.EVT_MENU, self.editFile, self.fileEdit)
		self.window.Bind(wx.EVT_MENU, self.viewFile, self.fileView)
		self.window.Bind(wx.EVT_MENU, self.recordFile, self.fileRecord)

		self.window.SetMenuBar(self.__menubar)

	def selectFile(self, evt): #Only way to set current file
		fileName = self.window.GetMenuBar().FindItemById(evt.GetId()).GetLabel()
		self.window.setFile(File(self.directory + fileName))

	def addFile(self, file): #When a new file is created and saved, it is then added to the file list
		labels = []
		for item in self.openMenu.GetMenuItems(): labels.append(item.GetLabel())
		if file not in labels:
			added = self.openMenu.Append(201+self.openMenu.GetMenuItemCount(), file)
			self.window.Bind(wx.EVT_MENU, self.selectFile, added)

	def newFile(self, evt): #File > New
		NewFile_Window(self.window)   

	def editFile(self, evt):
		pass #This is where I'm at   

	def viewFile(self, evt): #View
		if hasattr(self.window.getFile(), "data"):
			view = View(self.window)
			view.giveData(self.window.getFile().data)

	def recordFile(self, evt): #Record
		if self.window.hasFile():
			record = RecordCtrl(self.window) #The record ctrl is the only way the recorder can be used