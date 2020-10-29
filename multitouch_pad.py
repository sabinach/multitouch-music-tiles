#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Import the relevant files
from sys import exit
import cv2
import numpy as np
import simpleaudio as sa

# Initialize the camera
cam_port         = 0   # I've set my camera port to port zero!
cam              = cv2.VideoCapture(cam_port)   # I've created my camera object!

# Sound samples from:
# http://www.philharmonia.co.uk/explore/sound_samples/bass_clarinet?p=2

# Percussion (Piano) 
piano_c1 = sa.WaveObject.from_wave_file("sounds/piano/c1.wav")
piano_e1 = sa.WaveObject.from_wave_file("sounds/piano/e1.wav")
piano_g1 = sa.WaveObject.from_wave_file("sounds/piano/g1.wav")
piano_c2 = sa.WaveObject.from_wave_file("sounds/piano/c2.wav")

# Percussion (Battery)
perc_bass_drum = sa.WaveObject.from_wave_file("sounds/percussion/bass-drum__025_forte_bass-drum-mallet.wav")
perc_cymbal = sa.WaveObject.from_wave_file("sounds/percussion/chinese-cymbal__05_forte_damped.wav")
perc_tambourine = sa.WaveObject.from_wave_file("sounds/percussion/tambourine__025_forte_hand.wav")
perc_woodblock = sa.WaveObject.from_wave_file("sounds/percussion/woodblock__025_mezzo-forte_struck-singly.wav")

# Wind (trumpet)
trumpet_a3 = sa.WaveObject.from_wave_file("sounds/trumpet/trumpet_A3_025_forte_normal.wav")
trumpet_a4 = sa.WaveObject.from_wave_file("sounds/trumpet/trumpet_A4_025_forte_normal.wav")
trumpet_a5 = sa.WaveObject.from_wave_file("sounds/trumpet/trumpet_A5_025_forte_normal.wav")
trumpet_as3 = sa.WaveObject.from_wave_file("sounds/trumpet/trumpet_As3_025_forte_normal.wav")

# Wind (bass clarinet)
bass_clarinet_a2 = sa.WaveObject.from_wave_file("sounds/bass_clarinet/bass-clarinet_A2_025_forte_normal.wav")
bass_clarinet_a3 = sa.WaveObject.from_wave_file("sounds/bass_clarinet/bass-clarinet_A3_025_forte_normal.wav")
bass_clarinet_a4 = sa.WaveObject.from_wave_file("sounds/bass_clarinet/bass-clarinet_A4_025_forte_normal.wav")
bass_clarinet_a5 = sa.WaveObject.from_wave_file("sounds/bass_clarinet/bass-clarinet_A5_025_fortissimo_normal.wav")

# Piano sounds (more)
#piano_a1 = sa.WaveObject.from_wave_file("sounds/piano/a1.wav")
#piano_b1 = sa.WaveObject.from_wave_file("sounds/piano/b1.wav")
#piano_d1 = sa.WaveObject.from_wave_file("sounds/piano/d1.wav")
#piano_f1 = sa.WaveObject.from_wave_file("sounds/piano/f1.wav")


def empty_callback(x):
    '''
    Empty function for callback when slider positions change. Need input x, this is the value 
    the slider has changed to. You don't need to do anything in this function.
    '''
    pass

def scan():

    # default calibration for detecting finger pads
    #default_calibration = {'h':[90,96],'s':[0,114],'v':[0,255]}    
    default_calibration = {'h':[71,101],'s':[113,255],'v':[0,255],'contours':[3175,12344]} #[3617,12344]

    # create window
    cv2.namedWindow('tracker_window',0)        
    
    # H: 0-179
    cv2.createTrackbar('H Upper',"tracker_window",default_calibration['h'][1],179, empty_callback)
    cv2.createTrackbar('H Lower',"tracker_window",default_calibration['h'][0],179, empty_callback)

    # S: 0-255
    cv2.createTrackbar('S Upper',"tracker_window",default_calibration['s'][1],255, empty_callback)
    cv2.createTrackbar('S Lower',"tracker_window",default_calibration['s'][0],255, empty_callback)

    # V: 0-255
    cv2.createTrackbar('V Upper',"tracker_window",default_calibration['v'][1],255, empty_callback)
    cv2.createTrackbar('V Lower',"tracker_window",default_calibration['v'][0],255, empty_callback)

    # Contours
    cv2.createTrackbar('Max Area',"tracker_window",default_calibration['contours'][1],30000, empty_callback)
    cv2.createTrackbar('Min Area',"tracker_window",default_calibration['contours'][0],30000, empty_callback)

    # Check which quadrant user has tapped
    tap_top_left = False
    tap_top_right = False
    tap_bottom_left = False
    tap_bottom_right = False

    # counter for # of iterations where user is holding down one finger at swipe area
    hold_counter = 0
    initial_side_set = False
    initial_swipe_side = None

    # starting sound style
    style = 'percussion'
    toggle = 0          # toggle between sound types: Percussion: Piano <-> Drums, Wind: Trumpet <-> Bass Clarinet
    toggle_counter = 0  # make sure user is holding down two fingers long enough to toggle

    while True:

        # Captures a frame of video from the camera object
        _,frame = cam.read()

        # generates an hsv version of frame and stores it in the hsv image variable
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 

        # hue upper lower
        hu = cv2.getTrackbarPos('H Upper','tracker_window')
        hl = cv2.getTrackbarPos('H Lower','tracker_window')
        # saturation upper lower
        su = cv2.getTrackbarPos('S Upper','tracker_window')
        sl = cv2.getTrackbarPos('S Lower','tracker_window')
        # value upper lower
        vu = cv2.getTrackbarPos('V Upper','tracker_window')
        vl = cv2.getTrackbarPos('S Lower','tracker_window')

        # get hsv values from trackbar
        lower_hsv = np.array([hl,sl,vl])
        upper_hsv = np.array([hu,su,vu])
        
        # mask image
        mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
        res = cv2.bitwise_and(frame,frame, mask= mask)

        # get image contours
        ret,thresh = cv2.threshold(mask,127,255,0)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # value upper lower
        max_area= cv2.getTrackbarPos('Max Area','tracker_window')
        min_area = cv2.getTrackbarPos('Min Area','tracker_window')

        # overlay transparency 
        alpha = 0.35            # transparency for tiles
        offset_alpha = 0.7      # transparency for offset/title area

        # dividing lines
        offset = 100                    # leave swipe area on the top
        mid_x = 325                     # mid intersection area
        mid_y = 240 + int(offset/2)     # account for offset area
        max_x = 650                     # max boundary for x
        max_y = 475                     # max boundary for y
        cv2.line(frame,(0,offset),(max_x,offset),(0,0,0),5)         # offset divider
        cv2.line(frame,(mid_x,offset),(mid_x,max_y),(0,0,0),5)      # vertical divider
        cv2.line(frame,(0,mid_y),(max_x,mid_y),(0,0,0),5)           # horizontal divider
        
        # percussion color overlay - teal
        if style=='percussion':
            # create title bar percussion style
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (max_x, offset), (255, 255, 0), -1)
            cv2.addWeighted(overlay, offset_alpha, frame, 1 - offset_alpha, 0, frame)
            cv2.putText(frame, "<- Swipe Left for Wind", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 191), 2)
            # percussion: piano sounds
            if toggle==0:
                # text for percussion sound type (piano)
                cv2.putText(frame, "Percussion (Piano)", (mid_x-150, int(offset/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                # text for piano key 
                cv2.putText(frame, "c1", (mid_x - 50, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3) # c1
                cv2.putText(frame, "e1", (mid_x + 15, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3) # e1
                cv2.putText(frame, "g1", (mid_x - 50, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3) # g1
                cv2.putText(frame, "c2", (mid_x + 15, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3) # c2
                # color for piano tile
                cv2.rectangle(frame,(0,offset),(mid_x,mid_y),(0,0,255),3) 
                cv2.rectangle(frame,(mid_x,offset),(max_x,mid_y),(255,0,0),3) 
                cv2.rectangle(frame,(0,mid_y),(mid_x,max_y),(0,255,0),3) 
                cv2.rectangle(frame,(mid_x,mid_y),(max_x,max_y),(0,255,255),3) 
            # perussion: drum sounds
            if toggle==1:
                # text for percussion sound type (drums)
                cv2.putText(frame, "Percussion (Drums)", (mid_x-150, int(offset/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                # text for drum key
                cv2.putText(frame, "BD", (mid_x - 50, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3) # bass drum
                cv2.putText(frame, "CYM", (mid_x + 15, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3) # cymbal
                cv2.putText(frame, "TAM", (mid_x - 50, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3) # tambourine
                cv2.putText(frame, "WB", (mid_x + 15, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3) # woodblock
                # color for drum tile
                cv2.rectangle(frame,(0,offset),(mid_x,mid_y),(0,255,255),3) 
                cv2.rectangle(frame,(mid_x,offset),(max_x,mid_y),(0,255,0),3) 
                cv2.rectangle(frame,(0,mid_y),(mid_x,max_y),(255,0,0),3) 
                cv2.rectangle(frame,(mid_x,mid_y),(max_x,max_y),(0,0,255),3) 

        # wind color overlay - purple
        elif style=='wind':
            # create title bar for wind style
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (max_x, offset), (255, 0, 191), -1)
            cv2.addWeighted(overlay, offset_alpha, frame, 1 - offset_alpha, 0, frame)
            cv2.putText(frame, "Swipe Right for Percussion ->", (mid_x+50, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            # wind: trumpet sounds
            if toggle==0: 
                # text for wind sound type (trumpet)
                cv2.putText(frame, "Wind (Trumpet)", (mid_x-100, int(offset/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3) # current style
                # text for trumpet key 
                cv2.putText(frame, "a3", (mid_x - 50, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3) # a3
                cv2.putText(frame, "a4", (mid_x + 15, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3) # a4
                cv2.putText(frame, "a5", (mid_x - 50, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3) # a5
                cv2.putText(frame, "as3", (mid_x + 15, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3) # as3
                # color for trumpet tile
                cv2.rectangle(frame,(0,offset),(mid_x,mid_y),(0,0,255),3) 
                cv2.rectangle(frame,(mid_x,offset),(max_x,mid_y),(255,0,0),3) 
                cv2.rectangle(frame,(0,mid_y),(mid_x,max_y),(0,255,0),3) 
                cv2.rectangle(frame,(mid_x,mid_y),(max_x,max_y),(0,255,255),3) 
            # wind: bass clarinet sounds
            if toggle==1:
                # text for wind sound type (bass clarinet)
                cv2.putText(frame, "Wind (Bass Clarinet)", (mid_x-150, int(offset/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3) # current style
                # text for bass clarinet key
                cv2.putText(frame, "a2", (mid_x - 50, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3) # a2
                cv2.putText(frame, "a3", (mid_x + 15, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3) # a3
                cv2.putText(frame, "a4", (mid_x - 50, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3) # a4
                cv2.putText(frame, "a5", (mid_x + 15, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3) # a5
                # color for bass clarinet tile
                cv2.rectangle(frame,(0,offset),(mid_x,mid_y),(0,255,255),3) 
                cv2.rectangle(frame,(mid_x,offset),(max_x,mid_y),(0,255,0),3) 
                cv2.rectangle(frame,(0,mid_y),(mid_x,max_y),(255,0,0),3) 
                cv2.rectangle(frame,(mid_x,mid_y),(max_x,max_y),(0,0,255),3) 

        # filtered_contours = []

        # counter for keeping track of how many fingers user has on the touch pad during this iteration
        finger_counter = 0

        # filter out contours based on area
        for contour in contours:   

            # get contour area     
            area = cv2.contourArea(contour) 

            # filter contour based on min/max area        
            if area > min_area and area < max_area:

                # update list of correct sized contours                 
                # filtered_contours.append(contour)

                # draw a circle around the contour (b,g,r)
                ellipse = cv2.fitEllipse(contour)
                cv2.ellipse(frame,ellipse,(0,0,255),2)

                # draw the center of the contours 
                M = cv2.moments(contour)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cX, cY), 7, (255, 0, 0), -1)

                # show x,y coordinates of center 
                center_coord_text = "x:{}, y:{}".format(cX,cY)
                cv2.putText(frame, center_coord_text, (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # TAP TILES AND DISPLAY COLOR OVERLAY
                if toggle==0:
                    # top left -> play c1
                    if cX<=mid_x and cY<=mid_y and cY>=offset:
                        # user pressed top left tile
                        tap_top_left = True
                        # red tile overlay
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (0, offset), (mid_x, mid_y), (0, 0, 255), -1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                    # top right -> play e1
                    if cX>mid_x and cY<=mid_y and cY>=offset:
                        # user pressed top right tile
                        tap_top_right = True
                        # blue tile overlay
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (mid_x, offset), (max_x, mid_y), (255, 0, 0), -1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                    # bottom left -> play g1
                    if cX<=mid_x and cY>mid_y:
                        # user pressed bottom left tile
                        tap_bottom_left = True
                        # green tile overlay
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (0, mid_y), (mid_x, max_y), (0, 255, 0), -1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                    # bottom right -> play c2
                    if cX>mid_x and cY>mid_y:
                        # user pressed bottom right tile
                        tap_bottom_right = True
                        # yellow tile overlay
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (mid_x, mid_y), (max_x, max_y), (0, 255, 255), -1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                if toggle==1:
                    # top left -> play c1
                    if cX<=mid_x and cY<=mid_y and cY>=offset:
                        # user pressed top left tile
                        tap_top_left = True
                        # red tile overlay
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (0, offset), (mid_x, mid_y), (0, 255, 255), -1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                    # top right -> play e1
                    if cX>mid_x and cY<=mid_y and cY>=offset:
                        # user pressed top right tile
                        tap_top_right = True
                        # blue tile overlay
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (mid_x, offset), (max_x, mid_y), (0, 255, 0), -1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                    # bottom left -> play g1
                    if cX<=mid_x and cY>mid_y:
                        # user pressed bottom left tile
                        tap_bottom_left = True
                        # green tile overlay
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (0, mid_y), (mid_x, max_y), (255, 0, 0), -1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                    # bottom right -> play c2
                    if cX>mid_x and cY>mid_y:
                        # user pressed bottom right tile
                        tap_bottom_right = True
                        # yellow tile overlay
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (mid_x, mid_y), (max_x, max_y), (0, 0, 255), -1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                
                # if user's finger is in the swipe area
                if cY<offset:
                    finger_counter += 1
        
        # if user has one finger on the pad, keep track of the starting location       
        if finger_counter == 1 and hold_counter <= 10:
            # make sure that first the first 5 iterations, the user is on the same side (ie. user is not continuously switching sides)
            if initial_side_set:
                if (cX <= mid_x and cY <= offset and initial_swipe_side=='left') or (cX > mid_x and cY <= offset and initial_swipe_side=='right'):
                    hold_counter += 1
            # set the initial side the user is swiping from
            elif not initial_side_set or initial_set_set is None:
                if cX <= mid_x and cY <= offset:
                    initial_swipe_side = 'left'
                    print('INITIAL LEFT')
                elif cX > mid_x and cY <= offset :
                    initial_swipe_side = 'right'
                    print('INITIAL RIGHT')  
                initial_side_set = True
                hold_counter += 1

        # if user has more than one finger on the pad at a time      
        elif finger_counter > 1:
            # if user has exactly 2 fingers on pad, toggle between sounds
            if finger_counter == 2:
                toggle_counter += 1
                if toggle_counter == 10:
                    if toggle==1: 
                        toggle = 0
                        toggle_counter = 0
                        print('switch to sound type 0')
                    elif toggle==0: 
                        toggle = 1
                        toggle_counter = 0
                        print('switch to sound type 1')
                # reset one finger counter
                initial_side_set = False
                initial_swipe_side = None
                hold_counter = 0
            # else, reset all counters
            else:
                print('RESET')
                initial_side_set = False
                initial_swipe_side = None
                hold_counter = 0
                toggle_counter = 0

        # if user holds their one finger position long enough, then start considering the swipe
        if hold_counter > 10:
            # user swiped from left to right
            if cX >= mid_x and cY <= offset and initial_swipe_side == 'left':
                print('left -> right')
                hold_counter = 0
                initial_swipe_side = None
                initial_side_set = False
                style = 'percussion'
            # user swiped from right to left
            elif cX <= mid_x and cY <= offset and initial_swipe_side == 'right':
                print('right -> left')
                hold_counter = 0
                initial_swipe_side = None
                initial_side_set = False
                style = 'wind'

        # DEBUGGING STATEMENTS
        print('toggle_counter:{}'.format(toggle_counter))
        print('toggle:{}'.format(toggle))
        print(hold_counter)
            
        # draw filtered contours
        #cv2.drawContours(frame, filtered_contours, -1, (0,255,0), 3)

        # frame, mask, res
        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)
        cv2.imshow("tracker_window", res)

        # play sound if user pressed respective tile locations
        if style=='percussion':
            # piano
            if toggle==0:
                if tap_top_left:
                    piano_c1.play()
                if tap_top_right:
                    piano_e1.play()
                if tap_bottom_left:
                    piano_g1.play()
                if tap_bottom_right:
                    piano_c2.play()
            # drums
            if toggle==1:
                if tap_top_left:
                    perc_bass_drum.play()
                if tap_top_right:
                    perc_cymbal.play()
                if tap_bottom_left:
                    perc_tambourine.play()
                if tap_bottom_right:
                    perc_woodblock.play()

        elif style=='wind':
            # trumpet
            if toggle==0:
                if tap_top_left:
                    trumpet_a3.play()
                if tap_top_right:
                    trumpet_a4.play()
                if tap_bottom_left:
                    trumpet_a5.play()
                if tap_bottom_right:
                    trumpet_as3.play()
            # bass_clarinet
            if toggle==1:
                if tap_top_left:
                    bass_clarinet_a2.play()
                if tap_top_right:
                    bass_clarinet_a3.play()
                if tap_bottom_left:
                    bass_clarinet_a4.play()
                if tap_bottom_right:
                    bass_clarinet_a5.play()

        # reset tap (user let's go)
        tap_top_left = False
        tap_top_right = False
        tap_bottom_left = False
        tap_bottom_right = False

        # Sets the amount of time to display a frame in milliseconds
        key = cv2.waitKey(10)

        # quit on escape.
        if key == 27:
            break

    cam.release()
    cv2.destroyAllWindows()

scan()

