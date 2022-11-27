import cv2
import numpy as np

# get video stream
cap = cv2.VideoCapture(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

frameWidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frameHeight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(str(frameHeight) + 'x' + str(frameWidth))


# --------- 
winNameOriginal = "Original"
winNameProcessed = "Processed Image"

cv2.namedWindow(winNameProcessed, )     
cv2.namedWindow(winNameOriginal)

threshold = 20
h, s, v = [183, 9, 60]
target_color_HSV = np.array([h/2, s/100*255, v/100*255])  # convert to HSV value range

lowBound = target_color_HSV - threshold
upperBound = target_color_HSV + threshold
# to ignore Value value:
lowBound[2] = 50
upperBound[2] = 255


# Play Video
while cap.isOpened():
    ret, frame = cap.read()
        
    rotate = True
    if rotate:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    maskHSV = cv2.inRange(hsvFrame, lowBound, upperBound)

    # ---- opening/ closing
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(maskHSV, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    mask = closing
    # ----

    # ---- edges
    edges = cv2.Canny(frame, 100, 200)
    
    # ---- find contours
    contours, hierachy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # find biggest Area index
    maxConIndex = -1    # reset Index
    maxArea = 0    # reset Area
    # find max Area
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])   # Fläche 
        if area > maxArea:
            maxConIndex = i
            maxArea = area

    # --
    areaArray = []
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        areaArray.append(area)

    #first sort the array by area
    sorteddata = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse=True)
    
    if False:
        # draw n-th areas
        n = 8
        # Initialize empty list
        framePixel = []

        areaMask = np.zeros_like(frame)   # black frame
        areaMasksList = []


        # go trough n-th largest areas
        for i in range(1, n):
            cnt = sorteddata[i-1][1]
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            #cv2.drawContours(frame,[box],0,(0,0,255),-1)

            #areaMasksList[i] = np.zeros_like(frame)
            cv2.drawContours(areaMask,[box],0,(255,255,255),-1)
            cv2.drawContours(areaMask,[box],0,(0,0,255),2)
            cv2.drawContours(frame, contours, -1, (255,0,0),2)

            colorAreaMask = cv2.bitwise_and(areaMask, frame)

            # For each list of contour points...
            
            # Create a mask image that contains the contour filled in
         #   cimg = np.zeros_like(frame)
         #   cv2.drawContours(cimg, cnt, -1, color=255, thickness=-1)

            # Access the image pixels and create a 1D numpy array then add to list
         #   pts = np.where(cimg == 255)
         #   framePixel.append(frame[pts[0], pts[1]])

        #cv2.imshow('cimg', cimg)

    # ----
    
    # ---- draw box around contour
    # if maxArea found
    if maxConIndex != -1:
        cnt = contours[maxConIndex]   # set countour with max Area
        cv2.drawContours(mask, cnt, -1, (0, 255, 0), 2)

        # bounding Rectangle
        if False:
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            centerX = x + w/2
            centerY = y + h/2
            print("contour X, Y: [{}, {}]".format(centerX, centerY))

        # minArea Rectangle
        if False:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame,[box],0,(0,0,255),2)
        
        # minArea 2nd Rectangle
        n = 2
        if False:
            rect = cv2.minAreaRect(sorteddata[n-1][1])
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame,[box],0,(0,0,255),-1)
                            
        
        
    # ----
    

    # ---- show Images
    cv2.imshow(winNameOriginal, frame)
    cv2.imshow(winNameProcessed, mask)
    cv2.imshow("edges", edges)
    cv2.imshow("areaMask", areaMask)
    cv2.imshow("colorAreaMask", colorAreaMask)
    # ----

    # ---- waitkey
    if cv2.waitKey(25) & 0xFF == 27:   # when escap is pressed
        print("break")
        break


cap.release()
cv2.destroyAllWindows()



