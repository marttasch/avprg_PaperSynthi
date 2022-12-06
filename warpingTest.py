#importing the module cv2 and numpy
import cv2
import numpy as np

imgWidth = 1280
imgHeight = 720

cap = cv2.VideoCapture('./opencvTest.mp4')
#cap = cv2.VideoCapture(1)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, imgWidth)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, imgHeight)


#specifying the points in the source image which is to be transformed to the corresponding points in the destination image
#points1 = np.float32([[0, 100], [700, 260], [0, 700], [700, 400]])
points2 = np.float32([[0, 200], [600, 0], [0, 700], [1000, 700]])

inPoint1 = [0, 100]
inPoint2 = [700, 260]
inPoint3 = [0, 700]
inPoint4 = [700, 400]

points1_tuple = np.float32([inPoint1, inPoint2, inPoint3, inPoint4])
points2_tuple = np.float32([points2])


def mouseCallback(event, x, y, flags, param):
    #print('mouseCallback')
    if event == cv2.EVENT_LBUTTONDOWN:
        print('mouse Click')
        if (x <= imgWidth/2) and (y <= imgHeight/2):
            (inPoint1[0], inPoint1[1]) = (x, y)
            print("Mouseclick Area 1: ", x, y)
            return inPoint1
        if (x >= imgWidth/2) and (y <= imgHeight/2):
            (inPoint2[0], inPoint2[1]) = (x, y)
            print("Mouseclick Area 2: ", x, y)
            return inPoint2
        if (x <= imgWidth/2) and (y >= imgHeight/2):
            (inPoint3[0], inPoint3[1]) = (x, y)
            print("Mouseclick Area 3: ", x, y)
            return inPoint3
        if (x >= imgWidth/2) and (y >= imgHeight/2):
            (inPoint4[0], inPoint4[1]) = (x, y)
            print("Mouseclick Area 4: ", x, y)
            return inPoint4


cv2.namedWindow('input')
cv2.setMouseCallback('input', mouseCallback)

while cap.isOpened():

    ret, frame = cap.read()

    rotate = True
    if rotate:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

    points1_tuple = np.float32([inPoint1, inPoint2, inPoint3, inPoint4])

    # -- draw Mouse Areas
    #cv2.rectangle(frame, (0, 0), (imgWidth/2, imgHeight/2), (255,0,255), 2)
    #cv2.rectangle(frame, (imgWidth/2, 0), (imgWidth, imgHeight/2), (255,0,255), 2)
    #cv2.rectangle(frame, (0, imgHeight/2), (imgWidth/2, imgHeight), (255,0,255), 2)
    #cv2.rectangle(frame, (imgWidth/2, imgHeight/2), (imgWidth, imgHeight), (255,0,255), 2)
    # --

    # -- draw points
    cv2.circle(frame, (inPoint1[0], inPoint1[1]), 5, (255, 0, 255), -1)
    cv2.circle(frame, (inPoint2[0], inPoint2[1]), 5, (255, 0, 255), -1)
    cv2.circle(frame, (inPoint3[0], inPoint3[1]), 5, (255, 0, 255), -1)
    cv2.circle(frame, (inPoint4[0], inPoint4[1]), 5, (255, 0, 255), -1)
    # -- 

        
    #applying getPerspectiveTransform() function to transform the perspective of the given source image to the corresponding points in the destination image
    resultimage = cv2.getPerspectiveTransform(points1_tuple, points2_tuple)
    #applying warpPerspective() function to fit the size of the resulting image from getPerspectiveTransform() function to the size of source image
    finalimage = cv2.warpPerspective(frame, resultimage, (1280, 720))


    cv2.imshow('input', frame)
    cv2.imshow('Dest', finalimage)

    # ---- waitkey
    if cv2.waitKey(25) & 0xFF == 27:   # when escap is pressed
        print("break")
        break


cv2.destroyAllWindows()