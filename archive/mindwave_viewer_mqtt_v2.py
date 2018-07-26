'''
Created on 2017. 9. 8.

@author: Kipom
'''
# -*- coding: utf-8 -*-
import pygame, sys, numpy
from numpy import *
from pygame import *
import scipy
from mindwave.pyeeg import bin_power
from mindwave.parser import ThinkGearParser, TimeSeriesRecorder
from mindwave.bluetooth_headset import connect_magic, connect_bluetooth_addr
from mindwave.bluetooth_headset import BluetoothError
from startup_sub import mindwave_startup
from startup_sub import *
#from pip._vendor.pyparsing import White

import paho.mqtt.client as mqtt

description = """Pygame Example
"""

# Set mindwave mobile
socket, args = mindwave_startup(description=description)
recorder = TimeSeriesRecorder()
parser = ThinkGearParser(recorders= [recorder])

# Set MQTT client
MQTT_name = "localhost"
Topic_name = "myo"
mqttClient = mqtt.Client("mindwave1") # Create MQTT client
try:
    mqttClient.connect(MQTT_name, 1883, 60) # Connect to MQTT server
    MQTT_connection = 0
except:
    print "MQTT Server disconnected"
    MQTT_connection = 1
    pass
    
def main():
    pygame.init()
    fpsClock= pygame.time.Clock()
    window = pygame.display.set_mode((1360,768))
    #window = pygame.display.set_mode((1360,768),pygame.FULLSCREEN)
    pygame.display.set_caption("Mindwave Viewer")

    blackColor = pygame.Color(0,0,0)
    redColor = pygame.Color(255,0,0)
    whiteColor = pygame.Color(255,255,255)
    greenColor = pygame.Color(0,255,0)
    deltaColor = pygame.Color(100,0,0)
    thetaColor = pygame.Color(0,0,255)
    alphaColor = pygame.Color(255,0,0)
    betaColor = pygame.Color(0,255,00)
    gammaColor = pygame.Color(0,255,255)

    #Set pygame parameter
    background_img = pygame.image.load("KBRI_background_1360x768.jpg")
    font = pygame.font.Font("freesansbold.ttf", 20)
    meditation_img = font.render("Meditation", False, whiteColor)
    attention_value_img = font.render("0", False, whiteColor)
    attention_img = font.render("Attention", False, whiteColor)
    address_img = font.render(args.address,False, whiteColor)

    raw_eeg = True
    spectra = []
    iteration = 0
    num_attention = 0
    attention_value = 0
    mqtt_value = attention_value
    gain = 2
    debug = True
    control_mode = False
    record_baseline = False
    quit = False

    while quit is False:
        try:
            data = socket.recv(1000)
            parser.feed(data)
            #print len(data)
        except BluetoothError:
            pass
        window.blit(background_img,(0,0))
        window.blit(address_img, (1125,100))
        if len(recorder.attention)>0:
            attention_value = int(recorder.attention[-1])
            mqtt_value = gain*attention_value
            if num_attention < len(recorder.attention): 
                # publish attention value to MQTT server
                if MQTT_connection==0: 
                    mqttClient.publish(Topic_name, str(mqtt_value)) 
                num_attention = len(recorder.attention)
            iteration+=1
            flen = 50

            if len(recorder.raw)>=500:
                spectrum, relative_spectrum = bin_power(recorder.raw[-512*3:], range(flen), 512)
                spectra.append(array(relative_spectrum))
                if len(spectra)>30:
                    spectra.pop(0)
                spectrum = mean(array(spectra),axis=0)
                for i in range (flen-1):
                    value = float(spectrum[i]*1000)
                    if i<3:
                        color = deltaColor
                    elif i<8:
                        color = thetaColor
                    elif i<13:
                        color = alphaColor
                    elif i<30:
                        color = betaColor
                    else:
                        color = gammaColor
                    if control_mode:
                        pass 
                    else:
                        pygame.draw.rect(window, color, (25+i*15, 630-value*2, 10, value*2))
            else:
                pass
            # 
            if control_mode:
                attention_value_img = font.render(str(attention_value), False, whiteColor)
                pygame.draw.circle(window, redColor, (680,384), int(attention_value))
                pygame.draw.circle(window, greenColor, (680,384), 30, 1)
                pygame.draw.circle(window, greenColor, (680,384), 60, 1)
                pygame.draw.circle(window, greenColor, (680,384), 100, 1)
                window.blit(attention_img, (620,660))
                window.blit(attention_value_img, (720,660))
                gain_value_img = font.render(str(gain), False, whiteColor)
                window.blit(gain_value_img, (720,700))
                # debug value
                if debug:
                    debug_value = mqtt_value
                    debug_value_img = font.render(str(debug_value), False, whiteColor)
                    window.blit(debug_value_img, (760,700))
                else:
		    pass
            else:
                attention_value_img = font.render(str(attention_value), False, whiteColor)
                pygame.draw.circle(window, redColor, (1200,600), int(attention_value/2))
                pygame.draw.circle(window, greenColor, (1200,600), 30/2,1)
                pygame.draw.circle(window, greenColor, (1200,600), 60/2,1)
                pygame.draw.circle(window, greenColor, (1200,600), 100/2,1)
                window.blit(attention_img, (1155,660))
                window.blit(attention_value_img, (1260,660))
                if raw_eeg:
                    lv = 0
                    for i,value in enumerate(recorder.raw[-1360:]):
                        v = value/ 4.0
                        pygame.draw.line(window, redColor, (i+25, 400-lv), (i+25, 400-v))
                        lv = v
        else:
            img = font.render("Not receiving any data from mindwave...", False, redColor)
            window.blit(img,(60,100))
            #window.blit(address_img, (1100,100))
            pass

        for event in pygame.event.get():
            if event.type==QUIT:
                quit = True
            if event.type==KEYDOWN:
                if event.key==K_ESCAPE:
                    quit = True
                if event.key==K_SPACE:
		    if control_mode==True:
                        control_mode = False
		    else:
                        control_mode = True
  		if event.key==K_UP:
                    gain = gain + 0.1
		    if gain > 3:
                        gain = 3
		    else:
			pass
  		if event.key==K_DOWN:
                    gain = gain - 0.1
		    if gain < 1:
                        gain = 1
		    else:
                        pass
                    
        pygame.display.update()
        fpsClock.tick(12)

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
