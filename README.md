# Automated OMR Evaluation System

## Deployed Link - [text](https://automated-omr-system-ifl.streamlit.app/)
## 📝 Overview
This project provides a scalable, automated system for evaluating Optical Mark Recognition (OMR) sheets from images. It transforms the manual, error-prone, and time-consuming grading process for placement readiness assessments into a fast, accurate, and efficient workflow.

Designed to process thousands of OMR sheets captured via mobile phone cameras, the system corrects distortions and scores sheets against predefined answer keys. It offers subject-wise and total scores through a user-friendly web interface, reducing evaluation time from days to minutes.

### Key Benefits
- **Speed**: Evaluates batches of OMR sheets in minutes.
- **Accuracy**: Achieves <0.5% error rate using robust computer vision.
- **Efficiency**: Frees evaluators to focus on student feedback.
- **Scalability**: Handles thousands of sheets per exam day.
- **Transparency**: Provides visual overlays for a clear audit trail.

## ✨ Features
- **Image Ingestion**: Supports `.jpg` and `.png` images from mobile devices.
- **Advanced Preprocessing**: Corrects for:
  - Perspective distortion (angled images).
  - Rotation and skew.
  - Lighting variations.
- **Accurate Bubble Detection**: Uses OpenCV to identify marked bubbles in the grid.
- **Multi-Version Support**: Handles 2–4 exam versions (e.g., Set A, Set B) with corresponding answer keys.
- **Detailed Scoring**:
  - Subject-wise scores (0–20 for each of 5 subjects).
  - Total score (0–100).
- **Interactive Web Dashboard** (Streamlit):
  - Batch upload of OMR sheets.
  - Answer key selection.
  - Tabular result summaries.
  - Drill-down to review individual sheets.
- **Visual Audit Trail**: Saves processed images with:
  - Correct answers in green.
  - Incorrect answers in red.
- **Data Export**: Downloads batch results as a CSV file.

## ⚙️ System Workflow
The end-to-end process is simple and efficient:

1. **Capture**: Students complete OMR sheets; evaluators capture images using mobile phones.
2. **Upload**: Evaluators select the exam version (e.g., Set A) and upload images via the web app.
3. **Automated Processing**:
   - Detects sheet outline.
   - Applies perspective transform for a top-down view.
   - Thresholds image to isolate marked bubbles.
   - Identifies responses for each question.
4. **Scoring & Matching**: Compares answers to the selected key, calculating subject-wise and total scores.
5. **Result Display**: Shows a summary table in the web dashboard.
6. **Review & Export**: Evaluators review original and processed images side-by-side and export results as a CSV.

## 🛠️ Tech Stack
### Core OMR Engine
- **Python**: Backend logic.
- **OpenCV**: Image preprocessing, contour detection, perspective correction, and bubble analysis.
- **NumPy**: High-performance numerical operations on image arrays.

### Web Application & Data Handling:
- **Streamlit**: A rapid application development framework used to build the interactive front-end for evaluators.
- **Pandas**: Used for organizing the final results into a structured DataFrame for display and CSV export.

## 🚀 Setup and Installation Guide
Follow these steps to get the system running on your local machine.

### Prerequisites
- Python 3.8 or higher.
- `pip` (Python package installer).

### Step 1: Clone the Repository
Clone the project (replace `<repository-url>` with the actual repository URL):

```bash
git clone <repository-url>
cd automated-omr-system
```

### Step 2: Install Dependencies
Install required Python libraries:

```bash
pip install -r requirements.txt
```

### Step 3: Prepare Assets
- **OMR Template**:
  - Obtain a high-quality, blank OMR sheet image (scanned is ideal).
  - Save as `omr_template.png` in the `omr_processing/` folder, replacing the placeholder. Accuracy depends on this template.
- **Answer Key CSVs**:
  - Place raw answer key CSV files (e.g., `Key (Set A and B).xlsx - Set - A.csv`) in `scripts/source_keys/`.

### Step 4: Generate JSON Answer Keys
Convert CSV answer keys to JSON format:

```bash
python scripts/convert_keys.py
```

This creates `set_a.json` and `set_b.json` in `web_app/answer_keys/`.

### Step 5: Calibrate Bubble Coordinates
The system requires exact pixel locations of question blocks on the OMR template.

1. Open `omr_processing/processor.py`.
2. Locate the `self.question_blocks` list in the `OMREvaluator` class, containing `(x, y, width, height)` tuples for question blocks.
3. To find coordinates:
   - Open `omr_template.png` in an image editor (e.g., MS Paint, GIMP, or Preview).
   - Resize to 800x1000 pixels.
   - Note the top-left `x`, `y` coordinates of the first question block (questions 1–20).
   - Measure the block’s `width` and `height`.
   - Update the first tuple in `self.question_blocks`.
   - Repeat for all 5 question blocks.

### ▶️ Run the Application
Navigate to the `web_app` directory:

```bash
cd web_app
```

Launch the Streamlit app:

```bash
streamlit run app.py
```

Open the provided URL (typically `http://localhost:8501`) in your browser.

### Using the Web Interface
1. **Select Key**: Choose the answer key version (e.g., Set A) from the sidebar.
2. **Upload**: Drag and drop OMR sheet images or use the file browser.
3. **Evaluate**: Click "🚀 Start Evaluation."
4. **View Results**: Review the summary table; expand rows for detailed image comparisons.
5. **Download**: Click "📥 Download Results as CSV" to save the report.

## 🤔 Troubleshooting
- **Error: `Could not find OMR sheet contour`**:
  - Ensure the image is well-lit, clear, and includes all four corners of the sheet.
- **Incorrect Scores or Bubble Detection**:
  - Re-calibrate bubble coordinates (Step 5). Accurate coordinates are critical.
- **Error: `No answer keys found`**:
  - Run the command from Step 4 to generate JSON answer keys.