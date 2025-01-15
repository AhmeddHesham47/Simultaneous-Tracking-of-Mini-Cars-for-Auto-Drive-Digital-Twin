import cvzone
from cvzone.ColorModule import ColorFinder
import cv2
import socket
import numpy as np

# Initialize video capture from the usb webcam
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height
success, img = cap.read()

# Store image dimensions
img_height, img_width, _ = img.shape  

# Initialize socket communication for Unity
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address1 = ("127.0.0.1", 5053)

# Initialize socket communication for ESP32
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address2 = ("192.168.1.1", 5054)

# Define camera matrix and distortion coefficients
camera_matrix = np.array([[644.76561694, 0, 331.26266442],
                           [0, 645.89528116, 215.92835909],
                           [0, 0, 1]])
dist_coeffs = np.array([0.06830215, -0.14315368, -0.01151178, 0.00780322, 0.03096726])


# Initialize color finder object
myColorFinder = ColorFinder(False)

# Define HSV color ranges for different objects
hsvVals1 = {'hmin': 15, 'smin': 37, 'vmin': 165, 'hmax': 72, 'smax': 114, 'vmax': 215}
hsvVals2 = {'hmin': 108, 'smin': 17, 'vmin': 101, 'hmax': 123, 'smax': 116, 'vmax': 219}
hsvVals3 = {'hmin': 82, 'smin': 173, 'vmin': 131, 'hmax': 105, 'smax': 255, 'vmax': 187}
hsvVals4 = {'hmin': 0, 'smin': 18, 'vmin': 148, 'hmax': 15, 'smax': 177, 'vmax': 174}

   # Detect shape based on contour approximation
def detect_shape(c):

    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    sides = len(approx)

    if sides == 3:
        return "1"  # Triangle
    elif sides == 4:
        return "2"  # Quadrilateral
    elif sides == 5:
        return "3"  # Pentagon
    elif sides == 6:
        return "4"  # Hexagon
    return "Not Defined"

# Main loop for real-time processing
while True:
    success, img = cap.read()
    if not success:
        break
    # Undistort image using the camera matrix and distortion coefficients 
    img = cv2.undistort(img, camera_matrix, dist_coeffs)
    imgContour = img.copy()  # Copy image for contour processing
    
    # Process each color-defined group
    grouped_cars = [
        (myColorFinder.update(img, hsvVals1)[1], "1"),
        (myColorFinder.update(img, hsvVals2)[1], "2"),
        (myColorFinder.update(img, hsvVals3)[1], "3"),
        (myColorFinder.update(img, hsvVals4)[1], "4")
    ]

    for mask, shapeType in grouped_cars:
        imgContour, contours = cvzone.findContours(imgContour, mask)

        # Process each detected contour
        for contour in contours:
            detected_shape = detect_shape(contour['cnt'])
            
            # Display detected shape only if it matches the expected type
            if detected_shape == shapeType:
                x, y = contour['center']
                cv2.putText(imgContour, shapeType, (x - 50, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                print(f"Detected: {shapeType}")
                
                # Calculate object orientation using fitEllipse
                ellipse = cv2.fitEllipse(contour['cnt'])
                angle = ellipse[2]
                if angle < 0:
                    angle += 360  # Normalize angle to range [0, 360]
                
                # Format data for Unity communication
                data = f"{shapeType},{img_width - contour['center'][0]},{img_height - contour['center'][1]},{int(angle)}"

                sock1.sendto(data.encode(),server_address1)
                # Data sent to ESP32
                sock2.sendto(data.encode(),server_address2)


    # Display processed contours
    cv2.imshow("Color and Shape Detection", imgContour)
    
    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup resources
cap.release()
cv2.destroyAllWindows()
