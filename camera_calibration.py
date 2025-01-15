import numpy as np
import cv2
import glob
import os

class CameraCalibration:
    def __init__(self, checkerboard_size=(8,5), square_size=0.025):
        
        self.checkerboard_size = checkerboard_size
        self.square_size = square_size
        
        # Calibration storage
        self.camera_matrix = None
        self.dist_coefficients = None
        self.reprojection_error = None

    def calibrate(self, images_folder):
        
        # Prepare object points
        objp = np.zeros((self.checkerboard_size[0] * self.checkerboard_size[1], 3), np.float32)
        objp[:,:2] = np.mgrid[0:self.checkerboard_size[0], 0:self.checkerboard_size[1]].T.reshape(-1,2)
        objp = objp * self.square_size

        # Arrays to store object points and image points
        objpoints = []  # 3d points in real world space
        imgpoints = []  # 2d points in image plane

        # Get list of calibration images with multiple extensions
        image_extensions = ['*.jpg', '*.png', '*.jpeg', '*.tif']
        images = []
        for ext in image_extensions:
            images.extend(glob.glob(os.path.join(images_folder, ext)))
        
        print(f"Number of images loaded: {len(images)}")  # Debug statement
        
        if not images:
            raise ValueError(f"No calibration images found in {images_folder}")

        for fname in images:
            try:
                # Read image in grayscale
                img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
                
                if img is None:
                    print(f"Error loading image: {fname}")
                    continue

                # Find chessboard corners
                ret, corners = cv2.findChessboardCorners(img, self.checkerboard_size, None)

                # If corners found, add object points and image points
                if ret:
                    objpoints.append(objp)
                    imgpoints.append(corners)

                    # Optional: Draw and display corners
                    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    cv2.drawChessboardCorners(img_color, self.checkerboard_size, corners, ret)
                    cv2.imshow('Chessboard Corners', img_color)
                    cv2.waitKey(500)
                else:
                    print(f"No chessboard corners found in {fname}")

            except Exception as e:
                print(f"Error processing {fname}: {e}")

        # Ensure we have valid points
        if len(objpoints) == 0 or len(imgpoints) == 0:
            raise ValueError("No valid calibration images found. Check your images and checkerboard size.")

        # Calibrate camera
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, img.shape[::-1], None, None
        )

        # Calculate reprojection error
        total_error = 0
        for i in range(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(
                objpoints[i], rvecs[i], tvecs[i], 
                camera_matrix, dist_coeffs
            )
            error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            total_error += error

        # Store calibration results
        self.camera_matrix = camera_matrix
        self.dist_coefficients = dist_coeffs
        self.reprojection_error = total_error / len(objpoints)

        # Close windows
        cv2.destroyAllWindows()

        return {
            'camera_matrix': self.camera_matrix,
            'dist_coefficients': self.dist_coefficients,
            'reprojection_error': self.reprojection_error
        }

    def undistort_image(self, image):
        
        if self.camera_matrix is None:
            raise ValueError("Calibration not performed. Run calibrate() first.")
        
        return cv2.undistort(
            image, 
            self.camera_matrix, 
            self.dist_coefficients
        )

    def save_calibration(self, output_file='camera_calibration.npz'):
        
        np.savez(
            output_file, 
            camera_matrix=self.camera_matrix, 
            dist_coefficients=self.dist_coefficients
        )

    def load_calibration(self, calibration_file='camera_calibration.npz'):
        
        calibration = np.load(calibration_file)
        self.camera_matrix = calibration['camera_matrix']
        self.dist_coefficients = calibration['dist_coefficients']

# Example usage
def main():
    # Initialize calibration
    calibrator = CameraCalibration(
        checkerboard_size=(8,5),  # Adjust based on your chessboard
        square_size=0.025 # 3.7 cm in meters
    )

    # Perform calibration
    try:
        # Replace with the actual path to your calibration images
        img_paths = 'D:\Chess_images'
        results = calibrator.calibrate(img_paths)
        
        # Print calibration results
        print("Camera Matrix:")
        print(results['camera_matrix'])
        print("\nDistortion Coefficients:")
        print(results['dist_coefficients'])
        print(f"\nReprojection Error: {results['reprojection_error']}")

        # Save calibration
        calibrator.save_calibration()

    except Exception as e:
        print(f"Calibration failed: {e}")

if __name__ == '__main__':
    main()