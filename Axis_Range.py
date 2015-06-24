import wx
import numpy as np

class Axis_Range(wx.Panel):
	"""Creates a double slider to select a range, updates the graphs min max axis values"""

	def __init__(self, parent, axis, Min, Max):
		wx.Panel.__init__(self, parent)

		self.parent = parent
		if axis == 'x':
			style = wx.SL_HORIZONTAL
			type1 = wx.TOP
			type2 = wx.BOTTOM
			orientation = wx.VERTICAL
		elif axis == 'y':
			style = wx.SL_VERTICAL
			type1 = wx.LEFT
			type2 = wx.RIGHT
			orientation = wx.HORIZONTAL
		else:
			raise ValueError, "Axis needs to be 'x' or 'y'"

		self.sizer = wx.BoxSizer(orientation)

		self.minVal = Min
		self.maxVal = Max

		self.min = wx.Slider(self, value=self.minVal, minValue=self.minVal, maxValue=self.maxVal, style=style)
		self.max = wx.Slider(self, value=self.maxVal, minValue=self.minVal, maxValue=self.maxVal, style=style)
		self.min.Bind(wx.EVT_SCROLL, self.__setValues)
		self.max.Bind(wx.EVT_SCROLL, self.__setValues)

		self.sizer.Add(self.min, proportion=1, border=10, flag=wx.EXPAND|type1)
		self.sizer.Add(self.max, proportion=1, border=10, flag=wx.EXPAND|type2)

		self.SetSizer(self.sizer)

	def setRange(self, Range):    #Called by plot panel
		if Range[0] == Range[1]:
			Range[1] += 1
		self.min.SetMin(-5)
		self.max.SetMin(-5)
		self.min.SetMax(Range[1])
		self.min.SetMin(Range[0])
		self.min.SetValue(Range[0])
		self.max.SetMax(Range[1])
		self.max.SetMin(Range[0])
		self.max.SetValue(Range[1])
		self.minVal = Range[0]
		self.maxVal = Range[1]

	def getRange(self): #Called by plot panel
		return [self.minVal, self.maxVal]

	def __setValues(self, evt): #Called by slider event
		self.__adjustAxes()
		self.minVal = self.min.GetValue()
		self.maxVal = self.max.GetValue()
		self.parent.setRange()

	def __adjustAxes(self):
		if self.min.GetValue() > self.max.GetValue():
			self.min.SetValue(self.max.GetValue())
			self.max.SetValue(self.min.GetValue())