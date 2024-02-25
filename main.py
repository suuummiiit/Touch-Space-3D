from ursina import *
import cv2
import HandTrackingModule as htm
import math
import time


# Variables ---------------------------------
pTime, cTime = 0, 0

global lCatch, rCatch
lCatch, rCatch = False, False

p_angle, rot_z = 0, 0
pPos_x, pPos_y = 0, 0
rot_x, rot_y = 0, 0
#--------------------------------------------

# Ursina ------------------------------------
app = Ursina()
# window.size = window.fullscreen_size
# window.position = Vec2(0, 0)

rotation_resetter = Entity()
cube = Entity(parent=rotation_resetter, model='Assets/Block.obj', texture = load_texture('Assets/grass.png'))
# -------------------------------------------
# Open CV ------------------------------------
# OpenCV setup
wCam, hCam = 1280, 720
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use webcam at index 0
cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)

detector = htm.handDetector(detectionConfidence=0.8, maxHands=2)
# --------------------------------------------
# functions ------------------------------------------------------------

def fingersUp(list):
    fingers = []
    ind = [8,12,16,20]
    x1,y1 = list[4][1], list[4][2]
    x2,y2 = list[2][1], list[2][2]
    x3,y3 = list[13][1], list[13][2]
    d1 = math.hypot(x1-x2, y1-y2)
    d2 = math.hypot(x1-x3, y1-y3)
    if d2 < d1:
        fingers.append(0)
    else:
        fingers.append(1)
    for i in ind:
        if list[i][2] < list[i-2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return(fingers)



def findDistance(l1, l2):
    x1, y1 = l1[1:]
    x2, y2 = l2[1:]

    distance = math.hypot(x2-x1, y2-y1)
    return distance

def catch(list):
    finger_tips = [8, 12, 16, 20]
    counter = 0
    for tip in finger_tips:
        # if findDistance(rh[tip], rh[tip-2]) < findDistance(rh[tip-1], rh[tip-2])*1.7 and rh[tip][2] < rh[tip-2][2]:
        if findDistance(list[tip], list[tip-3]) > findDistance(list[tip], list[tip-2]):
            counter += 1
    if counter > 2  and (fingersUp(list) != [0,0,0,0,0] and fingersUp(list) != [1,0,0,0,0]):
        return True
    else:
        return False



def detect_hand(img, lmlist):
    lh, rh = [], []
    # Detectiing Hands  -------------------------------------------------
    for hand in lmlist:
        if hand == []:
            continue;
        max_x = max([x[1] for x in hand])+30
        min_x = min([x[1] for x in hand])-30
        max_y = max([y[2] for y in hand])+30
        min_y = min([y[2] for y in hand])-30

        dist = findDistance(hand[5], hand[17])
        if dist >= 100:
            cv2.rectangle(img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
            cv2.rectangle(img, (min_x-1, min_y-40), (min_x+200, min_y), (0, 255, 0), -1)

            if hand[5][1] < hand[17][1]: # Right Hand ---------------------------------------
                # print("Right")
                cv2.putText(img, "Right Hand", (min_x, min_y-10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                hand.append(min_x)
                hand.append(min_y)
                hand.append(max_x)
                hand.append(max_y)
                rh = hand


            elif hand[5][1] > hand[17][1]: # Left Hand ---------------------------------------
                # print("Left")
                cv2.putText(img, "Left Hand", (min_x, min_y-10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                hand.append(min_x)
                hand.append(min_y)
                hand.append(max_x)
                hand.append(max_y)
                lh = hand


    return img, lh, rh



# Control Functions ---------------------------------

def rotate_z(img, rh):
    global rot_z, p_angle
    cv2.circle(img, (rh[23]+20, rh[22]+20), 15, (0, 255, 0), cv2.FILLED)
    a = rh[9][1:]
    b = rh[0][1:]
    y = (a[1]-b[1])
    x = (a[0]-b[0])
    if x == 0:
        angle = 90
    else:
        angle = math.degrees(math.atan(y/x))
        angle = float(f"{angle:.2f}")
        # angle = int(angle)
        if angle < 0 and x > 0:
            angle = 180 + angle
    cv2.putText(img, f"Angle : {angle}", (20, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    if p_angle == 0:
        p_angle = angle
        rot_z = 0
    else:
        rot_z = angle - p_angle
        rot_z = float(f"{rot_z:.2f}")
        if rot_z > -2 and rot_z < 2:
            rot_z = 0
        elif rot_z > 30 or rot_z < -30:
            rot_z = (rot_z/abs(rot_z))*10
        p_angle = angle
        cv2.putText(img, f"rot_z : {rot_z}", (20, 150), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    return img

def rotate_x(img, rh):
    global pPos_y, rot_x
    
    cPos_y = rh[9][2]
    if pPos_y == 0:
        pPos_y = cPos_y
        rot_x = 0
    else:
        diff = cPos_y - pPos_y
        if diff < 3 and diff > -3:
            rot_x = 0
        elif diff < -3:
            rot_x = 5
        elif diff > 3:
            rot_x = -5
        elif diff < -20:
            rot_x = 10
        elif diff > 20:
            rot_x = -10
        
        pPos_y = cPos_y

    return img

def rotate_y(img, rh):
    global pPos_x, rot_y
    
    cPos_x = rh[9][1]
    if pPos_x == 0:
        pPos_x = cPos_x
        rot_y = 0
    else:
        diff = cPos_x - pPos_x
        if diff < 3 and diff > -3:
            rot_y = 0
        elif diff < -3:
            rot_y = 5
        elif diff > 3:
            rot_y = -5
        elif diff < -20:
            rot_y = 10
        elif diff > 20:
            rot_y = -10

        pPos_x = cPos_x

    return img



# Main loop --------------------------------------------------------
def update():

    # Global Variables --------------------------------------
    global lCatch, rCatch, pTime, cTime
    global p_angle, rot_z, rot_x, rot_y
    # ----------------------------------------------------------

    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Detect hands and get landmarks
    img = detector.findHands(img)
    lmlist = detector.findPosition(img)
    
    

    if lmlist:

        try:
            # detecting left and right hands ------------------------------
            img, lh, rh = detect_hand(img, lmlist)
            # print(len(lh))
            # print(len(rh))

            if lh: # Detecting catch for left hand
                lCatch = catch(lh)
                # print(lCatch)
                lmin_x = lh[21]
                lmin_y = lh[22]
                lmax_x = lh[23]
                lmax_y = lh[24]
                if lCatch:
                    cv2.circle(img, (lmin_x-20, lmin_y+20), 15, (0, 255, 0), cv2.FILLED)
                else:
                    cv2.circle(img, (lmin_x-20, lmin_y+20), 15, (0, 0, 255), cv2.FILLED)
                    cv2.circle(img, (lmin_x-20, lmin_y+20), 15, (255, 255, 255), 2)

            if rh: # Detecting catch for right hand
                rCatch = catch(rh)
                # print(rCatch)
                rmin_x =rh[21]
                rmin_y =rh[22]
                rmax_x =rh[23]
                rmax_y =rh[24]
                if rCatch:
                    cv2.circle(img, (rmax_x+20, rmin_y+20), 15, (0, 255, 0), cv2.FILLED)
                else:
                    cv2.circle(img, (rmax_x+20, rmin_y+20), 15, (0, 0, 255), cv2.FILLED)
                    cv2.circle(img, (rmax_x+20, rmin_y+20), 15, (255, 255, 255), 2)


            

            # Rotation on z axis --------------------------------------
            if (rh and rCatch) and not lh:
                img = rotate_z(img, rh)

            # Rotation on X and Y axis --------------------------------------
            elif (lh and rh) and (fingersUp(lh) == [0, 0, 0, 0, 0] or fingersUp(lh) == [1, 0, 0, 0, 0]) and (rCatch and not lCatch):
                img = rotate_x(img, rh)
                img = rotate_y(img, rh)


            # elif (lh and rh and lCatch and rCatch):




            if (fingersUp(lh) == [0, 1, 0, 0, 0] and fingersUp(rh) == [0, 1, 0, 0, 0]):
                rot_x, rot_y, rot_z = 0, 0, 0
        except:
            pass

























    rotation_resetter.rotation_x += 20 * rot_x * time.dt
    rotation_resetter.rotation_y += 20 * rot_y * time.dt
    rotation_resetter.rotation_z += 20 * rot_z * time.dt

    cube.rotation = cube.world_rotation
    rotation_resetter.rotation = (0,0,0)


    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    fps = f"FPS: {int(fps)}"
    cv2.putText(img, fps, (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 100, 255), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)



EditorCamera()
app.run()
