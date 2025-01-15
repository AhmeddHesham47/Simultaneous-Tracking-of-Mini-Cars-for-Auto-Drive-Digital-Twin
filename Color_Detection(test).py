#For extracting hsv colors
import cvzone
from cvzone.ColorModule import ColorFinder
import cv2

cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)
#extract each HSV color you adjusted and then put in the "color_detection(main)"
myColorFinder = ColorFinder(True)

while True:
    success, img = cap.read()
    imgColor, mask = myColorFinder.update(img)

    imgStack = cvzone.stackImages([img,imgColor], 2, 0.5)
    cv2.imshow("Image", imgStack)
    cv2.waitKey(1)