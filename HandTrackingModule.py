import cv2
import mediapipe as mp
import time
import math


class handDetector():
    def __init__(self, mode = False, maxHands = 2, modelComplexity = 1, detectionConfidence = 0.5, trackConfidence = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionConfidence = detectionConfidence
        self.trakcConfidence = trackConfidence

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplexity, self.detectionConfidence, self.trakcConfidence)
        self.mpDraw = mp.solutions.drawing_utils

    
    def findHands(self, img, draw = True):

        
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        
        return img
    
    def findPosition(self, img, draw = False):

        lmList = []
        h1 = []
        h2 = []
        if self.results.multi_hand_landmarks:
            # myHand = self.results.multi_hand_landmarks[handNo]
            for handNo, myHand in enumerate(self.results.multi_hand_landmarks):

                for id, lm in enumerate(myHand.landmark):
                    # print(id, lm)
                    h, w, c = img.shape
                    cx, cy = int(lm.x*w), int(lm.y*h)
                    # print(id, cx, cy)
                    if handNo == 0:
                        h1.append([id, cx, cy])
                    else:
                        h2.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 10, (0, 247, 0), cv2.FILLED)
            lmList.append(h1)
            lmList.append(h2)
            
            # try except has been used to avoid an error when the hand initially comes into frame, not all fingers are visible at that instant
            # try:
            #     for h in lmList:
            #         max_x = max([x[1] for x in h])+30
            #         min_x = min([x[1] for x in h])-30
            #         max_y = max([y[2] for y in h])+30
            #         min_y = min([y[2] for y in h])-30

            #         # cv2.rectangle(img, (h[4][1], h[12][2]), (h[20][1], h[0][2]), (255, 100, 0), 2)
            #         cv2.rectangle(img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
            # except:
            #     pass
        
        return lmList
    
    # def findPointDistance(self, l1, l2):
    #     x1, y1 = l1
    #     x2, y2 = l2

    #     distance = math.hypot(x2-x1, y2-y1)
    #     return distance




def main():
    
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList):
            print(lmList)

        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime = cTime
        
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (255,0,255), 3)
        
        

        cv2.imshow("Image", img)
        cv2.waitKey(1)

    






if __name__ == "__main__":
    main()