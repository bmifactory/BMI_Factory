'''
Created on 2017. 5. 11.

@author: Kipom
'''
import time
from NeuroPy import NeuroPy

def attention_callback(attention_value):
    #"this function will be called everytime NeuroPy has a new value for attention"
    print "Value of attention is",attention_value
    #do other stuff (fire a rocket), based on the obtained value of attention_value
    #do some more stuff
    return None

mindwaveObj=NeuroPy("COM10",9600) #If port not given 57600 is automatically assumed
                        #object1=NeuroPy("/dev/rfcomm0") for linux
#set call back:
mindwaveObj.setCallBack("attention",attention_callback)

#call start method
mindwaveObj.start()

#print "Wait 10 sec."
#time.sleep(10)

while True:
    #print "attention:", object1.rawValue
    if(mindwaveObj.meditation>90): #another way of accessing data provided by headset (1st being call backs)
        mindwaveObj.stop()         #if meditation level reaches above 70, stop fetching data from the headset
    time.sleep(1)