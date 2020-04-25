import cv2
import argparse
import glob
import numpy as np
import os
import time
import sys
import csv
import pandas

basedir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(basedir, os.path.pardir)))
from tracker import re3_tracker

from re3_utils.util import drawing
from re3_utils.util import bb_util
from re3_utils.util import im_util

from constants import OUTPUT_WIDTH
from constants import OUTPUT_HEIGHT
from constants import PADDING

np.set_printoptions(precision=7)
np.set_printoptions(suppress=True)

drawnBox = np.zeros(4)
boxToDraw = np.zeros(4)
mousedown = False
mouseupdown = False
initialize = False

list_1 = []
coords_x=[]
coords_y=[]
count=0

font = cv2.FONT_HERSHEY_SIMPLEX 
fontScale = 1 
thickness = 1

def on_mouse(event, x, y, flags, params):
    global mousedown, mouseupdown, drawnBox, boxToDraw, initialize
    if event == cv2.EVENT_LBUTTONDOWN:
        drawnBox[[0,2]] = x
        drawnBox[[1,3]] = y
        mousedown = True
        mouseupdown = False
    elif mousedown and event == cv2.EVENT_MOUSEMOVE:
        drawnBox[2] = x
        drawnBox[3] = y
    elif event == cv2.EVENT_LBUTTONUP:
        drawnBox[2] = x
        drawnBox[3] = y
        mousedown = False
        mouseupdown = True
        initialize = True
    boxToDraw = drawnBox.copy()
    boxToDraw[[0,2]] = np.sort(boxToDraw[[0,2]])
    boxToDraw[[1,3]] = np.sort(boxToDraw[[1,3]])


def show_webcam(mirror=False):
    global tracker, initialize
    cam = cv2.VideoCapture(0)
    cv2.namedWindow('Custom Brush', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Custom Brush', OUTPUT_WIDTH, OUTPUT_HEIGHT)
    cv2.setMouseCallback('Custom Brush', on_mouse, 0)
    frameNum = 0
    outputDir = None
    outputBoxToDraw = None
    if RECORD:
        print('saving')
        if not os.path.exists('outputs'):
            os.mkdir('outputs')
        tt = time.localtime()
        outputDir = ('outputs/%02d_%02d_%02d_%02d_%02d/' % (tt.tm_mon, tt.tm_mday, tt.tm_hour, tt.tm_min, tt.tm_sec))
        os.mkdir(outputDir)
        labels = open(outputDir + 'labels.txt', 'w')
    while True:
        ret_val, img = cam.read()
        if mirror:
            img = cv2.flip(img, 1)

            # The capability of cropping the end image
        cropped = img[70:170, 440:540] #y1,y2 x1,x2
        #cv2.imshow("dds",cropped)
        origImg = img.copy()
        cv2.rectangle(img,(0,0),(100,720),(0,0,0),-1)
        cv2.putText(img,'Left color:',(10,20),font,0.4,(255,255,255),thickness,cv2.LINE_AA)
        cv2.rectangle(img, (10, 30), (80, 90), (160,196,255) , -1)
        cv2.putText(img,'Right color:',(10,100),font,0.4,(255,255,255),thickness,cv2.LINE_AA)
        cv2.rectangle(img, (10, 110), (80, 170), (97,95,255) , -1)
        cv2.putText(img,'Bottom color:',(10,180),font,0.4,(255,255,255),thickness,cv2.LINE_AA)
        cv2.rectangle(img, (10, 190), (80, 250), (253,255,160) , -1)
        cv2.putText(img,'Line width:',(5,270),font,0.4,(255,255,255),thickness,cv2.LINE_AA)



        if mousedown:
            cv2.rectangle(img,
                    (int(boxToDraw[0]), int(boxToDraw[1])),
                    (int(boxToDraw[2]), int(boxToDraw[3])),
                    [0,0,255], PADDING)
# font  
            if RECORD:
                cv2.circle(img, (int(drawnBox[2]), int(drawnBox[3])), 10, [255,0,0], 4)
        elif mouseupdown:
            if initialize:
                outputBoxToDraw = tracker.track('Custom Brush', img[:,:,::-1], boxToDraw)
                initialize = False
            else:
                outputBoxToDraw = tracker.track('Custom Brush', img[:,:,::-1])
            cv2.rectangle(img,
                    (int(outputBoxToDraw[0]), int(outputBoxToDraw[1])),
                    (int(outputBoxToDraw[2]), int(outputBoxToDraw[3])),
                    [0,0,255], PADDING)

            
            traverse_point = []
            Npoints = {
                "stPoints":(int(outputBoxToDraw[0]),int(outputBoxToDraw[1])),
                "endPoints":(int(outputBoxToDraw[2]),int(outputBoxToDraw[3]))
            }
            lower_dict = {
                "role": "storage for lower left corner coords(x,y)",
                "point_display": (int(outputBoxToDraw[0]-200),int(outputBoxToDraw[3])),
                "point_coordinates": (int(outputBoxToDraw[0]),int(outputBoxToDraw[3])),
                "brush_width":(int(outputBoxToDraw[2]-outputBoxToDraw[0])),
                "mean_coordinates": (int( (outputBoxToDraw[0]+outputBoxToDraw[2])/2 ),int(outputBoxToDraw[3]) )
                }

            #cy=int(outputBoxToDraw[3])
            #cx=int(outputBoxToDraw[0]-50)
            YX = [int(outputBoxToDraw[3]),int(outputBoxToDraw[0]-20),int(outputBoxToDraw[3]),int(outputBoxToDraw[2]+20),int(outputBoxToDraw[3]+20),int((outputBoxToDraw[2]+outputBoxToDraw[0])/2)]
            left_cols=img[YX[0],YX[1]]
            right_cols=img[YX[2],YX[3]]
            bottom_cols=img[YX[4],YX[5]]
            #color2 = img[cy, cx]
            bL=int(left_cols[0])
            gL=int(left_cols[1])
            rL=int(left_cols[2])

            bR=int(right_cols[0])
            gR=int(right_cols[1])
            rR=int(right_cols[2])

            
            bB=int(bottom_cols[0])
            gB=int(bottom_cols[1])
            rB=int(bottom_cols[2])
            #print(parsedC)
            
            org = (70,270)
            color_dict = {
                "left":(bL,gL,rL),
                "right":(bR,gR,rR),
                "bottom":(bB,gB,rB)
            }
# Blue color in BGR 
            color = (255,0,0)
            
            
# Line thickness of 2 px

# Using cv2.putText() method 
            #cv2.putText(img, '{}'.format(Npoints["stPoints"]),Npoints["stPoints"] , font, fontScale, color, thickness, cv2.LINE_AA)
            cv2.putText(img, '{}'.format(lower_dict["point_coordinates"]), lower_dict["point_display"], font, fontScale, color, thickness, cv2.LINE_AA)
            cv2.putText(img, '{}'.format(Npoints["endPoints"]), Npoints["endPoints"], font, fontScale, color, thickness, cv2.LINE_AA)
            
            cv2.rectangle(img,(0,0),(100,720),(0,0,0),-1)
            cv2.rectangle(img, (10, 30), (80, 90), color_dict["left"], -1)
            cv2.rectangle(img, (10, 110), (80, 170), color_dict["right"], -1)
            cv2.rectangle(img, (10, 190), (80, 250), color_dict["bottom"], -1)
            cv2.putText(img,'Line width:',(5,270),font,0.4,(255,255,255),thickness,cv2.LINE_AA)
            cv2.putText(img, '{}'.format(lower_dict["brush_width"]),org, font, 0.4, (255,255,255), thickness, cv2.LINE_AA)
            cv2.putText(img,'mean XY:',(10,300),font,0.4,(255,255,255),thickness,cv2.LINE_AA)
            cv2.putText(img, '{}'.format(lower_dict["mean_coordinates"]),(70,300), font, 0.4, (255,255,255), thickness, cv2.LINE_AA)
            


            def draw_circles(frame, traverse_point):
                if traverse_point is not None:
                    for i in range(len(traverse_point)):
                        cv2.circle(frame, traverse_point[i], int(5 - (5 * i * 3) / 100), [0, 255, 255], -1)

            
            list_1.append(lower_dict["brush_width"])
            coords_x.append(int((outputBoxToDraw[0]+outputBoxToDraw[2])/2))
            coords_y.append(int(outputBoxToDraw[3]))
            
            print(coords_x,coords_y)
            def expCsv(pli):
                
                df = pandas.DataFrame(data={"width":pli})
                df.to_csv("file.csv", sep=',',index=False)


            def coords(l_width,x,y):
                
                ff = pandas.DataFrame(data={"width":l_width,"x":x,"y":y})
                ff.to_csv("coords.csv",sep=',',index=False)
                # Saving as a .txt file 
                #np.savetxt('nps.txt', ff.values, fmt='%d')

            
            coords(list_1,coords_x,coords_y)
            #expCsv(list_1)
        cv2.imshow('Custom Brush', img)
        if RECORD:
            if outputBoxToDraw is not None:
                labels.write('%d %.2f %.2f %.2f %.2f\n' %
                        (frameNum, outputBoxToDraw[0], outputBoxToDraw[1],
                            outputBoxToDraw[2], outputBoxToDraw[3]))
            cv2.imwrite('%s%08d.jpg' % (outputDir, frameNum), img)
            print('saving')
        keyPressed = cv2.waitKey(1)
        if keyPressed == 27 or keyPressed == 1048603:
            break  # esc to quit

        frameNum += 1
    cv2.destroyAllWindows()



# Main function
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Open the Custom Brush tool.')
    parser.add_argument('-r', '--record', action='store_true', default=False)
    args = parser.parse_args()
    RECORD = args.record

    tracker = re3_tracker.Re3Tracker()

    show_webcam(mirror=True)


