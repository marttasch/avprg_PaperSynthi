import cv2
import numpy as np

imgWidth = 1280
imgHeight = 720

#cap = cv2.VideoCapture(1)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, imgWidth)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, imgHeight)

cap = cv2.VideoCapture('opencvTest.mp4')


# --- Color Settings
hsvTreshold = 40
hsv_orange = [14, 38, 59]
hsv_red = [349, 62, 39]
hsv_green = [160, 84, 12]
hsv_blue = [227, 72, 13]
# ----

# --- -Points for warping
inPoint1 = [0, 100]
inPoint2 = [700, 260]
inPoint3 = [0, 700]
inPoint4 = [700, 400]

points2 = np.float32([[0, 200], [600, 0], [0, 700], [1000, 700]])

points1_tuple = np.float32([inPoint1, inPoint2, inPoint3, inPoint4])
points2_tuple = np.float32([points2])
# ----

def get_HSVMask(hsvFrame, hsvColor, hsvTresh):
    target_color_HSV = np.array([hsvColor[0]/2, hsvColor[1]/100*255, hsvColor[2]/100*255])  # convert to HSV value range
    lowBound = target_color_HSV - hsvTresh
    upperBound = target_color_HSV + hsvTresh
    # to ignore Value value:
    lowBound[2] = 50
    upperBound[2] = 255

    maskHSV = cv2.inRange(hsvFrame, lowBound, upperBound)
    return maskHSV

def do_morphology(mask, medianBlur=True, opening=False, closing=False):
    if medianBlur:
        mask = cv2.medianBlur(mask, 5)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    if opening:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    if closing:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask

def make_Mask_colored(frame, mask):
    maskColor = cv2.bitwise_and(frame, frame, mask=mask)

    return maskColor

def find_contours(mask):
    contours, hierachy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    areaArray = []
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        areaArray.append(area)

    #first sort the array by area
    sortedContours = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse=True)
    return sortedContours

def draw_contours(sortedContours, drawToFrame, mask, start, stop, color=(255,0,255), boundingRect=True, minAreaRect=False, contourToMask=False):
    objects = []
    for n in range(start, stop):
        try:
            cnt = sortedContours[n-1][1]
            if contourToMask:
                cv2.drawContours(mask, cnt, -1, color, 2)
            
            # bounding Rectangle
            if boundingRect:
                x,y,w,h = cv2.boundingRect(cnt)
                cv2.rectangle(drawToFrame,(x,y),(x+w,y+h),color,2)
                centerX = x + w/2
                centerY = y + h/2
                objects.append((centerX, centerY))
                #print("contour X, Y: [{}, {}]".format(centerX, centerY))

            # minArea Rectangle
            if minAreaRect:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(drawToFrame,[box],0,color,2)
        except IndexError:
            print("IndexError: list index out of range")
    return objects

def mouseCallbackWarping(event, x, y, flags, param):
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


# --- setup Window
winNameInput = 'input'

cv2.namedWindow(winNameInput)
cv2.setMouseCallback(winNameInput, mouseCallbackWarping)
# ---

frameCount = 0
# Play Video
while cap.isOpened():
    ret, frame = cap.read()

    rotate = True
    if rotate:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

    # ---- set up Layout
    rect_cX, rect_cY, rect_w, rect_h = [300, 200, 200, 150]
    rect_p1 = (rect_cX - rect_w/2 , rect_cY - rect_h/2)
    rect_p2 = (rect_cX + rect_w/2 , rect_cY + rect_h/2)
    rect_p1 = np.array(rect_p1, dtype='int')
    rect_p2 = np.array(rect_p2, dtype='int')

    outPoint1 = [rect_cX - rect_w/2 , rect_cY - rect_h/2]
    outPoint2 = [rect_cX + rect_w/2 , rect_cY - rect_h/2]
    outPoint3 = [rect_cX - rect_w/2 , rect_cY + rect_h/2]
    outPoint4 = [rect_cX + rect_w/2 , rect_cY + rect_h/2]
    # ---- 

    # ---- Warping
    points1_tuple = np.float32([inPoint1, inPoint2, inPoint3, inPoint4])
    points2_tuple = np.float32([outPoint1, outPoint2, outPoint3, outPoint4])

    # -- draw points
    cv2.circle(frame, (inPoint1[0], inPoint1[1]), 5, (255, 0, 255), -1)
    cv2.circle(frame, (inPoint2[0], inPoint2[1]), 5, (255, 0, 255), -1)
    cv2.circle(frame, (inPoint3[0], inPoint3[1]), 5, (255, 0, 255), -1)
    cv2.circle(frame, (inPoint4[0], inPoint4[1]), 5, (255, 0, 255), -1)
    # -- 

    #applying getPerspectiveTransform() function to transform the perspective of the given source image to the corresponding points in the destination image
    resultWarping = cv2.getPerspectiveTransform(points1_tuple, points2_tuple)
    #applying warpPerspective() function to fit the size of the resulting image from getPerspectiveTransform() function to the size of source image
    warpedImage = cv2.warpPerspective(frame, resultWarping, (imgWidth, imgHeight))
    # ----
    
    processedFrame = warpedImage.copy()
    hsvFrame = cv2.cvtColor(warpedImage, cv2.COLOR_BGR2HSV)   # convert to hsv

    contourStart = 1
    contourEnd = 3
    # ---- RED
    maskRed = get_HSVMask(hsvFrame, hsv_red, hsvTreshold)
    maskRed = do_morphology(maskRed, medianBlur=True, opening=True, closing=True)
    # -- find contours
    sortedContours = find_contours(maskRed)
    objects = draw_contours(sortedContours, processedFrame, maskRed, contourStart, contourEnd, (0,0,255), True, False, False)
    # ----
    
    if False:
        # ---- GREEN
        maskGreen = get_HSVMask(hsvFrame, hsv_green, hsvTreshold)
        maskGreen = do_morphology(maskGreen, medianBlur=True, opening=True, closing=True)
        # -- find contours
        sortedContours = find_contours(maskGreen)
        draw_contours(sortedContours, processedFrame, maskGreen, contourStart, contourEnd, (0,255,0), True, False, False)
        # ----

        # ---- Blue
        maskBlue = get_HSVMask(hsvFrame, hsv_blue, hsvTreshold)
        maskBlue = do_morphology(maskBlue, medianBlur=True, opening=True, closing=True)
        # -- find contours
        sortedContours = find_contours(maskBlue)
        draw_contours(sortedContours, processedFrame, maskBlue, contourStart, contourEnd, (255,0,0), True, False, False)
        # ----

    # --- bitmaps color
    maskRed = make_Mask_colored(frame, maskRed)
    #maskGreen = make_Mask_colored(frame, maskGreen)
    #maskBlue = make_Mask_colored(frame, maskBlue)

    #colorMask = cv2.add(maskRed, cv2.add(maskGreen, maskBlue))
    colorMask = maskRed

    



    # ---- colission detection
    if True:
        #processedImage = np.copy(frame)
        # -- draw Layout
        cv2.rectangle(processedFrame, rect_p1, rect_p2, (255,255,0), 2)
        # --

        # -- detect collision
        tresh = 50
        for centerX, centerY in objects:
            if (centerX <= rect_cX + rect_w/2 and centerX >= rect_cX - rect_w/2) and (centerY <= rect_cY + rect_h/2 and centerY >= rect_cY - rect_h/2):
                # in rectangle area / colission detected
                cv2.rectangle(processedFrame, rect_p1+(2,2), rect_p2-(2,2), (0,255,0), 2)
        # --
    # ----


    cv2.imshow(winNameInput, frame)
    cv2.imshow('processed', processedFrame)
    cv2.imshow('mask', colorMask)

    # ---- waitkey
    if cv2.waitKey(25) & 0xFF == 27:   # when escap is pressed
        print("break")
        break


cap.release()
cv2.destroyAllWindows()