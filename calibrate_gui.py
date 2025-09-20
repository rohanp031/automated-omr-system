import cv2
import numpy as np
import sys
import os

# --- CONFIGURATION ---
# 1. Path to a sample OMR sheet image you want to calibrate
#    IMPORTANT: Replace this with a valid path to one of your OMR images
IMAGE_PATH = "omr_processing\Img7.jpeg" 


MAX_DISPLAY_DIMENSION = 800


OUTPUT_WIDTH = 800
OUTPUT_HEIGHT = 1000


# Global variables
points = []
image_display = None

def mouse_callback(event, x, y, flags, param):
    """Handles mouse clicks to capture the four corner points."""
    global points, image_display

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            # Draw a circle on the clicked point
            cv2.circle(image_display, (x, y), 10, (0, 255, 0), -1)
            cv2.putText(image_display, f"{len(points)}", (x+15, y+15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imshow("OMR Calibration Tool", image_display)
            print(f"Point {len(points)} captured: ({x}, {y})")

def main():
    global image_display, points

    # Load the image
    image = cv2.imread(IMAGE_PATH)
    if image is None:
        print(f"FATAL ERROR: Could not load image from '{IMAGE_PATH}'")
        print("Please update the IMAGE_PATH variable in this script.")
        return

    # Resize for better display if the image is too large
    h, w = image.shape[:2]
    if h > MAX_DISPLAY_DIMENSION or w > MAX_DISPLAY_DIMENSION:
        scale = MAX_DISPLAY_DIMENSION / max(h, w)
        image = cv2.resize(image, (int(w*scale), int(h*scale)))
    
    image_display = image.copy()
    
    # Setup window and mouse callback
    cv2.namedWindow("OMR Calibration Tool")
    cv2.setMouseCallback("OMR Calibration Tool", mouse_callback)

    # Instructions
    print("\n--- OMR Calibration Tool ---")
    print("Instructions:")
    print("1. Click on the FOUR corners of the MAIN ANSWER GRID.")
    print("2. Order of clicks: Top-Left -> Top-Right -> Bottom-Right -> Bottom-Left.")
    print("3. After clicking the 4th point, a warped 'top-down' view will be shown.")
    print("4. Press 's' to save the coordinates and exit.")
    print("5. Press 'r' to restart the selection process.")
    print("6. Press 'q' to quit without saving.")
    print("\nWaiting for points...")

    while True:
        cv2.imshow("OMR Calibration Tool", image_display)
        key = cv2.waitKey(1) & 0xFF

        if len(points) == 4:
            # When 4 points are selected, show the warped preview
            try:
                # Get original image dimensions for scaling back
                orig_h, orig_w = cv2.imread(IMAGE_PATH).shape[:2]
                scale_factor = orig_w / image.shape[1]
                
                # Scale points back to original image size
                scaled_points = np.array(points, dtype="float32") * scale_factor
                
                # Define destination points
                dst_points = np.array([
                    [0, 0],
                    [OUTPUT_WIDTH - 1, 0],
                    [OUTPUT_WIDTH - 1, OUTPUT_HEIGHT - 1],
                    [0, OUTPUT_HEIGHT - 1]], dtype="float32")

                # Get the perspective transform matrix and warp the image
                matrix = cv2.getPerspectiveTransform(scaled_points, dst_points)
                original_full_image = cv2.imread(IMAGE_PATH)
                warped_preview = cv2.warpPerspective(original_full_image, matrix, (OUTPUT_WIDTH, OUTPUT_HEIGHT))
                
                cv2.imshow("Warped Preview", warped_preview)

            except Exception as e:
                print(f"Could not generate warped preview: {e}")

        # Handle key presses
        if key == ord('q'):
            break
        elif key == ord('r'):
            print("Resetting points. Please select 4 corners again.")
            points = []
            image_display = image.copy()
            if cv2.getWindowProperty("Warped Preview", 0) >= 0:
                 cv2.destroyWindow("Warped Preview")
        elif key == ord('s') and len(points) == 4:
            print("\n--- COORDINATES CAPTURED ---")
            print("Copy the following line and paste it into 'omr_processing/processor.py',")
            print("replacing the existing 'self.calibration_points' line:\n")
            
            orig_h, orig_w = cv2.imread(IMAGE_PATH).shape[:2]
            scale_factor = orig_w / image.shape[1]
            scaled_points = (np.array(points) * scale_factor).astype(int)

            print(f"self.calibration_points = np.array({scaled_points.tolist()})")
            print("\nCalibration complete. Exiting.")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    if "path/to/your" in IMAGE_PATH:
         print("ERROR: You have not set the IMAGE_PATH variable yet.")
         print("Please open 'calibrate_gui.py' and set the path to your sample OMR sheet.")
    elif not os.path.exists(IMAGE_PATH):
        print(f"ERROR: The file '{IMAGE_PATH}' does not exist.")
        print("Please check the IMAGE_PATH variable at the top of the 'calibrate_gui.py' script.")
    else:
        main()