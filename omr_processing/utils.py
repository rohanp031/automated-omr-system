import cv2
import numpy as np

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at path: {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    return image, gray, edged

def find_fiducial_markers(gray_image):
    """
    Finds the four black square fiducial markers at the corners of the answer grid.
    These markers are more reliable for perspective correction than the page contour.
    """
    # Threshold the image to get only black squares
    thresh = cv2.threshold(gray_image, 120, 255, cv2.THRESH_BINARY_INV)[1]

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    marker_contours = []
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        
        # Markers should be roughly square and have 4 corners
        if len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            
            # Filter by aspect ratio and a reasonable area to find squares
            if 0.9 <= aspect_ratio <= 1.1 and cv2.contourArea(c) > 100:
                marker_contours.append(approx)

    # We expect exactly 4 markers
    if len(marker_contours) == 4:
        # Sort contours by their y-coordinate
        marker_contours = sorted(marker_contours, key=lambda c: cv2.boundingRect(c)[1])
        
        # Top two and bottom two
        top_two = sorted(marker_contours[:2], key=lambda c: cv2.boundingRect(c)[0])
        bottom_two = sorted(marker_contours[2:], key=lambda c: cv2.boundingRect(c)[0])
        
        # Return in order: top-left, top-right, bottom-right, bottom-left
        return np.array([top_two[0], top_two[1], bottom_two[1], bottom_two[0]], dtype="int32")
        
    return None

def apply_perspective_transform(image, pts, width=800, height=1000):
    rect = pts.reshape(4, 2).astype("float32")
    
    # The destination points for the transform
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]], dtype="float32")

    # Compute the perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (width, height))
    return warped

def sort_contours(cnts, method="left-to-right"):
    reverse = False
    i = 0
    if method in ["right-to-left", "bottom-to-top"]:
        reverse = True
    if method in ["top-to-bottom", "bottom-to-top"]:
        i = 1
        
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
        key=lambda b: b[1][i], reverse=reverse))
    
    return cnts, boundingBoxes