"""
tellopy sample using keyboard and video player
- you must install mplayer to replay the video
"""
import time
import sys
import os
import tellopy
import pygame
from pygame import *
from subprocess import Popen, PIPE
import paho.mqtt.client as mqtt

#For MQTT
MQTT_name = "localhost"
#MQTT_name = "192.168.0.2"
Topic_name = "tello1"

# For tello
tello_connected = True
control_mode = True
game_mode = True
video_stream = True
prev_flight_data = None
video_player = None
battary = 10
altitude = 0
speed = 50
duration = 500
dir_flag = 0
updown_flag = 0
rot_flag = False
throttle = 0.0
yaw = 0.0
pitch = 0.0
roll = 0.0
start_time = 0.0
takeoff_time = 0.0
land_time = 0.0
fly_time = 0.0
set_time = 30.
takeoff_flag = False

# Set pygame parameter
fullscreen = False
os.environ['SDL_VIDEO_WINDOW_POS']="%d, %d" % (1360,0)
bg_file_1="Tello_bg_1.jpg"
bg_file_2="Tello_bg_2.jpg"
message_max = 5
message_list = list(range(message_max))
event_log = 0

def init_tello():
    global drone, speed, throttle, yaw, pitch, roll
    drone = tellopy.Tello()
    drone.connect()
    #drone.set_video_encoder_rate(10)
    drone.subscribe(drone.EVENT_FLIGHT_DATA, tello_handler)
    if video_stream:
        drone.start_video()
        pygame.time.wait(2)
        drone.subscribe(drone.EVENT_VIDEO_FRAME, tello_handler)

def init_pygame():
    global window, background_img, font, fpsClock
    global blackColor, blueColor, whiteColor, greenColor, redColor
    pygame.init()
    font = pygame.font.Font("bgothl.ttf", 20)
    blackColor = pygame.Color(0, 0, 0)
    redColor = pygame.Color(255, 0, 0)
    blueColor = pygame.Color(0, 0, 255)
    whiteColor = pygame.Color(255, 255, 255)
    greenColor = pygame.Color(0, 255, 0)
    window = pygame.display.set_mode((560, 575), pygame.RESIZABLE)
    background_img = pygame.image.load(bg_file_1)
    pygame_update(event_log)
    # fpsClock = pygame.time.Clock()

def init_mqtt():
    # Create MQTT client
    mqttClient = mqtt.Client("Tello1")
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    # mqttClient.on_message = on_disconnect
    # Connect to MQTT server
    try:
        mqttClient.connect(MQTT_name, 1883, 60)
        print("MQTT Server connected")
        MQTT_connection = 0
        mqttClient.loop_start()
    except:
        print("MQTT Server disconnected")
        MQTT_connection = 1
        pass

def tello_handler(event, sender, data, **args):
    global prev_flight_data
    global video_player
    global battary, altitude, event_log
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        if prev_flight_data != str(data):
            #print(data)
            flight_data = str(data)
            splited = flight_data.split(', ')
            for x in splited:
                a, b = x.split('=')
                if a == 'height':
                    altitude = int(b)
                    #print('Height = %d' % altitude)
                if a == 'battery_percentage':
                    battary = int(b)
                    #print('Battery = %d' % battary)
                print('Altitude = %d, Battery = %d' % (altitude, battary))
            pygame_update(event_log)
            prev_flight_data = str(data)
    elif event is drone.EVENT_VIDEO_FRAME:
        if video_player is None:
            video_player = Popen(['mplayer', '-xy', '560', '-geometry', '1360:660', '-fps', '35', '-'], stdin=PIPE)
        try:
            video_player.stdin.write(data)
        except IOError as err:
            #print(err)
            video_player = None
    #else:
    #    print('event="%s" data=%s' % (event.getname(), str(data)))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(Topic_name)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global event_log, dir_flag, updown_flag, background_img
    global takeoff_time, takeoff_flag, land_time, set_time
    if msg.topic == Topic_name:
        command_str = str(msg.payload)
        print(command_str)
        if command_str == "b'takeoff'":
            background_img = pygame.image.load(bg_file_2)
            takeoff_time = pygame.time.get_ticks()
            if tello_connected:
                drone.takeoff()
            takeoff_flag = True
        elif command_str == "b'land'":
            background_img = pygame.image.load(bg_file_1)
            if takeoff_flag == True:
                land_time = pygame.time.get_ticks()
            if tello_connected:
                drone.land()
            takeoff_flag = False
        elif command_str == "b'level1'":
            set_time = set_time + 1
            if tello_connected:
                if dir_flag == 0:
                    drone.counter_clockwise(speed)
                    pygame.time.wait(2000)
                    drone.counter_clockwise(0)
                    dir_flag = 1
                elif dir_flag == 1:
                    drone.clockwise(speed)
                    pygame.time.wait(2000)
                    drone.clockwise(0)
                    dir_flag = 0
        elif command_str == "b'level2'":
            set_time = set_time + 3
            if tello_connected:
                if battary > 50:
                    drone.flip_forward()
                else:
                    if dir_flag == 0:
                        drone.counter_clockwise(speed)
                        pygame.time.wait(2000)
                        drone.counter_clockwise(0)
                        dir_flag = 1
                    elif dir_flag == 1:
                        drone.clockwise(speed)
                        pygame.time.wait(2000)
                        drone.clockwise(0)
                        dir_flag = 0
        elif command_str == "b'left'":
            if tello_connected:
                    drone.left(speed)
                    pygame.time.wait(duration)
                    drone.left(0)
        elif command_str == "b'right'":
            if tello_connected:
                    drone.right(speed)
                    pygame.time.wait(duration)
                    drone.right(0)
        elif command_str == "b'forward'":
            if tello_connected:
                    drone.forward(speed)
                    pygame.time.wait(duration)
                    drone.forward(0)
        elif command_str == "b'back'":
            if tello_connected:
                    drone.backward(speed)
                    pygame.time.wait(duration)
                    drone.backward(0)
        elif command_str == "b'cw'":
            if tello_connected:
                    drone.counter_clockwise(speed)
                    pygame.time.wait(duration)
                    drone.counter_clockwise(0)
        elif command_str == "b'cw'":
            if tello_connected:
                    drone.clockwise(speed)
                    pygame.time.wait(duration)
                    drone.clockwise(0)
        elif command_str == "b'ccw'":
            if tello_connected:
                    drone.counter_clockwise(speed)
                    pygame.time.wait(duration)
                    drone.counter_clockwise(0)
        elif command_str == "b'up'":
            if tello_connected:
                    drone.up(speed)
                    pygame.time.wait(duration)
                    drone.up(0)
        elif command_str == "b'down'":
            if tello_connected:
                    drone.down(speed)
                    pygame.time.wait(duration)
                    drone.down(0)
        else:
            command_str = 'Wrong comment'

        mqtt_command_img = font.render(command_str, False, whiteColor)
        window.blit(mqtt_command_img, (50, 100))
        event_log_update(command_str)

def pygame_update(message_lane):
    global message_list, window, message_img, background_img, battary
    global attention_duration, attention_value, control_mode, takeoff_flag
    global takeoff_time, land_time, fly_time
    font = pygame.font.Font("bgothl.ttf", 20)
    # font = pygame.font.Font("freesansbold.ttf", 20)
    window.blit(background_img, (0, 0))
    for i in list(range(message_max)):
        if (i < message_lane-1):
            message_img = font.render("# "+str(message_list[i]), False, blackColor)
            window.blit(message_img, (50, 350 + i * 30))
        elif (i == message_lane-1):
            message_img = font.render("# "+str(message_list[i]), False, blueColor)
            window.blit(message_img, (50, 350 + i * 30))
        else:
            message_img = font.render("", False, whiteColor)
            window.blit(message_img, (50, 270 + i * 30))
    draw_gauge_bar(54, 309, 0, 4.5*battary, 10, redColor)
    if takeoff_flag == True:
        if set_time > 60:
            draw_gauge_bar(54, 550, 0, 7.5 * 60, 20, blueColor)
        else:
            draw_gauge_bar(54, 550, 0, 8*set_time, 20, blueColor)
    set_time_str = '{:.1f}'.format(set_time)
    font = pygame.font.Font("bgothl.ttf", 30)
    if takeoff_flag == True:
        if game_mode == True:
            time_img = font.render("Remain time : "+set_time_str, False, blueColor)
            window.blit(time_img, (80, 500))
    if takeoff_flag == False:
        time_img = font.render("Total flight : "+str('%.1f'%fly_time)+" sec", False, blueColor)
        window.blit(time_img, (80, 500))
    font = pygame.font.Font("bgothl.ttf", 20)
    pygame.display.update()

def draw_gauge_bar(center_x, center_y, dir, length, width, color):
    global redColor
    if dir is 0:
        end_x = center_x + length
        end_y = center_y
    else :
        end_x = center_x
        end_y = center_y - length
    pygame.draw.line(window, color, (center_x, center_y), (end_x, end_y), width)

def event_log_update(message):
    global event_log, message_list
    message_list[event_log] = message
    pygame_update(event_log)
    if event_log >= message_max - 1:
        event_log = 0
    else:
        event_log = event_log + 1

def main():
    global window, background_img, font, control_mode, fpsClock
    global blackColor, blueColor, whiteColor, greenColor
    global speed, duration, rot_flag, battary, takeoff_flag, msg
    global takeoff_time, land_time, fly_time, set_time

    init_pygame()
    if tello_connected:
        init_tello()
    init_mqtt()

    quit = False
    while quit is False:
        if takeoff_flag == True:
            if game_mode == True:  
                set_time = set_time - 0.1
            if set_time <= 0:
                msg = "land"
                takeoff_flag = True
                land_time = pygame.time.get_ticks()
                fly_time = (land_time - takeoff_time) / 1000.0
                takeoff_flag = False
                background_img = pygame.image.load(bg_file_1)
                event_log_update(msg)
                if tello_connected:
                    drone.land()
            else:
                pygame_update(event_log)
        pygame.time.wait(100)
        # loop with pygame.event.get() is too much tight w/o some sleep
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quit = True
                #elif event.key == K_F1:
                #    control_mode = True
                #    background_img = pygame.image.load(bg_file_open)
                elif event.key == K_t:
                    msg = 'takeoff'
                    background_img = pygame.image.load(bg_file_2)
                    takeoff_time = pygame.time.get_ticks()
                    takeoff_flag = True
                    set_time = 30
                    #background_img = pygame.image.load(bg_file_1)
                    #event_log_update(msg)
                    if tello_connected:
                        drone.takeoff()
                    event_log_update(msg)
                elif event.key == K_l:
                    msg = 'land'
                    background_img = pygame.image.load(bg_file_1)
                    if takeoff_flag == True:
                        land_time = pygame.time.get_ticks()
                    fly_time = (land_time - takeoff_time) / 1000.0
                    if tello_connected:
                        drone.land()
                    takeoff_flag = False
                    event_log_update(msg)
                elif event.key == K_LEFT:
                    msg = 'left'
                    event_log_update(msg)
                    if tello_connected:
                        drone.left(speed)
                        pygame.time.wait(duration)
                        drone.left(0)
                    event_log_update(msg)
                elif event.key == K_RIGHT:
                    msg = 'right'
                    #event_log_update(msg)
                    if tello_connected:
                        drone.right(speed)
                        pygame.time.wait(duration)
                        drone.right(0)
                    event_log_update(msg)
                elif event.key == K_UP:
                    msg = 'forward'
                    #event_log_update(msg)
                    if tello_connected:
                        drone.forward(speed)
                        pygame.time.wait(duration)
                        drone.forward(0)
                    event_log_update(msg)
                elif event.key == K_DOWN:
                    msg = 'back'
                    #event_log_update(msg)
                    if tello_connected:
                        drone.backward(speed)
                        pygame.time.wait(duration)
                        drone.backward(0)
                    event_log_update(msg)
                elif event.key == K_HOME:
                    msg = 'ccw'
                    #event_log_update(msg)
                    if tello_connected:
                        drone.counter_clockwise(speed)
                        pygame.time.wait(duration)
                        drone.counter_clockwise(0)
                    event_log_update(msg)
                elif event.key == K_END:
                    msg = 'cw'
                    #event_log_update(msg)
                    if tello_connected:
                        drone.clockwise(speed)
                        pygame.time.wait(duration)
                        drone.clockwise(0)
                    event_log_update(msg)
                elif event.key == K_PAGEUP:
                    msg = 'up'
                    #event_log_update(msg)
                    if tello_connected:
                        drone.up(speed)
                        pygame.time.wait(duration)
                        drone.up(0)
                    event_log_update(msg)
                elif event.key == K_PAGEDOWN:
                    msg = 'down'
                    #event_log_update(msg)
                    if tello_connected:
                        drone.down(speed)
                        pygame.time.wait(duration)
                        drone.down(0)
                    event_log_update(msg)
                elif event.key == K_r:
                    if rot_flag:
                        msg = 'Rotation stop'
                        if tello_connected:
                            drone.clockwise(0)
                        rot_flag = False
                    else:
                        msg = 'Rotation start'
                        if tello_connected:
                            drone.clockwise(50)
                        rot_flag = True
                    event_log_update(msg)
                elif event.key == K_f:
                    msg = 'Flip forward'
                    #event_log_update(msg)
                    if tello_connected:
                        if battary > 50:
                            drone.flip_forward()
                        else:
                            # print('Low battary to flip < 50%')
                            event_log_update('Low battary to flip < 50%')
                    event_log_update(msg)
                else:
                    msg = 'Wrong Command'  
                    event_log_update(msg)
        pygame.display.update()
        # fpsClock.tick(25)
    if tello_connected:
        drone.quit()
    exit(1)

if __name__ == '__main__':
    main()

