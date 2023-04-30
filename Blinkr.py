import cv2
import cvzone

from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import pyautogui
import pygame
import time

# initialize Pygame
pygame.init()

# load the image
image = pygame.image.load("loader.png")

# create the splash screen
splash = pygame.Surface((747, 497))
splash.fill((0, 46, 65))  # set background color
splash.blit(image, (0, 0))  # draw the image

# create the main window without borders
screen = pygame.display.set_mode((747, 497), pygame.NOFRAME)
screen.blit(splash, (0, 0))  # draw the splash screen on the main window
pygame.display.flip()  # update the display

# show the splash screen for a few seconds
time.sleep(5)

# close Pygame
pygame.quit()


cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=4)
plotY = LivePlot(640, 360, [20, 50], invert=True)

idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
ratioList = []
blinkCounter = 0
counter = 0
color = (255, 0, 255)
no_blink_time = 0  # initialize time since last blink to 0
notification_visible = False  # initialize notification as not visible

while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        face = faces[0]
        for id in idList:
            cv2.circle(img, face[id], 5,color, cv2.FILLED)

        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]
        lenghtVer, _ = detector.findDistance(leftUp, leftDown)
        lenghtHor, _ = detector.findDistance(leftLeft, leftRight)

        cv2.line(img, leftUp, leftDown, (0, 200, 0), 3)
        cv2.line(img, leftLeft, leftRight, (0, 200, 0), 3)

        ratio = int((lenghtVer / lenghtHor) * 100)
        ratioList.append(ratio)
        if len(ratioList) > 3:
            ratioList.pop(0)
        ratioAvg = sum(ratioList) / len(ratioList)

        if ratioAvg < 35 and counter == 0:
            blinkCounter += 1
            color = (0,200,0)
            counter = 1
            no_blink_time = 0  # reset time since last blink
            if notification_visible:
                cv2.destroyWindow("Notification")  # close the notification window
                notification_visible = False
        else:
            no_blink_time += 1  # increment time since last blink
            if no_blink_time > 75 and not notification_visible:  # 3.5 seconds have passed and notification is not already visible
                cv2.namedWindow("Notification", cv2.WINDOW_GUI_NORMAL )
                cv2.setWindowProperty("Notification", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.setWindowProperty("Notification", cv2.WND_PROP_TOPMOST, 1)  # make the window always stay on top
                
                cv2.resizeWindow("Notification", 200, 200)
                
                # Get screen dimensions
                screen_width, screen_height = pyautogui.size()

                # Calculate the window position to center it
                window_width, window_height = 250, 250
                window_x = int((screen_width - window_width) / 2)
                window_y = int((screen_height - window_height) / 2)

                # Move and show the window
                cv2.moveWindow("Notification", window_x, window_y)

                cv2.imshow("Notification", cv2.imread("notification.png")) 
                notification_visible = True


        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0
                color = (255,0, 255)

        cvzone.putTextRect(img, f'Blink Count: {blinkCounter}', (50, 100),
                           colorR=color)

        imgPlot = plotY.update(ratioAvg, color)
        img = cv2.resize(img, (640, 360))
        imgStack = cvzone.stackImages([img, imgPlot], 2, 1)
    else:
        img = cv2.resize(img, (640, 360))
        imgStack = cvzone.stackImages([img, img], 2, 1)

    cv2.imshow("Image", imgStack)
    cv2.waitKey(25)
