'''
Created on 2018. 10. 24.
@author: Kipom Kim
'''
# -*- coding: utf-8 -*-
import pygame, sys, numpy
from numpy import *
from pygame import *
import scipy, time
from mindwave3.pyeeg import bin_power, spectral_entropy, hjorth
from numpy.random import randn
from mindwave3.parser import ThinkGearParser, TimeSeriesRecorder
from mindwave3.bluetooth_headset import connect_magic, connect_bluetooth_addr
from mindwave3.bluetooth_headset import BluetoothError
from startup_sub import mindwave_startup
from startup_sub import *

import paho.mqtt.client as mqtt

description = """mindwave viewer with MQTT protocol
"""

# Set mindwave mobile
socket, args = mindwave_startup(description=description)
recorder = TimeSeriesRecorder()
parser = ThinkGearParser(recorders= [recorder])

# Set MQTT client
MQTT_name = "localhost"
Topic_1 = "bmi"
Topic_2 = "spider"
Topic_3 = "vib"

mqttClient = mqtt.Client("mindwave") # Create MQTT client
try:
    mqttClient.connect(MQTT_name, 1883, 60) # Connect to MQTT server
    mqtt.Client.connected_flag=True
    MQTT_connection = 0
    mqttClient.loop_start()
except:
    print("MQTT Server disconnected")
    MQTT_connection = 1
    pass
    
def main():
    fullscreen = False
    raw_eeg = True
    spectra = []
    iteration = 0
    num_attention = 0
    attention_value = 0
    entropy_value = 0
    mobility_value = 0
    complexity_value =0
    mqtt_value = 0
    gain = 1.4
    debug = False
    Max_mode = 3
    analysis_mode = 0
    record_baseline = False
    quit = False
    control_mode = False
    control_1 = True
    control_2 = False
    control_3 = True

    Th_attention = 60
    Th_entropy = 60
    Th_complexity = 200

    Th2_attention = 90
    Th2_entropy = 85
    Th2_complexity = 400

    pygame.init()
    fpsClock= pygame.time.Clock()

    if fullscreen==True:
        window = pygame.display.set_mode((1920,1080),pygame.FULLSCREEN)
    else:
        #window = pygame.display.set_mode((1920,1080),pygame.RESIZABLE)
        window = pygame.display.set_mode((1360,768),pygame.RESIZABLE)

    pygame.display.set_caption("Mindwave Viewer")

    blackColor = pygame.Color(0,0,0)
    redColor = pygame.Color(255,0,0)
    blueColor = pygame.Color(0,216,255)
    whiteColor = pygame.Color(255,255,255)
    greenColor = pygame.Color(0,255,0)
    deltaColor = pygame.Color(100,0,0)
    thetaColor = pygame.Color(0,0,255)
    alphaColor = pygame.Color(255,0,0)
    betaColor = pygame.Color(0,255,00)
    gammaColor = pygame.Color(0,255,255)
    #eegColor = pygame.Color(255,255,255)
    eegColor = pygame.Color(255,255,0)
    entropyColor = pygame.Color(0,0,255)

    #Set pygame parameter
    background_img_0 = pygame.image.load("Mindwave_1360x968_mode0.jpg")
    background_img_1 = pygame.image.load("Mindwave_1360x968_mode1.jpg")
    background_img_2 = pygame.image.load("Mindwave_1360x968_mode2-1.jpg")
    font = pygame.font.Font("freesansbold.ttf", 20)
    font_title = pygame.font.Font("freesansbold.ttf", 30)
    #meditation_txt_img = font.render("Meditation", False, whiteColor)
    attention_txt_img = font.render("Attention", False, whiteColor)
    attention_value_img = font.render("0", False, whiteColor)
    entropy_txt_img = font.render("Entropy", False, whiteColor)
    entropy_value_img = font.render("0", False, whiteColor)
    address_txt_img = font.render(args.address,False, whiteColor)

    while quit is False:
        try:
            data = socket.recv(1024)
            parser.feed(data)
        except BluetoothError:
            pass
        #window.blit(background_img_0,(0,0))
        #window.blit(address_txt_img, (1125,100))
        if analysis_mode == 0:
            window.blit(background_img_0,(0,0))
        elif analysis_mode == 1:
            window.blit(background_img_1,(0,0))
        elif analysis_mode == 2:
            window.blit(background_img_2,(0,0))
        else:
            mode_img = font_title.render(" ", False, whiteColor)
            window.blit(mode_img, (550,100))

        if control_mode == True:
            mode_img = font.render("Control On", False, blueColor)
            window.blit(mode_img, (1020,730))
            if control_1==True:
                txt_img = font.render("Car", False, redColor)
                window.blit(txt_img, (1020,755))
            if control_2==True:
                txt_img = font.render("Spider", False, redColor)
                window.blit(txt_img, (1080,755))
        else:
            mode_img = font.render("press F1 for control mode", False, whiteColor)
            window.blit(mode_img, (1000,730))

        if len(recorder.attention)>0:
            attention_value = int(recorder.attention[-1])
            iteration+=1
            flen = 50
            if len(recorder.raw)>=512:
                if analysis_mode==1:
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
                        pygame.draw.rect(window, color, (150+i*22, 530-value*3, 18, value*3))
                elif analysis_mode==2:
                    #entropy_value = 100*spectral_entropy(recorder.raw[-512*3:], range(flen), 512)
		            #entropy_value = 2*(entropy_value-50)
                    if debug==True:
                        print(entropy_value)
                    pass
                elif analysis_mode==0:
                    #mobility_value, complexity_value = hjorth(recorder.raw[-512*3:])
                    if debug==True:
                        print(mobility_value)
                    pass
                else:
                    pass
            else:
                pass
            #Show raw EEG signal
            if raw_eeg:
                lv = 0
                for i,value in enumerate(recorder.raw[-1360:]):
                    v = value/ 8.0
                    if analysis_mode==0:
                        pygame.draw.line(window, eegColor, (i+25, 400-lv), (i+25, 400-v))
                    else:
                        pygame.draw.line(window, eegColor, (i+25, 400-lv), (i+25, 400-v))
                    lv = v
                raw_img = font.render("press e key to hide Raw EEG", False, whiteColor)
                window.blit(raw_img, (150,730))
            else:
                raw_img = font.render("press e key to show Raw EEG", False, whiteColor)
                window.blit(raw_img, (150,730))

            #MQTT publish
            #if num_attention < len(recorder.attention): 
            if analysis_mode==0:
                if gain*attention_value > Th_attention and gain*attention_value < Th2_attention :
                    mqtt_value = 11
                elif gain*attention_value > Th2_attention:
                    mqtt_value = 22
                else :
                    mqtt_value = 0
            elif analysis_mode==2:
                if gain*attention_value > Th_attention and gain*attention_value < Th2_attention :
                    mqtt_value = 11
                elif gain*attention_value > Th2_attention:
                    mqtt_value = 22
                else :
                    mqtt_value = 0
            else:
                mqtt_value = 0

            if mqttClient.connected_flag == True:
                MQTT_connection = 0
            else:
                MQTT_connection = 1
            #MQTT_connection_img = font.render(str(MQTT_connection), False, whiteColor)
            #window.blit(MQTT_connection_img, (1260,100))
            # publish attention value to MQTT server
            if MQTT_connection==0: 
                if control_mode == True:
                    if control_1 == True:
                        mqttClient.publish(Topic_1, str(mqtt_value))
                    else:
                        pass
                    if control_2 == True:
                        mqttClient.publish(Topic_2, str(mqtt_value))
                    else:
                        pass
                    if control_3 == True:
                        mqttClient.publish(Topic_3, str(mqtt_value))
                    else:
                        pass
                else:
                #mqttClient.publish(Topic_3, str(mqtt_value))
                    pass
            num_attention = len(recorder.attention)
            if debug==True:
                print(num_attention)
                print(mqtt_value)
                print(MQTT_connection)
            if analysis_mode==1:
                pygame.draw.circle(window, redColor, (1620,860), int(attention_value/2))
                pygame.draw.circle(window, greenColor, (1620,860), int(30/2),1)
                pygame.draw.circle(window, greenColor, (1620,860), int(60/2),1)
                pygame.draw.circle(window, greenColor, (1620,860), int(100/2),1)
                window.blit(attention_txt_img, (1575,920))
                #attention_value_img = font.render(str(attention_value), False, whiteColor)
                #window.blit(attention_value_img, (1580,920))
            elif analysis_mode==2:
                attention_value_img = font.render(str(int(gain*attention_value)), False, whiteColor)
                if int(gain*attention_value) > 100:
                    pygame.draw.circle(window, whiteColor, (678,394), 140, 1)
                elif int(gain*attention_value) < 8:
                    pygame.draw.circle(window, whiteColor, (678,394), 1)
                else:
                    pygame.draw.circle(window, whiteColor, (678,394), int(1.4*gain*attention_value), 1)
                #pygame.draw.circle(window, whiteColor, (680,384), 30,1)
                #pygame.draw.circle(window, greenColor, (680,384), Th_attention, 1)
                #pygame.draw.circle(window, blueColor, (680,384), Th2_attention, 1)
                #pygame.draw.circle(window, whiteColor, (680,384), 120, 1)
                window.blit(attention_txt_img, (600,612))
                window.blit(attention_value_img, (725,612))
                gain_value_img = font.render(str(gain), False, whiteColor)
                window.blit(gain_value_img, (725,650))
                #debug_value = mqtt_value
                #debug_value_img = font.render(str(debug_value), False, whiteColor)
                #window.blit(debug_value_img, (680,612))
            #else:
		    #    pass
            elif analysis_mode==0:
                #debug value
                if debug:
                    debug_value = mqtt_value
                    #debug_value_img = font.render('%.2f'%(debug_value), False, whiteColor)
                    window.blit(debug_value_img, (760,670))
                else:
                    pass
            else:
                pass

        else:
            Wait_txt_img = font.render("Wait!!..Not yet receiving data from mindwave.", False, redColor)
            window.blit(Wait_txt_img,(60,130))
            #window.blit(address_img, (1100,100))
            pass

        #Get pygame event (ESC, SPACE, Up, Down, F1)
        for event in pygame.event.get():
            if event.type==QUIT:
                quit = True
                if MQTT_connection==0:
                    mqttClient.publish(Topic_1, "0")
                    mqttClient.publish(Topic_2, "0")
                    mqttClient.publish(Topic_3, "0")
            if event.type==KEYDOWN:
                if event.key==K_ESCAPE:
                    quit = True
                    if MQTT_connection==0:
                        mqttClient.publish(Topic_1, "0") 
                        mqttClient.publish(Topic_2, "0")
                        mqttClient.publish(Topic_3, "0")
                if event.key==K_SPACE:
                    analysis_mode = analysis_mode + 1
                    if analysis_mode == 0:
                        raw_eeg = True
                        analysis_mode = 0
                    elif analysis_mode == 1:
                        raw_eeg = False
                    elif analysis_mode == 2:
                        raw_eeg = False
                    elif analysis_mode == 3:
                        raw_eeg = True
                        analysis_mode = 0
                    else:
                        pass
                if event.key==K_F1:
                    if control_mode == True:
                        control_mode = False
                        if MQTT_connection==0:
                            mqttClient.publish(Topic_1, "0")
                            mqttClient.publish(Topic_2, "0")
                            mqttClient.publish(Topic_3, "0")
                    else:
                        control_mode = True
                if event.key==K_e:
                    if raw_eeg == True:
                        raw_eeg = False
                    else:
                        raw_eeg = True
                if event.key==K_1:
                    if control_1 == True:
                        control_1 = False
                        if MQTT_connection==0:
                            mqttClient.publish(Topic_1, "0")
                    else:
                        control_1 = True
                if event.key==K_2:
                    if control_2 == True:
                        control_2 = False
                        if MQTT_connection==0:
                            mqttClient.publish(Topic_2, "0")
                    else:
                        control_2 = True
                if event.key==K_UP:
                    gain = gain + 0.1
                    if gain > 3:
                        gain = 3
                    else:
                        pass
                if event.key==K_DOWN:
                    gain = gain - 0.1
                    if gain < 0.5:
                        gain = 0.5
                    else:
                        pass
                if event.key==K_RIGHT:
                    if control_mode == True:
                        if MQTT_connection==0:
                            mqttClient.publish(Topic_1, "11") 
                            mqttClient.publish(Topic_2, "11")
                            #mqttClient.publish(Topic_3, "11")
                if event.key==K_LEFT:
                    if control_mode == True:
                        if MQTT_connection==0:
                            mqttClient.publish(Topic_1, "22") 
                            mqttClient.publish(Topic_2, "22")
                            #mqttClient.publish(Topic_3, "22")
                if event.key==K_END:
                    if MQTT_connection==0:
                        mqttClient.publish(Topic_1, "0") 
                        mqttClient.publish(Topic_2, "0")
                        #mqttClient.publish(Topic_3, "0")
        #Display update            
        pygame.display.update()
        fpsClock.tick(12)

#mqtt close
#mqttClient.loop_stop()
#mqttClient.disconnect()

if __name__ == '__main__':
    try:
        main()
    finally:
        #mqtt close
        mqttClient.loop_stop()
        mqttClient.disconnect()
        pygame.quit()
