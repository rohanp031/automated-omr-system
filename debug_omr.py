import cv2
import numpy as np
import os
import shutil
from omr_processing.processor import OMREvaluator, QUESTIONS_PER_SUBJECT 
from omr_processing.utils import apply_perspective_transform
# --- CONFIGURATION ---
# 1. Path to the sample OMR sheet image you want to debug
IMAGE_PATH = "omr_processing\Img7.jpeg"

# 2. Path to the answer key (make sure this is correct)
ANSWER_KEY_PATH = "web_app/answer_keys/set_a.json" 

# 3. Which question number do you want a detailed view of?
DEBUG_QUESTION_NUMBER = 5 
# ---------------------

def run_debug():
    print("--- Starting OMR Debugger ---")
    
    # Create a clean directory for debug output
    output_dir = "debug_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    print(f"1. Loading image: {IMAGE_PATH}")
    if not os.path.exists(IMAGE_PATH):
        print(f"FATAL ERROR: Image path not found: '{IMAGE_PATH}'")
        return

    # Initialize the evaluator
    evaluator = OMREvaluator(IMAGE_PATH, ANSWER_KEY_PATH)

    # --- Step 1: Check Calibration and Warping ---
    try:
        original_img = cv2.imread(IMAGE_PATH)
        warped_image = apply_perspective_transform(original_img, evaluator.calibration_points)
        cv2.imwrite(os.path.join(output_dir, "01_warped_image.jpg"), warped_image)
        print("✅ Saved '01_warped_image.jpg'. Check if the answer grid looks flat and rectangular.")
    except Exception as e:
        print(f"❌ ERROR during image warping: {e}")
        return

    # --- Step 2: Check Question Block Placement ---
    blocks_on_image = warped_image.copy()
    for i, (x, y, w, h) in enumerate(evaluator.question_blocks):
        color = (0, 255, 0) # Green
        cv2.rectangle(blocks_on_image, (x, y), (x + w, y + h), color, 3)
        cv2.putText(blocks_on_image, f"Block {i+1}", (x + 10, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imwrite(os.path.join(output_dir, "02_question_blocks.jpg"), blocks_on_image)
    print("✅ Saved '02_question_blocks.jpg'. Check if the green boxes correctly surround the 5 answer sections.")

    # --- Step 3: Deep Dive into a Single Question ---
    print(f"\n--- Analyzing Question {DEBUG_QUESTION_NUMBER} ---")
    
    # Find which block and row this question is in
    block_idx = (DEBUG_QUESTION_NUMBER - 1) // QUESTIONS_PER_SUBJECT
    row_idx_in_block = (DEBUG_QUESTION_NUMBER - 1) % QUESTIONS_PER_SUBJECT

    x, y, w, h = evaluator.question_blocks[block_idx]
    block_roi = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)[y:y+h, x:x+w]
    row_h = h // QUESTIONS_PER_SUBJECT
    row_y_start = row_idx_in_block * row_h
    
    # Isolate the specific row for our debug question
    row_roi = block_roi[row_y_start:row_y_start + row_h, :]
    
    # Save the isolated row
    cv2.imwrite(os.path.join(output_dir, f"03_q{DEBUG_QUESTION_NUMBER}_row_isolated.jpg"), row_roi)
    print(f"✅ Saved '03_q{DEBUG_QUESTION_NUMBER}_row_isolated.jpg'. This should be the small image of just one question's bubbles.")

    # --- Step 4: Check Thresholding and Contour Detection ---
    # This is the most critical step
    thresh = cv2.threshold(row_roi, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cv2.imwrite(os.path.join(output_dir, f"04_q{DEBUG_QUESTION_NUMBER}_row_threshold.jpg"), thresh)
    print(f"✅ Saved '04_q{DEBUG_QUESTION_NUMBER}_row_threshold.jpg'. Check if the filled-in bubbles are white and the background is black.")

    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    row_with_contours = cv2.cvtColor(row_roi, cv2.COLOR_GRAY2BGR)
    
    print(f"Found {len(contours)} initial contours in the row.")
    
    bubble_contours = []
    for c in contours:
        (cx, cy, cw, ch) = cv2.boundingRect(c)
        aspect_ratio = cw / float(ch) if ch > 0 else 0
        
        # Draw all initial contours in RED
        cv2.rectangle(row_with_contours, (cx, cy), (cx+cw, cy+ch), (0, 0, 255), 1)

        # Apply the filter from the processor
        if 12 < cw < 40 and 12 < ch < 40 and 0.75 < aspect_ratio < 1.25:
            bubble_contours.append(c)
            # Draw filtered contours (our "bubbles") in GREEN
            cv2.rectangle(row_with_contours, (cx, cy), (cx+cw, cy+ch), (0, 255, 0), 2)
            
    cv2.imwrite(os.path.join(output_dir, f"05_q{DEBUG_QUESTION_NUMBER}_row_contours.jpg"), row_with_contours)
    print(f"✅ Saved '05_q{DEBUG_QUESTION_NUMBER}_row_contours.jpg'. This is the most important image.")
    print(f"    - It should have exactly 4 GREEN boxes, one around each bubble.")
    print(f"    - If you see fewer than 4 green boxes, the filter is too strict.")
    print(f"    - If the boxes are in the wrong place, the thresholding failed.")
    print(f"Found {len(bubble_contours)} contours that passed the filter.")

    print("\n--- Debug Complete ---")
    print(f"Please check the images in the '{output_dir}' folder.")

if __name__ == "__main__":
    if "path/to/your" in IMAGE_PATH:
        print("ERROR: Please open 'debug_omr.py' and set the IMAGE_PATH variable.")
    else:
        run_debug()