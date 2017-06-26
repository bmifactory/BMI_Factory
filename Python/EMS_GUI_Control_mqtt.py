'''
Created on 2017. 5. 15.

@author: Kipom
'''
# -*- coding: utf-8 -*-
import wx, time
import paho.mqtt.client as mqtt

# Set MQTT client
MQTT_name = "localhost"
Topic_name = "ems"
mqttClient = mqtt.Client() # Create MQTT client
try:
    mqttClient.connect(MQTT_name, 1883, 60) # Connect to MQTT server
    print "MQTT Server connected"
    MQTT_connection = 0
except:
    print "MQTT Server disconnected"
    MQTT_connection = 1
    pass

class LeftPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.LeftSlide1 = wx.Slider(self, -1, 100, 100, 1000, (-1, 10), (200, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.LeftSlide2 = wx.Slider(self, -1, 100, 0, 100, (-1, 80), (200, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
        button1 = wx.Button(self, -1, 'Channel 1', (50, 150))
        self.Bind(wx.EVT_BUTTON, self.OnLeftButton, id=button1.GetId())
        valueText = 'C1T'+str(self.LeftSlide1.GetValue())+'I'+str(self.LeftSlide2.GetValue())
        self.text = wx.StaticText(self, -1, valueText, (55, 200))
        #self.text = parent.GetParent().rightPanel.text       
    def OnLeftButton(self, event):
        valueText = 'C1T'+str(self.LeftSlide1.GetValue())+'I'+str(self.LeftSlide2.GetValue())       
        self.text.SetLabel(valueText)
        if MQTT_connection==0: 
            mqttClient.publish(Topic_name, valueText) 
            time.sleep(self.LeftSlide2.GetValue()/1000.0)
            self.text.SetLabel(valueText+'*')

class RightPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.RightSlide1 = wx.Slider(self, -1, 100, 100, 1000, (-1, 10), (200, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.RightSlide2 = wx.Slider(self, -1, 100, 0, 100, (-1, 80), (200, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
        button2 = wx.Button(self, -1, 'Channel 2', (50, 150))
        self.Bind(wx.EVT_BUTTON, self.OnRightButton, id=button2.GetId())
        valueText = 'C2T'+str(self.RightSlide1.GetValue())+'I'+str(self.RightSlide2.GetValue()) 
        self.text = wx.StaticText(self, -1, valueText, (55, 200))
    def OnRightButton(self, event):
        valueText = 'C2T'+str(self.RightSlide1.GetValue())+'I'+str(self.RightSlide2.GetValue())       
        self.text.SetLabel(valueText)
        if MQTT_connection==0: 
            mqttClient.publish(Topic_name, valueText)
            time.sleep(self.RightSlide2.GetValue()/1000.0)
            self.text.SetLabel(valueText+'*')

class Communicate(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(450, 300))
        panel = wx.Panel(self, -1)
        #self.rightPanel = RightPanel(panel, -1)
        rightPanel = RightPanel(panel, -1)
        leftPanel = LeftPanel(panel, -1)
        hbox = wx.BoxSizer()
        hbox.Add(leftPanel, 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND | wx.ALL, 5)
#       hbox.Add(self.rightPanel, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(hbox)
        self.Centre()
        self.Show(True)
              
app = wx.App()
Communicate(None, -1, 'EMS Control')
app.MainLoop()