import cv2
import numpy as np
import json
from . import utils

TOTAL_QUESTIONS = 100
TOTAL_OPTIONS = 4
QUESTIONS_PER_SUBJECT = 20
NUM_SUBJECTS = 5
BUBBLE_THRESHOLD_RATIO = 0.30 

class OMREvaluator:
    def __init__(self, image_path, answer_key_path):
        self.image_path = image_path
        with open(answer_key_path, 'r') as f:
            self.answer_key = json.load(f)
        self.processed_data = {}
        
        self.calibration_points = np.array([[75, 167], [934, 164], [953, 904], [49, 900]])
        
        self.question_blocks = [
            (4, 98, 152, 897),
            (172, 101, 139, 888),
            (325, 101, 149, 890),
            (478, 104, 155, 891),
            (632, 106, 161, 888),
        ]

    def run_evaluation(self):
        try:
            original_img = cv2.imread(self.image_path)
            if original_img is None: raise ValueError("Image could not be read.")
            self.warped_image = utils.apply_perspective_transform(original_img, self.calibration_points)
            self.warped_gray = cv2.cvtColor(self.warped_image, cv2.COLOR_BGR2GRAY)
            self.extract_and_score_bubbles()
            self.create_visual_overlay()
            return self.processed_data, self.overlay_image
        except Exception as e:
            print(f"Error processing {self.image_path}: {e}")
            return None, None

    def extract_and_score_bubbles(self):
        detected_answers = {}
        total_score = 0
        subject_scores = {f"Subject_{i+1}": 0 for i in range(NUM_SUBJECTS)}
        question_counter = 1
        
        for block_idx, (x, y, w, h) in enumerate(self.question_blocks):
            block_roi = self.warped_gray[y:y+h, x:x+w]
            row_h = h // QUESTIONS_PER_SUBJECT
            
            for i in range(QUESTIONS_PER_SUBJECT):
                row_y_start = i * row_h
                row_roi = block_roi[row_y_start:row_y_start+row_h, :]
                thresh = cv2.threshold(row_roi, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                min_area = 50
                possible_bubbles = [c for c in contours if cv2.contourArea(c) > min_area]

                if len(possible_bubbles) >= TOTAL_OPTIONS:
                    possible_bubbles.sort(key=cv2.contourArea, reverse=True)
                    bubble_contours = possible_bubbles[:TOTAL_OPTIONS]
                else:
                    bubble_contours = []

                if len(bubble_contours) != TOTAL_OPTIONS:
                    question_counter += 1
                    continue

                bubble_contours, _ = utils.sort_contours(bubble_contours, method="left-to-right")
                marked_bubble_index = -1
                max_filled = -1

                for j, c in enumerate(bubble_contours):
                    mask = np.zeros(thresh.shape, dtype="uint8")
                    cv2.drawContours(mask, [c], -1, 255, -1)
                    mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                    total_pixels = cv2.countNonZero(mask)
                    if total_pixels > max_filled:
                        max_filled = total_pixels
                        marked_bubble_index = j
                
                (cx, cy, cw, ch) = cv2.boundingRect(bubble_contours[marked_bubble_index])
                bubble_area = cw * ch
                fill_ratio = max_filled / float(bubble_area) if bubble_area > 0 else 0
                marked_answer = -1
                if fill_ratio > BUBBLE_THRESHOLD_RATIO:
                    marked_answer = marked_bubble_index
                    
                correct_answer_char = self.answer_key.get(str(question_counter))
                correct_answer_index = {"A": 0, "B": 1, "C": 2, "D": 3}.get(correct_answer_char, -1)
                is_correct = (marked_answer == correct_answer_index)
                if is_correct:
                    total_score += 1
                    subject_scores[f"Subject_{block_idx + 1}"] += 1

                detected_answers[question_counter] = {
                    "marked": {0: "A", 1: "B", 2: "C", 3: "D"}.get(marked_answer, "None"),
                    "correct": correct_answer_char, "is_correct": is_correct,
                    "coords": [cv2.boundingRect(c) for c in bubble_contours], "block_origin": (x,y)
                }
                question_counter += 1

        self.processed_data = {"total_score": total_score, "subject_scores": subject_scores, "detected_answers": detected_answers}

    def create_visual_overlay(self):
        self.overlay_image = self.warped_image.copy()
        if not self.processed_data.get("detected_answers"):
            return
        for q_num, data in self.processed_data["detected_answers"].items():
            correct_answer_char = data["correct"]
            correct_answer_index = {"A": 0, "B": 1, "C": 2, "D": 3}.get(correct_answer_char, -1)
            marked_answer_char = data["marked"]
            marked_answer_index = {"A": 0, "B": 1, "C": 2, "D": 3}.get(marked_answer_char, -1)
            block_x, block_y = data["block_origin"]
            q_in_block = (q_num - 1) % QUESTIONS_PER_SUBJECT
            row_h = (self.question_blocks[block_idx][3] / QUESTIONS_PER_SUBJECT)
            
            if len(data["coords"]) != TOTAL_OPTIONS:
                continue

            if correct_answer_index != -1:
                (cx, cy, cw, ch) = data["coords"][correct_answer_index]
                abs_x, abs_y = block_x + cx, block_y + int(q_in_block * row_h) + cy
                cv2.rectangle(self.overlay_image, (abs_x, abs_y), (abs_x+cw, abs_y+ch), (0, 255, 0), 2)
            
            if marked_answer_index != -1 and not data["is_correct"]:
                (cx, cy, cw, ch) = data["coords"][marked_answer_index]
                abs_x, abs_y = block_x + cx, block_y + int(q_in_block * row_h) + cy
                cv2.rectangle(self.overlay_image, (abs_x, abs_y), (abs_x+cw, abs_y+ch), (0, 0, 255), 2)