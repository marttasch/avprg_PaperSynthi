from cvzone.HandTrackingModule import HandDetector
import cv2
import matplotlib.path as mpltPath
import numpy as np

polygon = np.array([[10, 10], [10, 100], [30, 100], [30, 50], [20, 50], [20, 10], [10, 10]], np.int32)
pts = polygon.reshape((-1,1,2))

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=2)
while True:
    # Get image frame
    success, img = cap.read()
    
    img = cv2.flip(img, 1)   # flip horizontally
    
    # Find the hand and its landmarks
    hands, img = detector.findHands(img)  # with draw
    #hands = detector.findHands(img, draw=False)  # without draw


    if hands:
        # Hand 1
        hand1 = hands[0]
        lmList1 = hand1["lmList"]  # List of 21 Landmark points
        bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
        centerPoint1 = hand1['center']  # center of the hand cx,cy
        handType1 = hand1["type"]  # Handtype Left or Right

        fingers1 = detector.fingersUp(hand1)

        if len(hands) == 2:
            # Hand 2
            hand2 = hands[1]
            lmList2 = hand2["lmList"]  # List of 21 Landmark points
            bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
            centerPoint2 = hand2['center']  # center of the hand cx,cy
            handType2 = hand2["type"]  # Hand Type "Left" or "Right"

            fingers2 = detector.fingersUp(hand2)

            # Find Distance between two Landmarks. Could be same hand or different hands
            length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)  # with draw
            # length, info = detector.findDistance(lmList1[8], lmList2[8])  # with draw

        # colission detection
        if lmList1:
            fingerXY = np.array([lmList1[8][0], lmList1[8][1]]).reshape(1, 2)
            path = mpltPath.Path(polygon)
            print('finger point: ', fingerXY)
            inside = path.contains_points(fingerXY)
            if inside:
                cv2.polylines(img, [pts], isClosed=False, color=(255, 0, 0), thickness=2)
                print(inside)
            else:
                cv2.polylines(img, [pts], isClosed=False, color=(0, 255, 255), thickness=2)

    
        

    
    # Display
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()