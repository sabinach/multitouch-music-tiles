#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Import the relevant files
from sys import exit
import cv2
import numpy as np

# Initialize the camera
cam_port         = 0   # I've set my camera port to port zero!
cam              = cv2.VideoCapture(cam_port)   # I've created my camera object!

def empty_callback(x):
    '''
    Empty function for callback when slider positions change. Need input x, this is the value 
    the slider has changed to. You don't need to do anything in this function.
    '''
    pass

def scan():

    # default calibration for detecting finger pads
    #default_calibration = {'h':[90,96],'s':[0,114],'v':[0,255]}    
    default_calibration = {'h':[85,96],'s':[0,92],'v':[0,255],'contours':[3617,12344]} #[2086,12344]

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

        # filtered_contours = []
        
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
                center_coord = "x:{}, y:{}".format(cX,cY)
                cv2.putText(frame, center_coord, (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # draw filtered contours
        #cv2.drawContours(frame, filtered_contours, -1, (0,255,0), 3)

        # frame, mask, res
        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)
        cv2.imshow("tracker_window", res)

        # Sets the amount of time to display a frame in milliseconds
        key = cv2.waitKey(10)

        # quit on escape.
        if key == 27:
            break

    cam.release()
    cv2.destroyAllWindows()

scan()

