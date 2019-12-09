"""
tellop SDK sample
- you must install mplayer to replay the video
"""
import time, sys, os
import pygame
from pygame import *
from subprocess import Popen, PIPE
import paho.mqtt.client as mqtt
from tello import Tello

#For MQTT
MQTT_name = "localhost"
#MQTT_name = "192.168.0.2"
Topic_name = "tello1"

# For tello
tello_connected = True
control_mode = True
video_stream = True
prev_flight_data = None
video_player = None
battery = 0
altitude = 0
speed = 100
duration = 500
dir_flag = 0
updown_flag = 0
rot_flag = False

# Set pygame parameter
fullscreen = False
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (1360,0)
bg_file_1 = "images/Tello_bg_1.jpg"
bg_file_2 = "images/Tello_bg_2.jpg"
txt_font = "font/bgothl.ttf"
message_max = 7
message_list = list(range(message_max))
event_log = 0

def init_tello():
    global drone, speed, battery
    #global throttle, yaw, pitch, roll
    drone = Tello()
    drone.send_command('command')
    drone.send_command('battery?')
    battery = int(str(drone.response).split("'")[1].split("\\")[0])
    #print(battery)
    pygame_update(event_log)
    #drone.connect()
    #drone.set_video_encoder_rate(10)
    #drone.subscribe(drone.EVENT_FLIGHT_DATA, tello_handler)
    #if video_stream:
    #    drone.start_video()
    #    pygame.time.wait(2)
    #    drone.subscribe(drone.EVENT_VIDEO_FRAME, tello_handler)

def init_pygame():
    global window, background_img, font, fpsClock
    global blackColor, blueColor, whiteColor, greenColor, redColor
    pygame.init()
    font = pygame.font.Font(txt_font, 20)
    blackColor = pygame.Color(0, 0, 0)
    redColor = pygame.Color(255, 0, 0)
    blueColor = pygame.Color(0, 0, 255)
    whiteColor = pygame.Color(255, 255, 255)
    greenColor = pygame.Color(0, 255, 0)
    window = pygame.display.set_mode((560, 575), pygame.RESIZABLE)
    #window = pygame.display.set_mode((240, 575), pygame.RESIZABLE)
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


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(Topic_name)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global event_log, dir_flag, updown_flag, background_img, battery
    if msg.topic == Topic_name:
        command_str = str(msg.payload)
        command_str = command_str.split("'")[1]
        print(command_str)
        if command_str == "takeoff":
            background_img = pygame.image.load(bg_file_2)
        elif command_str == "land":
            background_img = pygame.image.load(bg_file_1)
        mqtt_command_img = font.render(command_str, False, whiteColor)
        window.blit(mqtt_command_img, (50, 100))
        event_log_update(command_str)
        if tello_connected:
            if command_str == "takeoff":
                #pygame.time.wait(2000)
                drone.send_command("takeoff")
                drone.send_command("battery?")
                battery = int(str(drone.response).split("'")[1].split("\\")[0])
            elif command_str == "level1":
                if dir_flag == 0:
                    drone.send_command("cw 90")
                    dir_flag = 1
                elif dir_flag == 1:
                    drone.send_command("ccw 90")
                    dir_flag = 0
            elif command_str == "level2":
                drone.send_command("battery?")
                battery = int(str(drone.response).split("'")[1].split("\\")[0])
                if battery > 50:
                    drone.send_command("flip f")
                    drone.send_command("back 30")
                else:
                    if updown_flag == 0:
                        drone.send_command("up 30")
                        updown_flag = 1
                    elif updown_flag == 1:
                        drone.send_command("down 30")
                        updown_flag = 0
            elif command_str == "land":
                drone.send_command("land")
            elif command_str == "left":
                drone.send_command("left 30")
            elif command_str == "right":
                drone.send_command("right 30")
            elif command_str == "forward":
                drone.send_command("forward 30")
            elif command_str == "back":
                drone.send_command("back 30")
            elif command_str == "cw":
                drone.send_command("cw 45")
            elif command_str == "ccw":
                drone.send_command("ccw 45")
            elif command_str == "up":
                drone.send_command("up 30")
            elif command_str == "down":
                drone.send_command("down 30")
            elif command_str == "Neurosky connected":
                drone.send_command('battery?')
                battery = int(str(drone.response).split("'")[1].split("\\")[0])
            else:
                event_log_update('Wrong comment')

def pygame_update(message_lane):
    global message_list, window, message_img, background_img, battery
    global attention_duration, attention_value, control_mode, takeoff_flag
    font = pygame.font.Font(txt_font, 20)
    window.blit(background_img, (0, 0))
    for i in list(range(message_max)):
        if (i < message_lane):
            message_img = font.render("# "+str(message_list[i]), False, blackColor)
            window.blit(message_img, (50, 350 + i * 30))
        elif (i == message_lane):
            message_img = font.render("# "+str(message_list[i]), False, blueColor)
            window.blit(message_img, (50, 350 + i * 30))
        else:
            message_img = font.render("", False, whiteColor)
            window.blit(message_img, (50, 270 + i * 30))
    draw_gauge_bar(49, 309, 0, 4*battery, 10)
    #draw_gauge_bar(30, 309, 0, 2*battery, 18)
    battery_str = '{:.1f}'.format(battery)
    font = pygame.font.Font(txt_font, 30)
    battery_img = font.render(battery_str+"%", False, blueColor)
    window.blit(battery_img, (30, 260))
    pygame.display.update()

def draw_gauge_bar(center_x, center_y, dir, length, width):
    global redColor
    if dir is 0:
        end_x = center_x + length
        end_y = center_y
    else :
        end_x = center_x
        end_y = center_y - length
    pygame.draw.line(window, redColor, (center_x, center_y), (end_x, end_y), width)

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
    global speed, duration, rot_flag, battery, takeoff_flag, msg

    init_pygame()
    if tello_connected:
        init_tello()
    init_mqtt()

    quit = False
    while quit is False:
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
                    event_log_update(msg)
                    if control_mode:
                        if tello_connected:
                            drone.send_command("takeoff")
                            drone.send_command("battery?")
                            battery = int(str(drone.response).split("'")[1].split("\\")[0])
                        #background_img = pygame.image.load(bg_file_2)
                elif event.key == K_l:
                    msg = 'land'
                    if tello_connected:
                        drone.send_command("land")
                        drone.send_command("battery?")
                        battery = int(str(drone.response).split("'")[1].split("\\")[0])
                    background_img = pygame.image.load(bg_file_1)
                    takeoff_flag = False
                    event_log_update(msg)
                elif event.key == K_LEFT:
                    msg = 'left'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("left 30")
                elif event.key == K_RIGHT:
                    msg = 'right'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("right 30")
                elif event.key == K_UP:
                    msg = 'forward'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("forward 30")
                elif event.key == K_DOWN:
                    msg = 'back'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("back 30")
                elif event.key == K_HOME:
                    msg = 'ccw'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("ccw 45")
                elif event.key == K_END:
                    msg = 'cw'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("cw 45")
                elif event.key == K_PAGEUP:
                    msg = 'up'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("up 30")
                elif event.key == K_PAGEDOWN:
                    msg = 'down'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("down 30")
                elif event.key == K_f:
                    msg = 'Flip forward'
                    event_log_update(msg)
                    if tello_connected:
                        drone.send_command("battery?")
                        battery = int(str(drone.response).split("'")[1].split("\\")[0])
                        if battery > 50:
                            drone.send_command("flip f")
                            drone.send_command("back 30")
                        else:
                            event_log_update('Low battery to flip < 50%')
        pygame.display.update()
        # fpsClock.tick(25)
    if tello_connected:
        pygame.time.wait(duration)
    exit(1)

if __name__ == '__main__':
    main()

