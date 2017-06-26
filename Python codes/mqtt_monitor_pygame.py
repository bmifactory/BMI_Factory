'''
Created on 2017. 5. 29.

@author: Kipom
'''
import pygame, sys, numpy
import scipy
import paho.mqtt.client as mqtt
from numpy import *
from pygame import *
from pip._vendor.pyparsing import White

description = """MQTT monitor using Pygame
"""

# Set MQTT client
#MQTT_name = "192.168.0.2"
MQTT_name = "localhost"
Topic_name = "bmi"
mqtt_event = 0 
message_range = 20
plot_range = 100
myo_plot_list= range(plot_range)
mind_plot_list= range(plot_range)
topic_list = range(message_range)
message_list = range(message_range)
myo_plot_event = 0
mind_plot_event = 0
base_position_x=500
zoom_x = 5
myo_base_position_y=200
mind_base_position_y=500
zoom_y = 0.1

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("bmi")
    client.subscribe("ems")
    client.subscribe("mind")
    client.subscribe("myo")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global mqtt_event,myo_plot_event, myo_plot_list, topic_list,message_list 
    topic_list[mqtt_event]="["+msg.topic+"]"
    message_list[mqtt_event]=str(msg.payload)
    if msg.topic=="myo":
        myo_plot_list[myo_plot_event]=int(str(msg.payload))       
    pygame_update(mqtt_event,myo_plot_event)     
    if mqtt_event>=message_range-1:
        mqtt_event = 0
    else:
        mqtt_event = mqtt_event+1
    if (msg.topic=="myo"):    
        if myo_plot_event>plot_range:
            myo_plot_event = 0
            myo_plot_list[myo_plot_event]=int(str(msg.payload))
        else:
            myo_plot_event = myo_plot_event + 1
        
def on_disconnect(client, userdata, rc=0):
    print("DisConnected result code "+str(rc))
    client.loop_stop()

def setup():
    global window, fpsClock, font, mqtt_event, plot_event
    # Create MQTT client
    mqttClient = mqtt.Client() 
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    try:
        mqttClient.connect(MQTT_name, 1883, 60) # Connect to MQTT server
        print "MQTT Server connected"
        MQTT_connection = 0
        mqttClient.loop_start()
    except:
        print "MQTT Server disconnected"
        MQTT_connection = 1
        pass       
    pygame.init()
    fpsClock= pygame.time.Clock()
    window = pygame.display.set_mode((1280,720))
    pygame.display.set_caption("MQTT monitor")
    pygame_update(mqtt_event, myo_plot_event)

def pygame_update(message_lane, plot_event): 
    global topic_list, message_list, lv, window
    whiteColor = pygame.Color(255,255,255)
    greenColor = pygame.Color(0,255,0)
    redColor = pygame.Color(255,0,0)
    yellowColor = pygame.Color(255,228,0)
        
    background_img = pygame.image.load("KBRI_background2.jpg")
    font = pygame.font.Font("freesansbold.ttf", 20)
    window.blit(background_img,(0,0))
    mqtt_topic_img = font.render("Topic", False, whiteColor)
    window.blit(mqtt_topic_img, (100,50))
    mqtt_message_img = font.render("Message", False, whiteColor)
    window.blit(mqtt_message_img, (170,50))
    for i in range(20): 
        if (i<message_lane):
            mqtt_topic_img = font.render(str(topic_list[i]), False, greenColor)
            window.blit(mqtt_topic_img, (100,80+i*30))
            mqtt_message_img = font.render(str(message_list[i]), False, greenColor)
            window.blit(mqtt_message_img, (170,80+i*30))
        elif(i==message_lane):
            mqtt_topic_img = font.render(str(topic_list[i]), False, redColor)
            window.blit(mqtt_topic_img, (100,80+i*30))            
            mqtt_message_img = font.render(str(message_list[i]), False, redColor)
            window.blit(mqtt_message_img, (170,80+i*30))            
        else:
            mqtt_topic_img = font.render("", False, greenColor)
            window.blit(mqtt_topic_img, (100,80+i*30))
            mqtt_message_img = font.render("", False, greenColor)
            window.blit(mqtt_message_img, (170,80+i*30))
    lv=myo_plot_list[0]
    for j in range(myo_plot_event+1):
        v=myo_plot_list[j]
        pygame.draw.line(window, yellowColor, 
            ((j)*zoom_x+base_position_x, myo_base_position_y-lv*zoom_y), 
            ((j+1)*zoom_x+base_position_x, myo_base_position_y-v*zoom_y))
        lv=v
                    
    pygame.display.update()    
    
def main():
    quit = False
    while quit is False:
        #window.blit(background_img,(0,0))
        # publish attention value to MQTT server
        #if MQTT_connection==0: 
            #mqttClient.publish(Topic_name, "bmi") 
        for event in pygame.event.get():
            if event.type==QUIT:
                quit = True
            if event.type==KEYDOWN:
                if event.key==K_ESCAPE:
                    quit = True                    
        #pygame.display.update()
        fpsClock.tick(12)

if __name__ == '__main__':
    try:
        setup()
        main()
    finally:
        pygame.quit()
