import cv2
import numpy as np

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# --- Color Settings
threshold = 40
hsv_orange = [14, 38, 59]
hsv_red = [349, 62, 39]
hsv_green = [160, 84, 12]
hsv_blue = [227, 72, 13]

hsv = hsv_orange
target_color_HSV = np.array([hsv[0]/2, hsv[1]/100*255, hsv[2]/100*255])  # convert to HSV value range

lowBound = target_color_HSV - threshold
upperBound = target_color_HSV + threshold
# to ignore Value value:
lowBound[2] = 50
upperBound[2] = 255
# ----





frameCount = 0
# Play Video
while cap.isOpened():
    ret, frame = cap.read()

    rotate = True
    if rotate:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   # convert to hsv

    maskHSV = cv2.inRange(hsvFrame, lowBound, upperBound)
    median = cv2.medianBlur(maskHSV, 5)
    # ----

    # ---- opening/ closing
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(maskHSV, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    mask = closing
    # ----

    # ---- make mask colored
    maskColor = cv2.bitwise_and(frame, frame, mask=mask)
    mask = maskColor
    # ----

    # ---- find contours
    contours, hierachy = cv2.findContours(maskHSV, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # find biggest Area index
    maxConIndex = -1    # reset Index
    maxArea = 0    # reset Area
    # find max Area
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])   # Fläche 
        if area > maxArea:
            maxConIndex = i
            maxArea = area
    # ----
    
    # ---- draw box around contour
    # if Area found
    if maxConIndex != -1:
        cnt = contours[maxConIndex]   # set countour with max Area
        cv2.drawContours(mask, cnt, -1, (0, 255, 0), 2)

        # bounding Rectangle
        if True:
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            centerX = x + w/2
            centerY = y + h/2
            print("contour X, Y: [{}, {}]".format(centerX, centerY))

        # minArea Rectangle
        if True:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame,[box],0,(0,0,255),2)
    # ----

    # ---- Rectangle
    rect_cX, rect_cY, rect_w, rect_h = [300, 200, 200, 150]
    rect_p1 = (rect_cX - rect_w/2 , rect_cY - rect_h/2)
    rect_p2 = (rect_cX + rect_w/2 , rect_cY + rect_h/2)
    rect_p1 = np.array(rect_p1, dtype='int')
    rect_p2 = np.array(rect_p2, dtype='int')

    processedImage = np.copy(frame)
    tresh = 50
    if (centerX <= rect_cX + rect_w/2 and centerX >= rect_cX - rect_w/2) and (centerY <= rect_cY + rect_h/2 and centerY >= rect_cY - rect_h/2):
        # in rectangle area
        cv2.rectangle(processedImage, rect_p1, rect_p2, (0,255,0), 2)
    else:
        cv2.rectangle(processedImage, rect_p1, rect_p2, (0,0,255), 2)
  
    # ----

    cv2.imshow('processed', processedImage)
    cv2.imshow('mask', mask)

    # ---- waitkey
    if cv2.waitKey(25) & 0xFF == 27:   # when escap is pressed
        print("break")
        break


cap.release()
cv2.destroyAllWindows()