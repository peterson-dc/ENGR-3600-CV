import cv2
import numpy as np
import sys
import time
import argparse

# Add arguments for min, max, and debug
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("--min", required=False, default=100)
ap.add_argument("--max", required=False, default=300)
ap.add_argument("-d", "--debug", required=False, help="enter debug mode", action="store_true")
args = ap.parse_args()
DEBUG = args.debug
MIN_LEN = int(args.min)
MAX_LEN = int(args.max)

def drawBox(im, bbox):
    n = len(bbox)
    for j in range(n):
        cv2.line(im, tuple(bbox[j][0]), tuple(bbox[ (j+1) % n][0]), (255,0,0), 3)
    return im

def findAvgLen(bbox):
    n = len(bbox)
    totalLen = 0
    for j in range(n):
        point1 = tuple(bbox[j][0])
        point2 = tuple(bbox[ (j+1) % n][0])
        totalLen += np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    return totalLen / n

capture = cv2.VideoCapture(0)

if not (capture.isOpened()):
    print("External camera not found. \n Going for internal camera")
    #2nd cam
    capture = cv2.VideoCapture(1)
if not (capture.isOpened()):
    print("Device not found")

qrDecoder = cv2.QRCodeDetector()

if DEBUG:
    start = time.time()
avgLen = 0
lines = []

while(True):
    ret, frame = capture.read()

    grayscale_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect and decode the qrcode
    retval, points = qrDecoder.detect(grayscale_img)

    if retval:
        frame = drawBox(frame, points)
        avgLen = findAvgLen(points)
        if DEBUG:
            print(str(avgLen))
        if avgLen < MIN_LEN:
            # insert gpio 10
            if DEBUG:
                print("FORWARD")
        elif avgLen > MAX_LEN:
            # insert gpio 11
            if DEBUG:
                print("BACKWARD")
    if DEBUG:
        cv2.putText(frame, "FPS: " + str(1/(time.time() - start)), (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        start = time.time()
        cv2.imshow("Original Image", frame)
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

capture.release()
