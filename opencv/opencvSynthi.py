import cv2
import numpy as np

imgWidth = 1280
imgHeight = 720

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, imgWidth)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, imgHeight)

#cap = cv2.VideoCapture('opencvTest.mp4')


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
        self.position = (cx, cy)
        self.size = (width, heigth)
        self.color = colorRGB
        self.note = midiNote

        self.calcRectPoints()
    
    # #### Getter
    def getName(self):
        print("LayoutName: ", self.function)

    # #### Setter


    # #########
    # ######### Functions
    # ## main func
    def update(self, imageToDrawOn, objects):
        self.draw(imageToDrawOn)
        self.checkCollision(imageToDrawOn, objects)
        #self.playmidi()

    # ## init
    def calcRectPoints(self):
        self.p_ul = np.array((self.position[0] - self.size[0]/2, self.position[1] - self.size[1]/2), dtype='int')
        self.p_ur = np.array((self.position[0] + self.size[0]/2, self.position[1] - self.size[1]/2), dtype='int')
        self.p_bl = np.array((self.position[0] - self.size[0]/2, self.position[1] + self.size[1]/2), dtype='int')
        self.p_br = np.array((self.position[0] + self.size[0]/2, self.position[1] + self.size[1]/2), dtype='int')

    # ## all functions
    def draw(self, frame):
        cv2.rectangle(frame, self.p_ur, self.p_bl, self.color, 2)
        return

    def checkCollision(self, frame, objects):
        #tresh = 50
        for centerX, centerY in objects:
            if (centerX <= self.position[0] + self.size[0]/2 and centerX >= self.position[0] - self.size[0]/2) and (centerY <= self.position[1] + self.size[1]/2 and centerY >= self.position[1] - self.size[1]/2):
                # in rectangle area / colission detected
                #cv2.rectangle(processedFrame, rect_p1+(2,2), rect_p2-(2,2), (0,255,0), 2)
                if self.type == 'button':
                    self.pressed = True
                    cv2.rectangle(frame, self.p_ur+(2,2), self.p_bl-(2,2), (0,255,255), 2)
                    print(self.name, ': pressed',)
                if self.type == 'faderH':
                    # get value
                    value = centerX - (self.position[0] - self.size[0]/2)
                    value = value / (self.size[0]) * 100
                    self.value = value
                    # draw visual feedback
                    cv2.rectangle(frame, self.p_ur+(2,2), self.p_bl-(2,2), (0,255,255), 2)
                    cv2.line(frame,np.int16((centerX, self.position[1]+self.size[1]/2)), np.int16((centerX, self.position[1]-self.size[1]/2)), (0,0,0), 3)
                    cv2.putText(frame, str(np.round(self.value, 1)), np.int16((centerX + 5, self.position[1]+self.size[1]/2 -10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
                    # print in console
                    print(self.name, ' = ', self.value)
                if self.type == 'faderV':
                    # get value
                    value = centerY - (self.position[1] - self.size[1]/2)
                    value = value / (self.size[1]) * 100
                    self.value = value
                    # draw visual feedback
                    cv2.rectangle(frame, self.p_ur+(2,2), self.p_bl-(2,2), (0,255,255), 2)
                    cv2.line(frame,np.int16((self.position[0]-self.size[0]/2, centerY)), np.int16((self.position[0]+self.size[0]/2, centerY)), (0,0,0), 3)
                    cv2.putText(frame, str(np.round(self.value, 1)), np.int16((self.position[0]-self.size[0]/2, centerY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
                    # print in console
                    print(self.name, ' = ', self.value)
        

    def playMidi():
        return

# -----


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

def detect_objects(sortedContours, drawToFrame, mask, start, stop, color=(255,0,255), boundingRect=True, contourToMask=False):
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

# --- -Points for warping
inPoint1 = [0, 100]
inPoint2 = [700, 260]
inPoint3 = [0, 700]
inPoint4 = [700, 400]

outPoint1 = [31, 31]
outPoint2 = [1245, 71]
outPoint3 = [31, 692]
outPoint4 = [1245, 692]

points1_tuple = np.float32([inPoint1, inPoint2, inPoint3, inPoint4])
points2_tuple = np.float32([outPoint1, outPoint2, outPoint3, outPoint4])
# ----

layout = []
# --- set up Layout
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
#Oszi1
layout.append(Layout('Volume', 'faderH', 584, 107, 420, 73, (205,100,205), 'note'))
layout.append(Layout('LFO', 'faderH', 584, 180, 420, 73, (205,100,205), 'note'))
layout.append(Layout('Sinus', 'button', 427, 266, 105, 100, (205,100,205), 'note'))
layout.append(Layout('Triangle', 'button', 532, 266, 105, 100, (205,100,205), 'note'))
layout.append(Layout('Sawtooth', 'button', 637, 266, 105, 100, (205,100,205), 'note'))
layout.append(Layout('Rectangle', 'button', 742,266, 105, 100, (205,100,205), 'note'))
#Oszi2
layout.append(Layout('Volume', 'faderH', 1035, 107, 420, 73, (205,100,100), 'note'))
layout.append(Layout('LFO', 'faderH', 1035, 180, 420, 73, (205,100,100), 'note'))
layout.append(Layout('Sinus', 'button', 878, 266, 105, 100, (205,100,100), 'note'))
layout.append(Layout('Triangle', 'button', 983, 266, 105, 100, (205,100,100), 'note'))
layout.append(Layout('Sawtooth', 'button', 1088, 266, 105, 100, (205,100,100), 'note'))
layout.append(Layout('Rectangle', 'button', 1193,266, 105, 100, (205,100,100), 'note'))

# ---


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

    #outPoint1 = [rect_cX - rect_w/2 , rect_cY - rect_h/2]
    #outPoint2 = [rect_cX + rect_w/2 , rect_cY - rect_h/2]
    #outPoint3 = [rect_cX - rect_w/2 , rect_cY + rect_h/2]
    #outPoint4 = [rect_cX + rect_w/2 , rect_cY + rect_h/2]

    # ---- 


    # ---- Warping
    if True:
        points1_tuple = np.float32([inPoint1, inPoint2, inPoint3, inPoint4])
        #points2_tuple = np.float32([outPoint1, outPoint2, outPoint3, outPoint4])

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

    # --------- Detect Objects
    if True:
        # how many contours to take
        contourStart = 1
        contourEnd = 3

        processedFrame = warpedImage.copy()
        hsvFrame = cv2.cvtColor(warpedImage, cv2.COLOR_BGR2HSV)   # convert to hsv

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

    # --------- colission detection
    if False:
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
    #cv2.imshow('mask', colorMask)

    # ---- waitkey
    if cv2.waitKey(25) & 0xFF == 27:   # when escap is pressed
        print("break")
        break


cap.release()
cv2.destroyAllWindows()