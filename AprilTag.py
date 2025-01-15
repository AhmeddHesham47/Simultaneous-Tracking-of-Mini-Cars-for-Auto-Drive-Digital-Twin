import cv2
import socket
import numpy as np
from pupil_apriltags import Detector

class AprilTagTracker:
    def __init__(self):
        # Initialize video capture
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(3, 640)  
        self.cap.set(4, 480)  
        
        # IP Address and Port Number UNITY
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address1 = ("127.0.0.1", 5053)
         
        # IP Address and Port Number ESP32
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address2 = ("192.168.1.1", 5054)
        
        # Camera matrix and distortion coefficients
        self.camera_matrix = np.array([[644.76561694, 0, 331.26266442],
                                       [0, 645.89528116, 215.92835909],
                                       [0, 0, 1]])
        self.dist_coeffs = np.array([0.06830215, -0.14315368, -0.01151178, 0.00780322, 0.03096726])

        # Create AprilTag detector
        self.detector = Detector(
            families='tag36h11',
            nthreads=5,
            quad_decimate=0.6,
            quad_sigma=0.5,
            refine_edges=1,
            decode_sharpening=0.0,
            debug=0
        )

    def normalize_angle(self, angle):
        return angle % 360

    def process_frame(self):
        success, img = self.cap.read()
        if not success:
            return False

        # Undistort the image
        img = cv2.undistort(img, self.camera_matrix, self.dist_coeffs)

        img_height, img_width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        results = self.detector.detect(gray)

        for r in results:
            tag_id = r.tag_id
            center = r.center
            corners = r.corners.astype(int)

            # Calculate angle
            top_left = corners[0]
            top_right = corners[1]
            angle = np.arctan2(top_right[1] - top_left[1], 
                               top_right[0] - top_left[0])
            angle_degrees = self.normalize_angle(np.degrees(angle))

            cX, cY = int(center[0]), int(center[1])

            # Data sent to UNITY
            data = f"{tag_id},{cX},{img_height-cY},{int(angle_degrees)}"
            self.sock1.sendto(data.encode(), self.server_address1)
            
            # Data sent to ESP32
            self.sock2.sendto(data1.encode(), self.server_address2)
            
            # Draw tag outline
            cv2.polylines(img, [corners.reshape((-1, 1, 2))], True, (255, 0, 0), 2)

            # Display tag ID
            cv2.putText(img, f"{tag_id}", (cX - 15, cY - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow("AprilTag Detection", img)
        return True

    def run(self):
        while True:
            if not self.process_frame():
                break
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
     # Release resources and close sockets
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.sock1.close()
        self.sock2.close()

if __name__ == "__main__":
    tracker = AprilTagTracker()
    tracker.run()
