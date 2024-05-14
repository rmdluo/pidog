#!/usr/bin/env python3
from pidog import Pidog
from time import sleep
from vilib import Vilib
from preset_actions import bark
import math

my_dog = Pidog()
sleep(0.1)

def head_nod(step):
    y = 0
    r = 0
    p = 30
    angs = []
    for i in range(20):
        r = round(10*math.sin(i*0.314), 2)
        p = round(20*math.sin(i*0.314) + 10, 2)
        angs.append([y, r, p])

    my_dog.head_move(angs*step, pitch_comp=-40, immediately=False, speed=80)

def face_track():
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=True, web=True)
    Vilib.human_detect_switch(True)
    sleep(0.2)
    print('start')
    yaw = 0
    roll = 0
    pitch = 0
    flag = False
    direction = 0

    # my_dog.do_action('sit', speed=50)
    my_dog.do_action('stand', speed=50)
    my_dog.head_move([[yaw, 0, pitch]], pitch_comp=0, immediately=True, speed=80)
    my_dog.wait_all_done()
    sleep(0.5)
    # Cleanup sound detection by servos moving
    if my_dog.ears.isdetected():    
        direction = my_dog.ears.read()

    while True:
        if flag == False:
            my_dog.rgb_strip.set_mode('breath', 'pink', bps=1)
        # If heard somthing, turn to face it
        if my_dog.ears.isdetected():
            flag = False
            read_direction = my_dog.ears.read()
            for direction in range(read_direction - 20, read_direction + 20 + 1, 20):
                if direction > 0 and direction < 160:
                    yaw = -direction
                    if yaw < -80:
                        yaw = -80
                elif direction > 200 and direction < 360:
                    yaw = 360 - direction
                    if yaw > 80:
                        yaw = 80
                my_dog.head_move([[yaw, 0, 0]], pitch_comp=0, immediately=True, speed=80)
                my_dog.wait_head_done()
                sleep(0.05)

                ex = Vilib.detect_obj_parameter['human_x'] - 320
                ey = Vilib.detect_obj_parameter['human_y'] - 240
                people = Vilib.detect_obj_parameter['human_n']

                if people == 0:
                    pitch_updates = [i for i in range(80, -40, -10)]
                    # move head from up to down, looking for person
                    for new_pitch in pitch_updates:
                        my_dog.head_move([[yaw, 0, new_pitch]], pitch_comp=0, immediately=False, speed=50)
                        my_dog.wait_head_done()

                        ex = Vilib.detect_obj_parameter['human_x'] - 320
                        ey = Vilib.detect_obj_parameter['human_y'] - 240
                        people = Vilib.detect_obj_parameter['human_n']

                        if people > 0:
                            pitch = new_pitch
                            break
        else:
            ex = Vilib.detect_obj_parameter['human_x'] - 320
            ey = Vilib.detect_obj_parameter['human_y'] - 240
            people = Vilib.detect_obj_parameter['human_n']

        # If see someone, bark at him/her
        if people > 0 and flag == False:
            flag = True
            my_dog.do_action('wag_tail', step_count=2, speed=100)

            if ex > 15 and yaw > -80:
                yaw -= 0.5 * int(ex/30.0+0.5)

            elif ex < -15 and yaw < 80:
                yaw += 0.5 * int(-ex/30.0+0.5)

            if ey > 25:
                pitch -= 1*int(ey/50+0.5)
                if pitch < -30:
                    pitch = -30
            elif ey < -25:
                pitch += 1*int(-ey/50+0.5)
                if pitch > 30:
                    pitch = 30

            yaw = int(yaw)
            pitch = int(pitch)

            bark(my_dog, [yaw, 0, pitch], pitch_comp=0, volume=80)
            my_dog.head_move([[yaw, 0, pitch]], pitch_comp=0, immediately=False, speed=50)
            my_dog.wait_all_done()

            if my_dog.ears.isdetected():
                direction = my_dog.ears.read()

            # input()

            break   

        if ex > 15 and yaw > -80:
            yaw -= 0.5 * int(ex/30.0+0.5)

        elif ex < -15 and yaw < 80:
            yaw += 0.5 * int(-ex/30.0+0.5)

        if ey > 25:
            pitch -= 1*int(ey/50+0.5)
            if pitch < -30:
                pitch = -30
        elif ey < -25:
            pitch += 1*int(-ey/50+0.5)
            if pitch > 30:
                pitch = 30

        print('direction: %s |number: %s | ex, ey: %s, %s | yrp: %s, %s, %s '
              % (direction, people, ex, ey, round(yaw, 2), round(roll, 2), round(pitch, 2)),
              end='\r',
              flush=True,
        )
        my_dog.head_move([[yaw, 0, pitch]], pitch_comp=0, immediately=True, speed=50)
        my_dog.wait_head_done()
        if my_dog.ears.isdetected():
            direction = my_dog.ears.read()
        sleep(0.05)

    distance = my_dog.read_distance()
    distance = round(distance,2)
    print(f"Distance: {distance} cm")
    print(f"Distance horizontal: {distance * math.cos(math.radians(pitch))} cm")
    print(f"Pitch: {pitch}")
    print(f"Yaw: {yaw}")

    if(yaw < 0):
        for i in range(-yaw // 12):
            my_dog.do_action('turn_right', speed=80)
            my_dog.do_action('backward', speed=80)
    elif(yaw > 0):
        for i in range(yaw // 12):
            my_dog.do_action('turn_left', speed=80)
            my_dog.do_action('backward', speed=80)
        # my_dog.do_action('turn_left', step_count=yaw // 10, speed=80)

    my_dog.head_move([[0, 0, pitch]], pitch_comp=0, immediately=True, speed=50)
    
    my_dog.wait_all_done()

    # ex = Vilib.detect_obj_parameter['human_x'] - 320
    # ey = Vilib.detect_obj_parameter['human_y'] - 240
    # people = Vilib.detect_obj_parameter['human_n']

    horizontal_dist = int(distance * math.cos(math.radians(pitch)))
    for i in range(horizontal_dist // 12):
        if my_dog.read_distance() < 15 and my_dog.read_distance() > 1:
            break
        my_dog.do_action('trot', speed=80)
        my_dog.wait_all_done()

    # my_dog.wait_all_done()

    my_dog.do_action('sit', speed=80)
    my_dog.head_move([[0, 0, 0]], pitch_comp=-40, immediately=True, speed=50)

    my_dog.wait_all_done()

    while(True):
        # relax
        if my_dog.dual_touch.read() != 'N':
            if len(my_dog.head_action_buffer) < 2:
                head_nod(1)
                my_dog.do_action('wag_tail', step_count=10, speed=80)
                my_dog.rgb_strip.set_mode('listen', color="#8A2BE2", bps=0.35, brightness=0.8)

    input()

if __name__ == "__main__":
    try:
        face_track()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()
        my_dog.close()