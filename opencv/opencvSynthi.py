import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import matplotlib.path as mpltPath

from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

midiout, port_name = open_midioutput(1)

# ####### Settings #######
imgWidth = 1280
imgHeight = 720

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, imgWidth)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, imgHeight)

#cap = cv2.VideoCapture('opencvTest.mp4')

rotateImage180 = True

# set how many contours to take for object detection
contourStart = 0
contourEnd = 11

# ####### Settings end #######

handDetector = HandDetector(detectionCon=0.8, maxHands=2)

# --- Color Settings
hsvTreshold = 60
hsv_orange = [14, 38, 59]
hsv_red = [349, 62, 39]
hsv_green = [160, 84, 12]
hsv_blue = [204, 56, 35]
# ----

# ----- Class Layout
class Layout:
    def __init__(self, name, type, cx, cy, width, heigth, colorRGB, midiNote):
        if type not in ('faderH', 'faderV', 'button'):
            raise Exception('Layout Element cant be created: Wrong type')

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
        self.playMidi()

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
        

    def playMidi(self):
        return

# -----

# ---- Class Key
class Key:
    def __init__(self, name, type, vertices, colorRGB, midiNote):
        if type not in ('white', 'black'):
            raise Exception('Key cant be created: Wrong Type')
        
        else:
            self.type = type

        self.name = name
        self.color = colorRGB
        self.note = midiNote

        self.pressed = False
        self.prevPressed = False
        self.stateChange = False

        self.note_on = [0x90, self.note, 112] # channel 1, note, velocity 112
        self.note_off = [0x80, self.note, 0]

        vertices = np.array(vertices)
        self.vertices = vertices
        pts = vertices.reshape((-1,1,2)) 
        self.points = pts

    def update(self, imageToDrawon, fingertipObjects):
                
        self.checkCollision(imageToDrawon, fingertipObjects)
        if self.prevPressed != self.pressed:
            self.stateChange = True
        else:
            self.stateChange = False
        self.prevPressed = self.pressed

        self.draw(imageToDrawon)
        self.playMidi()
        return

    def draw(self, frame):

        if self.pressed:
            # filled overlay
            print('key', self.name, ' filled, pressed: ', self.pressed)
            alpha = 0.6   # opacity
            overlay = frame.copy()
            cv2.fillPoly(overlay, [self.vertices], (0,255,255))   # filled polygon
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, dst=frame)   # transparent overlay
            cv2.polylines(frame, [self.vertices], isClosed=False, color=(0,255,255), thickness=2)   # border
        else:
            if self.type == 'black':
                alpha = 0.2
            else:
                alpha = 0.1
            overlay = frame.copy()
            cv2.fillPoly(overlay, [self.vertices], self.color)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, dst=frame)

        cv2.polylines(frame, [self.vertices], isClosed=False, color=self.color, thickness=2)


    def checkCollision(self, frame, objects):
        #self.prevPressed = self.pressed
        if objects:
            for obj_cX, obj_cY, obj_w, obj_h in objects:

                fingerXY = np.array([obj_cX, obj_cY]).reshape(1, 2)
                path = mpltPath.Path(self.vertices)

                pressed = path.contains_points(fingerXY)

                #if self.prevPressed != pressed:
                #    self.stateChange = True 
                #else:
                #    self.stateChange = False

                if pressed:
                    self.pressed = True
                    print('Key ', self.name, ' pressed.')
                    break
                else:
                    self.pressed = False
        else:
            self.pressed = False
            #self.stateChange = False
        
    
    def playMidi(self):
        if self.stateChange:
            if self.pressed:
                midiout.send_message(self.note_on)
                print('send midi: ', self.name, self.note_on)
            else:
                midiout.send_message(self.note_off)
                print('send midi: ', self.name, self.note_off)
        return

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

def do_morphology(mask, medianBlur=True, opening=False, closing=False, dilation=False):
    """Apply diffrent Types of morphology to given bitmask"""

    if medianBlur:
        mask = cv2.medianBlur(mask, 5)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8,8))
    if opening:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    if closing:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    if dilation:
        mask = cv2.dilate(mask, kernel, iterations=3)
    
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
            #print("IndexError: list index out of range")
            pass
        
    return objects

def detect_hands(frame):
    # Find the hand and its landmarks
    hands, frame = handDetector.findHands(frame)  # with draw
    lmList1 = []
    lmList2 = []

    if hands:
        # Hand 1
        hand1 = hands[0]
        lmList1 = hand1["lmList"]  # List of 21 Landmark points

        if len(hands) == 2:
            # Hand 2
            hand2 = hands[1]
            lmList2 = hand2["lmList"]  # List of 21 Landmark points

    return lmList1, lmList2


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


# ---- set up keys
keys = []
# 1st octave white
polygon = np.array([[345, 342], [345, 692], [410, 692], [410, 585], [387, 585], [387, 342], [345, 342]], np.int32)
keys.append(Key('C', 'white', polygon, (90, 165, 0), midiNote=60))
polygon = np.array([[433, 342], [433, 585], [410, 585], [410, 692], [473, 692], [473, 585], [451, 585], [451, 342], [433, 342]], np.int32)
keys.append(Key('D', 'white', polygon, (90, 165, 0), midiNote=62))
polygon = np.array([[497, 342], [497, 585], [473, 585], [473, 692], [538, 692], [538, 342], [497, 342]], np.int32)
keys.append(Key('E', 'white', polygon, (90, 165, 0), midiNote=64))
polygon = np.array([[538, 342], [538, 692], [603, 692], [603, 585], [580, 585], [580, 342], [538, 342]], np.int32)
keys.append(Key('F', 'white', polygon, (90, 165, 0), midiNote=65))
polygon = np.array([[626, 342], [626, 585], [603, 585], [603, 692], [666, 692], [666, 585], [644, 585], [644, 342], [626, 342]], np.int32)
keys.append(Key('G', 'white', polygon, (90, 165, 0), midiNote=67))
polygon = np.array([[690, 342], [690, 585], [666, 585], [666, 692], [730, 692], [730, 585], [708, 585], [708, 342], [690, 342]], np.int32)
keys.append(Key('A', 'white', polygon, (90, 165, 0), midiNote=69))
polygon = np.array([[754, 342], [754, 585], [730, 585], [730, 692], [795, 692], [795, 342], [754, 342]], np.int32)
keys.append(Key('H', 'white', polygon, (90, 165, 0), midiNote=71))

# 1st octave black
polygon = np.array([[387, 342], [387, 585], [433, 585], [433, 342], [387, 342]], np.int32)
keys.append(Key('C#', 'black', polygon, (60, 110, 0), midiNote=61))
polygon = np.array([[451, 342], [451, 585], [497, 585], [497, 342], [451, 342]], np.int32)
keys.append(Key('D#', 'black', polygon, (60, 110, 0), midiNote=63))
polygon = np.array([[580, 342], [580, 585], [626, 585], [626, 342], [580, 342]], np.int32)
keys.append(Key('F#', 'black', polygon, (60, 110, 0), midiNote=66))
polygon = np.array([[644, 342], [644, 585], [690, 585], [690, 342], [644, 342]], np.int32)
keys.append(Key('G#', 'black', polygon, (60, 110, 0), midiNote=68))
polygon = np.array([[708, 342], [708, 585], [754, 585], [754, 342], [708, 342]], np.int32)
keys.append(Key('A#', 'black', polygon, (60, 110, 0), midiNote=70))

# 2nd octave white
polygon = np.array([[795, 342], [795, 692], [859, 692], [859, 585], [836, 585], [836, 342], [795, 342]], np.int32)
keys.append(Key('C1', 'white', polygon, (90, 165, 0), midiNote=72))
polygon = np.array([[882, 342], [882, 585], [859, 585], [859, 692], [923, 692], [923, 585], [901, 585], [901, 342], [882, 342]], np.int32)
keys.append(Key('D1', 'white', polygon, (90, 165, 0), midiNote=74))
polygon = np.array([[945, 342], [945, 585], [923, 585], [923, 692], [988, 692], [988, 342], [945, 342]], np.int32)
keys.append(Key('E1', 'white', polygon, (90, 165, 0), midiNote=76))
polygon = np.array([[988, 342], [988, 692], [1052, 692], [1052, 585], [1029, 585], [1029, 342], [988, 342]], np.int32)
keys.append(Key('F1', 'white', polygon, (90, 165, 0), midiNote=77))
polygon = np.array([[1075, 342], [1075, 585], [1052, 585], [1052, 692], [1116, 692], [1116, 585], [1094, 585], [1094, 342], [1075, 342]], np.int32)
keys.append(Key('G1', 'white', polygon, (90, 165, 0), midiNote=79))
polygon = np.array([[1139, 342], [1139, 585], [1116, 585], [1116, 692], [1180, 692], [1180, 585], [1158, 585], [1158, 342], [1139, 342]], np.int32)
keys.append(Key('A1', 'white', polygon, (90, 165, 0), midiNote=81))
polygon = np.array([[1203, 342], [1203, 585], [1180, 585], [1180, 692], [1244, 692], [1244, 342], [1203, 342]], np.int32)
keys.append(Key('H1', 'white', polygon, (90, 165, 0), midiNote=83))

# 2nd octave black
polygon = np.array([[836, 342], [836, 585], [882, 585], [882, 342], [836, 342]], np.int32)
keys.append(Key('C1#', 'black', polygon, (60, 110, 0), midiNote=73))
polygon = np.array([[901, 342], [901, 585], [945, 585], [945, 342], [901, 342]], np.int32)
keys.append(Key('D1#', 'black', polygon, (60, 110, 0), midiNote=75))
polygon = np.array([[1029, 342], [1029, 585], [1075, 585], [1075, 342], [1029, 342]], np.int32)
keys.append(Key('F1#', 'black', polygon, (60, 110, 0), midiNote=78))
polygon = np.array([[1094, 342], [1094, 585], [1139, 585], [1139, 342], [1094, 342]], np.int32)
keys.append(Key('G1#', 'black', polygon, (60, 110, 0), midiNote=80))
polygon = np.array([[1158, 342], [1158, 585], [1203, 585], [1203, 342], [1158, 342]], np.int32)
keys.append(Key('A1#', 'black', polygon, (60, 110, 0), midiNote=82))
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
    processedFrame = warpedImage.copy()

    # ---- Detect Hands
    if True:
        handLandmarkList1, handLandmarkList2 = detect_hands(frame)
        
        fingertipMask = np.zeros((imgHeight, imgWidth), np.uint8)   # black mask for fingertip
        fingertipObjects = []
        if handLandmarkList1:
            #print(handLandmarkList1[8])
            cv2.circle(fingertipMask, (handLandmarkList1[8][0], handLandmarkList1[8][1]), 3, (255,255,255), -1)   # draw fingertip on bitmask

            if handLandmarkList2:
                #print(handLandmarkList2[8])
                cv2.circle(fingertipMask, (handLandmarkList2[8][0], handLandmarkList2[8][1]), 3, (255,255,255), -1)   # draw fingertip on bitmask

            warpedFingertipBitmask = cv2.warpPerspective(fingertipMask, resultWarping, (imgWidth, imgHeight))    # warp fingertip bitmask
            warpedFingertipBitmask = do_morphology(warpedFingertipBitmask, medianBlur=True, opening=False, closing=True)
            #cv2.imshow('fingermask', warpedFingertipBitmask)

            # find fingertip in bitmask
            fingertipContour = find_contours(warpedFingertipBitmask)
            fingertipObjects = detect_objects(fingertipContour, processedFrame, warpedFingertipBitmask, 0, 3, (0,125,255), True, True)
    # ----

    # ---- Detect Objects
    if True:
        # copy frame and convert to hsv
        
        hsvFrame = cv2.cvtColor(warpedImage, cv2.COLOR_BGR2HSV)

        if False:
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
            objects = detect_objects(sortedContours, processedFrame, maskGreen, contourStart, contourEnd, (0,0,255), True, False)
            # ----

        if True:
            # ---- Blue
            maskBlue = get_HSVMask(hsvFrame, hsv_blue, hsvTreshold)
            maskBlue = do_morphology(maskBlue, medianBlur=True, opening=False, closing=True, dilation=True)
            # -- find contours
            sortedContours = find_contours(maskBlue)
            objects = detect_objects(sortedContours, processedFrame, maskBlue, contourStart, contourEnd, (0,0,255), True, True)
            # ----

        # --- bitmaps color
        #maskRed = make_Mask_colored(frame, maskRed)
        #maskGreen = make_Mask_colored(frame, maskGreen)
        #maskBlue = make_Mask_colored(frame, maskBlue)

        #colorMask = cv2.add(maskRed, cv2.add(maskGreen, maskBlue))
        colorMask = maskBlue
    # --------- 

    # ---- update Layout
    for n in range(0, len(layout)):
        layout[n].update(processedFrame, objects)
    # ----

    # ---- update Keys
    for n in range(0, len(keys)):
        keys[n].update(processedFrame, fingertipObjects)
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