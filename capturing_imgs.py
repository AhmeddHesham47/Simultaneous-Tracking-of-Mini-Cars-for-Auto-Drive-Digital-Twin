import cv2
import os


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Folder to save images
save_path = 'D:\Chess_images'
os.makedirs(save_path, exist_ok=True)

count = 1

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # Display the frame
    cv2.imshow('Camera', frame)
    
    # Wait for user to press 'x'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('x'):
        # Save the captured image
        filename = os.path.join(save_path, f'img{count}.jpg')
        cv2.imwrite(filename, frame)
        print(f'Image saved as {filename}')
        count += 1
    
    # Break the loop on 'q' key press
    if key == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()
