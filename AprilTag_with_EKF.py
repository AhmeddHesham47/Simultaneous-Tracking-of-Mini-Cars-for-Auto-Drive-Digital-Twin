import cv2
import socket
import numpy as np
from pupil_apriltags import Detector
from EKF import ExtendedKalmanFilter

class AprilTagTracker:
    def __init__(self):
        # Initialize video capture
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(3, 640)  # Set frame width
        self.cap.set(4, 480)  # Set frame height
        
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
        
        # Initialize Kalman filter
        self.kalman = ExtendedKalmanFilter(dt=1/70)
        
        # Store previous tag positions and angles
        self.prev_positions = {}
        self.prev_angles = {}

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

        # Convert frame to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect AprilTags
        results = self.detector.detect(gray)
        
        # Track detected tags
        current_tags = set([r.tag_id for r in results])

        for r in results:
            tag_id = r.tag_id
            center = r.center
            corners = r.corners.astype(int)

            # Calculate angle of tag
            top_left = corners[0]
            top_right = corners[1]
            angle = np.arctan2(top_right[1] - top_left[1], top_right[0] - top_left[0])
            angle_degrees = self.normalize_angle(np.degrees(angle))

            cX, cY = int(center[0]), int(center[1])

            # Apply Kalman filter to smooth position and orientation
            measurement = np.array([cX, cY, angle_degrees])
            filtered_state = self.kalman.predict_and_update(tag_id, np.array(measurement))
            self.prev_positions[tag_id] = (filtered_state[0], filtered_state[1])
            self.prev_angles[tag_id] = filtered_state[2]

            # Prepare and send data to UNITY and ESP32
            img_height, img_width = img.shape[:2]
            data = f"{tag_id},{img_width - int(filtered_state[0])},{img_height - int(filtered_state[1])},{int(filtered_state[2])}"
            self.sock1.sendto(data.encode(), self.server_address1)
            self.sock2.sendto(data.encode(), self.server_address2)
            
            # Draw bounding box around detected tag
            cv2.polylines(img, [corners.reshape((-1, 1, 2))], True, (0, 255, 0), 2)
        
        # Remove undetected tags from tracking
        for tag_id in list(self.prev_positions.keys()):
            if tag_id not in current_tags:
                del self.prev_positions[tag_id]
                del self.prev_angles[tag_id]

        # Display frame
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
