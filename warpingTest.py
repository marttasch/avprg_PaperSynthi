#importing the module cv2 and numpy
import cv2
import numpy as np

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


#specifying the points in the source image which is to be transformed to the corresponding points in the destination image
points1 = np.float32([[0, 100], [700, 260], [0, 700], [700, 400]])
points2 = np.float32([[0, 200], [600, 0], [0, 700], [1000, 700]])


while cap.isOpened():

    ret, frame = cap.read()

    rotate = True
    if rotate:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        
    #applying getPerspectiveTransform() function to transform the perspective of the given source image to the corresponding points in the destination image
    resultimage = cv2.getPerspectiveTransform(points1, points2)
    #applying warpPerspective() function to fit the size of the resulting image from getPerspectiveTransform() function to the size of source image
    finalimage = cv2.warpPerspective(frame, resultimage, (1280, 720))


    cv2.imshow('Source', frame)
    cv2.imshow('Dest', finalimage)

    # ---- waitkey
    if cv2.waitKey(25) & 0xFF == 27:   # when escap is pressed
        print("break")
        break


cv2.destroyAllWindows()