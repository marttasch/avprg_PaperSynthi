import cv2
import numpy as np

imgWidth = 1280
imgHeight = 720

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, imgWidth)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, imgHeight)

#cap = cv2.VideoCapture('opencvTest.mp4')

rotateImage180 = True

# set how many contours to take for object detection
contourStart = 1
contourEnd = 3


# --- Color Settings
hsvTreshold = 40
hsv_orange = [14, 38, 59]
hsv_red = [349, 62, 39]
hsv_green = [160, 84, 12]
hsv_blue = [227, 72, 13]
# ----

# ----- Class
class Layout:
    def __init__(self, name, type, cx, cy, width, heigth, colorRGB, midiNote):
        if type not in ('faderH', 'faderV', 'button'):
            print('Layout Element cant be created: Wrong type')
            return
        elif type == 'button':
            self.type = type
            self.pressed = False
        elif type in ('faderH', 'faderV'):
            self.type = type
            self.value = 0

        self.name = name
        self.center = (cx, cy)
        self.size = (width, heigth)
        self.color = colorRGB
        self.note = midiNote

        self.calcRectPoints()
    
    # -- Getter
    def getName(self):
        print("LayoutName: ", self.function)

    # -- Setter

    # ---- Functions
    # -- main func
    def update(self, imageToDrawOn, objects):
        self.draw(imageToDrawOn)
        self.checkCollision(imageToDrawOn, objects)
        #self.playmidi()

    # -- init
    def calcRectPoints(self):
        self.p_ul = np.array((self.center[0] - self.size[0]/2, self.center[1] - self.size[1]/2), dtype='int')
        self.p_ur = np.array((self.center[0] + self.size[0]/2, self.center[1] - self.size[1]/2), dtype='int')
        self.p_bl = np.array((self.center[0] - self.size[0]/2, self.center[1] + self.size[1]/2), dtype='int')
        self.p_br = np.array((self.center[0] + self.size[0]/2, self.center[1] + self.size[1]/2), dtype='int')

    # -- all functions
    def draw(self, frame):
        cv2.rectangle(frame, self.p_ur, self.p_bl, self.color, 2)
        return

    def checkCollision(self, frame, objects):

        # check for every object, if object center is inside rectangle
        for obj_cX, obj_cY, obj_w, obj_h in objects:
            if (obj_cX <= self.center[0] + self.size[0]/2 and obj_cX >= self.center[0] - self.size[0]/2) and (obj_cY <= self.center[1] + self.size[1]/2 and obj_cY >= self.center[1] - self.size[1]/2):
                # colission detected / in rectangle area
                
                if self.type == 'button':
                    # get value
                    self.pressed = True
                    
                    # draw visual feedback
                    cv2.rectangle(frame, self.p_ur+(2,2), self.p_bl-(2,2), (0,255,255), 2)
                    cv2.putText(frame, self.name, np.int16((self.center[0]-self.size[0]/2+10, self.center[1]+10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
                    
                    # print in console
                    print(self.name, ': pressed',)   # console feedback
                
                if self.type == 'faderH':
                    # get value
                    value = obj_cX - (self.center[0] - self.size[0]/2)
                    value = value / (self.size[0]) * 100
                    self.value = value

                    # draw visual feedback
                    cv2.rectangle(frame, self.p_ur+(2,2), self.p_bl-(2,2), (0,255,255), 2)
                    cv2.line(frame,np.int16((obj_cX, self.center[1]+self.size[1]/2)), np.int16((obj_cX, self.center[1]-self.size[1]/2)), (0,0,0), 3)
                    cv2.putText(frame, str(np.round(self.value, 1)), np.int16((obj_cX + 5, self.center[1]+self.size[1]/2 -10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
                    
                    # print in console
                    print(self.name, ' = ', self.value)
                
                if self.type == 'faderV':
                    # get value
                    value = obj_cY - (self.center[1] - self.size[1]/2)
                    value = value / (self.size[1]) * 100
                    self.value = value

                    # draw visual feedback
                    cv2.rectangle(frame, self.p_ur+(2,2), self.p_bl-(2,2), (0,255,255), 2)
                    cv2.line(frame,np.int16((self.center[0]-self.size[0]/2, obj_cY)), np.int16((self.center[0]+self.size[0]/2, obj_cY)), (0,0,0), 3)
                    cv2.putText(frame, str(np.round(self.value, 1)), np.int16((self.center[0]-self.size[0]/2, obj_cY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
                    
                    # print in console
                    print(self.name, ' = ', self.value)
        

    def playMidi():
        return

# -----


def get_HSVMask(hsvFrame, hsvColor, hsvTresh):
    """Create Bitmask of given HSV-Frame and HSV-Color"""

    target_color_HSV = np.array([hsvColor[0]/2, hsvColor[1]/100*255, hsvColor[2]/100*255])  # convert to HSV value range
    lowBound = target_color_HSV - hsvTresh
    upperBound = target_color_HSV + hsvTresh
    # to ignore Value value:
    lowBound[2] = 50
    upperBound[2] = 255

    maskHSV = cv2.inRange(hsvFrame, lowBound, upperBound)
    return maskHSV

def do_morphology(mask, medianBlur=True, opening=False, closing=False):
    """Apply diffrent Types of morphology to given bitmask"""

    if medianBlur:
        mask = cv2.medianBlur(mask, 5)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    if opening:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    if closing:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask

def make_Mask_colored(frame, mask):
    """Color a given bitmask with original color of a frame"""

    maskColor = cv2.bitwise_and(frame, frame, mask=mask)
    return maskColor

def find_contours(mask):
    """Find all Contours in a mask and return areas in an array sorted by size"""

    # find all contours and write areas in an aray
    areaArray = []
    contours, hierachy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        areaArray.append(area)

    # sort Array by area size, start with biggest
    sortedContours = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse=True)
    return sortedContours

def detect_objects(sortedContours, drawToFrame, mask, start, stop, color=(255,0,255), boundingRect=True, contourToMask=False):
    """Detect the biggest objects from sortedAreas and create an object Array, also draw visual Feedback around."""
    
    objects = []
    # start and stop with sorted by biggest area
    for n in range(start, stop):
        try:
            cnt = sortedContours[n-1][1]   # select current contour

            # if True, draw Contour to mask
            if contourToMask:
                cv2.drawContours(mask, cnt, -1, color, 2)
            
            # if True, append object to list and draw bounding rect around object
            if boundingRect:
                x,y,w,h = cv2.boundingRect(cnt)
                cv2.rectangle(drawToFrame,(x,y),(x+w,y+h),color,2)
                
                cX = x + w/2
                cY = y + h/2
                objects.append((cX, cY, w, h))

        except IndexError:
            # no Objects available
            print("IndexError: list index out of range")
        
    return objects

def mouseCallbackWarping(event, x, y, flags, param):
    """Callback Function for mouse input on input window"""

    # left mousebutton click
    if event == cv2.EVENT_LBUTTONDOWN:
        print('mouse Click')

        # corner upper left
        if (x <= imgWidth/2) and (y <= imgHeight/2):
            (inPoint1[0], inPoint1[1]) = (x, y)
            print("Mouseclick Area 1: ", x, y)
            return inPoint1
        
        # corner upper right
        if (x >= imgWidth/2) and (y <= imgHeight/2):
            (inPoint2[0], inPoint2[1]) = (x, y)
            print("Mouseclick Area 2: ", x, y)
            return inPoint2

        # corner lower left
        if (x <= imgWidth/2) and (y >= imgHeight/2):
            (inPoint3[0], inPoint3[1]) = (x, y)
            print("Mouseclick Area 3: ", x, y)
            return inPoint3

        # corner lower right
        if (x >= imgWidth/2) and (y >= imgHeight/2):
            (inPoint4[0], inPoint4[1]) = (x, y)
            print("Mouseclick Area 4: ", x, y)
            return inPoint4

# ---- Points for warping

# map inPoints to outPoints
outPoint1 = [31, 31]
outPoint2 = [1245, 31]
outPoint3 = [31, 692]
outPoint4 = [1245, 692]

# no warping for now
inPoint1 = outPoint1
inPoint2 = outPoint2
inPoint3 = outPoint3
inPoint4 = outPoint4

# save as array
points1_tuple = np.float32([inPoint1, inPoint2, inPoint3, inPoint4])
points2_tuple = np.float32([outPoint1, outPoint2, outPoint3, outPoint4])
# ----


# ---- set up Layout
layout = []
# generel
layout.append(Layout('mode keys', 'button', 81, 81, 100, 100, (255,255,0), 'note'))
layout.append(Layout('Record', 'button', 81, 188, 100, 100, (255,255,0), 'note'))
layout.append(Layout('Distortion', 'button', 81, 295, 100, 100, (255,255,0), 'note'))
layout.append(Layout('Modus Drums', 'button', 188, 81, 100, 100, (255,255,0), 'note'))
layout.append(Layout('Play', 'button', 188, 188, 100, 100, (255,255,0), 'note'))
layout.append(Layout('Reverb', 'button', 188, 295, 100, 100, (255,255,0), 'note'))
layout.append(Layout('Modus Sounds', 'button', 295, 81, 100, 100, (255,255,0), 'note'))
layout.append(Layout('Pitch', 'faderV', 76, 527, 90, 330, (90,90,90), 'note'))
layout.append(Layout('Bend', 'faderV', 173, 527, 90, 330, (90,90,90), 'note'))
layout.append(Layout('Gain', 'faderV', 270, 527, 90, 330, (90,90,90), 'note'))
# Oszi1
layout.append(Layout('Volume', 'faderH', 584, 107, 420, 73, (205,100,205), 'note'))
layout.append(Layout('LFO', 'faderH', 584, 180, 420, 73, (205,100,205), 'note'))
layout.append(Layout('Sinus', 'button', 427, 266, 105, 100, (205,100,205), 'note'))
layout.append(Layout('Triangle', 'button', 532, 266, 105, 100, (205,100,205), 'note'))
layout.append(Layout('Sawtooth', 'button', 637, 266, 105, 100, (205,100,205), 'note'))
layout.append(Layout('Rectangle', 'button', 742,266, 105, 100, (205,100,205), 'note'))
# Oszi2
layout.append(Layout('Volume', 'faderH', 1035, 107, 420, 73, (205,100,100), 'note'))
layout.append(Layout('LFO', 'faderH', 1035, 180, 420, 73, (205,100,100), 'note'))
layout.append(Layout('Sinus', 'button', 878, 266, 105, 100, (205,100,100), 'note'))
layout.append(Layout('Triangle', 'button', 983, 266, 105, 100, (205,100,100), 'note'))
layout.append(Layout('Sawtooth', 'button', 1088, 266, 105, 100, (205,100,100), 'note'))
layout.append(Layout('Rectangle', 'button', 1193,266, 105, 100, (205,100,100), 'note'))

# ----


# ---- setup Window
winNameInput = 'input'
winNameProcessed = 'processed'

# setup MouseCallback for Warping Input
cv2.namedWindow(winNameInput)
cv2.setMouseCallback(winNameInput, mouseCallbackWarping)
# ---


# ------------------------
# ------ Main Loop -------
# ------------------------
while cap.isOpened():
    ret, frame = cap.read()

    # rotate frame
    if rotateImage180:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

    # ---- Warping
    if True:
        # convert points from mousCallback to Array
        points1_tuple = np.float32([inPoint1, inPoint2, inPoint3, inPoint4])

        # -- draw points
        cv2.circle(frame, (inPoint1[0], inPoint1[1]), 5, (255, 0, 255), -1)
        cv2.circle(frame, (inPoint2[0], inPoint2[1]), 5, (255, 0, 255), -1)
        cv2.circle(frame, (inPoint3[0], inPoint3[1]), 5, (255, 0, 255), -1)
        cv2.circle(frame, (inPoint4[0], inPoint4[1]), 5, (255, 0, 255), -1)
        # -- 

        # warp image
        resultWarping = cv2.getPerspectiveTransform(points1_tuple, points2_tuple)
        warpedImage = cv2.warpPerspective(frame, resultWarping, (imgWidth, imgHeight))
    # ----

    # ---- Detect Objects
    if True:
        # copy frame and convert to hsv
        processedFrame = warpedImage.copy()
        hsvFrame = cv2.cvtColor(warpedImage, cv2.COLOR_BGR2HSV)

        # ---- RED
        maskRed = get_HSVMask(hsvFrame, hsv_red, hsvTreshold)
        maskRed = do_morphology(maskRed, medianBlur=True, opening=True, closing=True)
        # -- find contours
        sortedContours = find_contours(maskRed)
        objects = detect_objects(sortedContours, processedFrame, maskRed, contourStart, contourEnd, (0,0,255), True, False)
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
    # --------- 

    # ---- update Layout
    for n in range(0, len(layout)):
        layout[n].update(processedFrame, objects)
    # ----

    cv2.imshow(winNameInput, frame)
    cv2.imshow(winNameProcessed, processedFrame)
    #cv2.imshow('mask', colorMask)

    # ---- waitkey
    if cv2.waitKey(25) & 0xFF == 27:   # when escap is pressed
        print("break")
        break


cap.release()
cv2.destroyAllWindows()