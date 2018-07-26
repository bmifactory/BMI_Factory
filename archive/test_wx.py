'''
Created on 2017. 5. 14.

@author: Kipom
'''
import wx

class MainWindow(wx.Frame):

    def __init__(self, parent, title):

        wx.Frame.__init__(self, parent, title=title)

        # Bind a "paint" event for the frame to the
        # "OnPaint" method
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Show()


    def OnPaint(self, event):

        dc = wx.PaintDC(self)

        # Set a red brush to draw a rectangle
        dc.SetBrush(wx.RED_BRUSH)
        dc.DrawRectangle(10, 10, 50, 50)
        
app = wx.App(False)
frame = MainWindow(None, 'Sample application')
app.MainLoop()