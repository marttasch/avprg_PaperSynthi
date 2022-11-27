import cv2
import numpy as np

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# --- Color Settings
hsvTreshold = 40
hsv_orange = [14, 38, 59]
hsv_red = [349, 62, 39]
hsv_green = [160, 84, 12]
hsv_blue = [227, 72, 13]
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
    maskColor = cv2.bitwise_and(frame, mask)

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
                print("contour X, Y: [{}, {}]".format(centerX, centerY))

            # minArea Rectangle
            if minAreaRect:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(drawToFrame,[box],0,color,2)
        except IndexError:
            print("IndexError: list index out of range")



frameCount = 0
# Play Video
while cap.isOpened():
    ret, frame = cap.read()

    rotate = True
    if rotate:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   # convert to hsv

    # ---- RED
    maskRed = get_HSVMask(hsvFrame, hsv_red, hsvTreshold)
    maskRed = do_morphology(maskRed, medianBlur=True, opening=True, closing=True)
    #maskRed = make_Mask_colored(frame, maskRed)
    # -- find contours
    sortedContours = find_contours(maskRed)
    draw_contours(sortedContours, frame, maskRed, 1, 4, (0,0,255), True, False, False)
    # ----

    # ---- GREEN
    maskGreen = get_HSVMask(hsvFrame, hsv_green, hsvTreshold)
    maskGreen = do_morphology(maskGreen, medianBlur=True, opening=True, closing=True)
    #maskGreen = make_Mask_colored(frame, maskGreen)
    # -- find contours
    sortedContours = find_contours(maskGreen)
    draw_contours(sortedContours, frame, maskGreen, 1, 4, (0,255,0), True, False, False)
    # ----

    # ---- Blue
    maskBlue = get_HSVMask(hsvFrame, hsv_blue, hsvTreshold)
    maskBlue = do_morphology(maskBlue, medianBlur=True, opening=True, closing=True)
    #maskBlue = make_Mask_colored(frame, maskBlue)
    # -- find contours
    sortedContours = find_contours(maskBlue)
    draw_contours(sortedContours, frame, maskBlue, 1, 4, (255,0,0), True, False, False)
    # ----
    



    cv2.imshow('processed', frame)
    cv2.imshow('mask', maskRed)

    # ---- waitkey
    if cv2.waitKey(25) & 0xFF == 27:   # when escap is pressed
        print("break")
        break


cap.release()
cv2.destroyAllWindows()