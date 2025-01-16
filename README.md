# Simultaneous-Tracking-of-Mini-Cars-for-Auto-Drive-Digital-Twin
That is a description of each file for the project:

1) " Color_Detection(test) " : Script used to extract the HSV (Hue, Saturation, Value) color space from images to isolate specific colors to be used in " Color_Detection(main) ".

2) " Color_Detection(main) ": Main script for color and shape detction .

3) " AprilTag " : Main script for AprilTag detection ONLY .

4) " AprilTag_with_EKF " : Main script for AprilTag detection with an Extended Kalman Filter (EKF) " EKF "  .

5) " EKF ": The Extended Kalman Filter to be used with " AprilTag_with_EKF " 

6) " CarMovement " : Unity script for cars movement in Unity . 

7) " UDPReceive " : A UDP receiver is used to collect real-time data from a Python script.
   
8) " Chess " : A chessboard pattern is generated to facilitate camera calibration, ensuring precise mapping of the physical world to the digital environment without distortions.

9) " capturing imgs " : Responsible for capturing images from the camera.

10) " camera_calibration " : Script uses the captured chessboard images to generate matrices that correct distortions in the camera feed.





