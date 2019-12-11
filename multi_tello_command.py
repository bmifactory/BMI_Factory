 # -*- coding: utf-8 -*-
import sys
from tello_multi import *
import multiprocessing
import time
import os
import binascii

num_of_tello = 2
threshold = 20
battery = 0
Drone_SN = ["b'0TQDG2KEDBFP39'","b'0TQDG2KEDB94U4'"]

def create_execution_pools(num):
    pools = []
    for x in range(num):
        execution_pool = multiprocessing.Queue()
        pools.append(execution_pool)
    return pools

def drone_handler(tello, queue):
    while True:
        while queue.empty():
            pass
        command = queue.get()
        tello.send_command(command)

def all_queue_empty(execution_pools):
    for queue in execution_pools:
        if not queue.empty():
            return False
    return True

def all_got_response(manager):
    for tello_log in manager.get_log().values():
        if not tello_log[-1].got_response():
            return False
    return True

def save_log(manager):
    log = manager.get_log()

    if not os.path.exists('log'):
        try:
            os.makedirs('log')
        except Exception as e:
            pass

    out = open('log/' + start_time + '.txt', 'w')
    cnt = 1
    for stat_list in log.values():
        out.write('------\nDrone: %s\n' % cnt)
        cnt += 1
        for stat in stat_list:
            #stat.print_stats()
            str = stat.return_stats()
            out.write(str)
        out.write('\n')

def check_timeout(start_time, end_time, timeout):
    diff = end_time - start_time
    time.sleep(0.1)
    return diff > timeout

def delay(delay_time):
    print('[Delay_Seconds]Start Delay for %f second\n' % delay_time)
    time.sleep(delay_time)

def drone_ID(id, sn):
    global id_sn_dict
    id_sn_dict[id - 1] = sn

def send_command(id, action):
    global tello_list, id_list, execution_pools, sn_ip_dict, id_sn_dict, ip_fid_dict

    id_list = []
    if id == '*':
        for x in range(len(tello_list)):
            id_list.append(x)
    else:
        # index starbattery_checkt from 1
        id_list.append(int(id) - 1)

    # push command to pools
    for tello_id in id_list:
        tmp_sn = id_sn_dict[tello_id]
        reflec_ip = sn_ip_dict[tmp_sn]
        fid = ip_fid_dict[reflec_ip]
        execution_pools[fid].put(action)

    # wait till all commands are executed
    while not all_queue_empty(execution_pools):
        time.sleep(0.5)

    time.sleep(1)

    # wait till all responses are received
    while not all_got_response(manager):
        time.sleep(0.5)

def sync(timeout):
    print('[Sync_And_Waiting]Sync for %s seconds \n' % timeout)
    time.sleep(1)
    try:
        start = time.time()
        # wait till all commands are executed
        while not all_queue_empty(execution_pools):
            now = time.time()
            if check_timeout(start, now, timeout):
                raise RuntimeError

        print('[All_Commands_Send]All queue empty and all command send,continue\n')
        # wait till all responses are received
        while not all_got_response(manager):
            now = time.time()
            if check_timeout(start, now, timeout):
                raise RuntimeError
        print('[All_Responses_Get]All response got, continue\n')
    except RuntimeError:
        print('[Quit_Sync]Fail Sync:Timeout exceeded, continue...\n')

def battery_check():
    global manager, tello_list, execution_pools, sn_ip_dict, id_sn_dict, ip_fid_dict, start_time, battery

    for queue in execution_pools:
        queue.put('battery?')

    # wait till all commands are executed
    while not all_queue_empty(execution_pools):
        time.sleep(0.5)

    time.sleep(1)

    # wait till all responses are received
    while not all_got_response(manager):
        time.sleep(0.5)

    for tello_log in manager.get_log().values():
        battery = int(tello_log[-1].response)
        print('[Battery_Show]show drone battery: %d  ip:%s\n' % (battery, tello_log[-1].drone_ip))
        if battery < threshold:
            print('[Battery_Low]IP:%s  Battery < Threshold. Exiting...\n' % tello_log[-1].drone_ip)
            #save_log(manager)
            exit(0)
    print('[Battery_Enough]Pass battery check\n')
    return battery

def init_tello_manager():
    global manager, tello_list, execution_pools, sn_ip_dict, id_sn_dict, ip_fid_dict, start_time, battery

    manager = Tello_Manager()
    start_time = str(time.strftime("%a-%d-%b-%Y_%H-%M-%S-%Z", time.localtime(time.time())))
    sn_ip_dict = {}
    id_sn_dict = {}
    ip_fid_dict = {}

    manager.find_avaliable_tello(num_of_tello)
    tello_list = manager.get_tello_list()
    execution_pools = create_execution_pools(num_of_tello)

    for x in range(len(tello_list)):
        t1 = Thread(target=drone_handler, args=(tello_list[x], execution_pools[x]))
        ip_fid_dict[tello_list[x].tello_ip] = x
        # str_cmd_index_dict_init_flag [x] = None
        t1.daemon = True
        t1.start()

    battery = battery_check()

    #correct_ip
    for queue in execution_pools:
        queue.put('sn?')

    while not all_queue_empty(execution_pools):
        time.sleep(0.5)

    time.sleep(1)

    while not all_got_response(manager):
        time.sleep(0.5)

    for tello_log in manager.get_log().values():
        sn = str(tello_log[-1].response)
        tello_ip = str(tello_log[-1].drone_ip)
        sn_ip_dict[sn] = tello_ip

    for id in range(num_of_tello):
        drone_ID(id+1,Drone_SN[id])

#def main():

#    init_tello_manager()

#    send_command("*", "mon")

#    send_command("*",'takeoff')

#    send_command("*",'ccw 45')

#    send_command("*",'land')

#if __name__ == '__main__':
#    main()
