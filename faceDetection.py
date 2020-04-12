import numpy as np
import cv2
face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)

if not (cap.isOpened()):
    print("External camera not found. \n Going for internal camera")
    #2nd cam
    cap = cv2.VideoCapture(1)
if not (cap.isOpened()):
    print("Device not found")

while(True):
    #capture frame-by-frame
    _, frame = cap.read()

    grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(grayImage)

    # print(type(faces))

    if len(faces) == 0:
        print("No faces found")

    else:
        # print(faces)
        # print(faces.shape)
        # print("Number of faces detected: " + str(faces.shape[0]))

        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),1)

        cv2.rectangle(frame, ((0,frame.shape[0] -25)),(270, frame.shape[0]), (255,255,255), -1)
        cv2.putText(frame, "Number of faces detected: " + str(faces.shape[0]), (0,frame.shape[0] -10), cv2.FONT_HERSHEY_TRIPLEX, 0.5,  (0,0,0), 1)

        cv2.imshow('Image with faces',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
