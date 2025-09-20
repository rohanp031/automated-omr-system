<<<<<<< HEAD

# Automated OMR Evaluation System

## 📝 Overview
This project provides a complete, scalable system to automatically evaluate OMR (Optical Mark Recognition) sheets from images. It addresses the challenges of manual grading for placement readiness assessments, transforming a time-consuming, error-prone, and resource-intensive process into a fast, accurate, and automated workflow.

The system is designed to process thousands of OMR sheets captured via mobile phone cameras, correcting for distortions and accurately scoring them against predefined answer keys. It provides subject-wise scores, total scores, and a user-friendly web interface for evaluators to manage the entire process, reducing the evaluation turnaround time from days to mere minutes.

### Key Benefits
- **Speed**: Evaluates an entire batch of OMR sheets in minutes.
- **Accuracy**: Achieves an error tolerance of <0.5% through robust computer vision techniques.
- **Efficiency**: Frees up evaluators to focus on student feedback and engagement rather than manual grading.
- **Scalability**: Capable of handling thousands of sheets from a single exam day.
- **Transparency**: Generates visual overlays on processed sheets for a clear audit trail.

## ✨ Features
- **Image Ingestion**: Accepts OMR sheet images (.jpg, .png) captured from any mobile device.
- **Advanced Preprocessing**: Automatically corrects for:
  - Perspective distortion (images taken at an angle).
  - Rotation and skew.
  - Lighting variations.
- **Accurate Bubble Detection**: Uses classical computer vision (OpenCV) to precisely identify the grid of bubbles and determine which ones are marked.
- **Multi-Version Support**: Seamlessly handles 2-4 different versions (e.g., Set A, Set B) of an exam by matching against the correct answer key.
- **Detailed Scoring**: Calculates and displays:
  - Subject-wise scores (0–20 for each of the 5 subjects).
  - Total score (0–100).
- **Interactive Web Dashboard**: A user-friendly interface built with Streamlit for:
  - Uploading multiple OMR sheets in a single batch.
  - Selecting the appropriate answer key version.
  - Viewing a summary of results in a clean, tabular format.
  - Drilling down to review individual sheets with visual feedback.
- **Visual Audit Trail**: For each sheet, the system saves a processed image showing:
  - Correct answers highlighted in green.
  - Incorrectly marked answers highlighted in red.
- **Data Export**: Allows evaluators to download the complete results of a batch as a single CSV file for reporting and further analysis.

## ⚙️ System Workflow
The end-to-end process is designed for simplicity and efficiency.

1. **Capture**: Students fill out the standard OMR sheets during an assessment. Afterward, an evaluator captures an image of each sheet using a mobile phone.
2. **Upload**: The evaluator navigates to the web application, selects the correct exam version (e.g., "Set A"), and uploads the batch of captured images.
3. **Automated Processing**: Upon clicking "Start Evaluation," the backend pipeline executes for each image:
   - The system detects the sheet's outline.
   - A perspective transform is applied to get a flat, top-down view.
   - The image is thresholded to isolate marked bubbles.
   - The system iterates through predefined question blocks, identifies the marked response for each question, and stores the student's answers.
4. **Scoring & Matching**: The extracted answers are compared against the selected answer key. Subject-wise and total scores are calculated.
5. **Result Display**: The web dashboard updates with a summary table of the results.
6. **Review & Export**: The evaluator can expand each entry to see the original and processed images side-by-side for verification. Finally, they can download a consolidated CSV report of all the scores.

## 🛠️ Tech Stack
The system is built with a powerful and efficient stack of open-source technologies.

### Core OMR Engine:
- **Python**: The primary programming language for the entire backend logic.
- **OpenCV**: The core library for all computer vision tasks, including image preprocessing, contour detection, perspective correction, and bubble analysis.
- **NumPy**: Used for high-performance numerical operations on image arrays.

### Web Application & Data Handling:
- **Streamlit**: A rapid application development framework used to build the interactive front-end for evaluators.
- **Pandas**: Used for organizing the final results into a structured DataFrame for display and CSV export.

## 📁 Project Structure
The codebase is organized into distinct modules for clarity and maintainability.

```
automated-omr-system/
|-- omr_processing/        # Core computer vision logic
|   |-- __init__.py        # Makes the directory a Python package
|   |-- processor.py       # Main evaluation pipeline class
|   |-- utils.py           # Image processing helper functions
|   |-- omr_template.png   # CRITICAL: Your blank OMR sheet template
|
|-- web_app/               # Streamlit application
|   |-- app.py             # The web app code
|   |-- answer_keys/       # Folder for generated JSON answer keys
|   |-- uploads/           # Temporarily stores uploaded images
|   |-- results/           # Stores all output files (images, JSON, CSV)
|
|-- scripts/               # Helper scripts for data preparation
|   |-- convert_keys.py    # Script to convert CSV keys to JSON
|   |-- source_keys/       # Folder for your raw answer key CSV files
|
|-- requirements.txt       # Python dependencies
|-- README.md              # This file
```

## 🚀 Setup and Installation Guide
Follow these steps to get the system running on your local machine.

### Prerequisites
- Python 3.8 or higher.
- pip (Python package installer).

### Step 1: Clone the Repository
Open your terminal and clone this project:

```bash
git clone <repository-url>
cd automated-omr-system
```

### Step 2: Install Dependencies
Install all the required Python libraries using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 3: Prepare Your Assets (Mandatory)
- **OMR Template**:
  - Get a high-quality, clean, and blank image of your OMR sheet. A scanned image is ideal.
  - Save it as `omr_template.png` and place it inside the `omr_processing/` folder, replacing the placeholder file. The system's accuracy depends entirely on this template.
- **Answer Key CSVs**:
  - Place your raw answer key CSV files (e.g., `Key (Set A and B).xlsx - Set - A.csv`) inside the `scripts/source_keys/` directory.

### Step 4: Generate JSON Answer Keys
The application uses JSON files for answer keys. Run the provided script to convert your source CSVs into the required format.

```bash
python scripts/convert_keys.py
```

This command reads the CSVs from `scripts/source_keys/` and creates `set_a.json` and `set_b.json` in `web_app/answer_keys/`.

### Step 5: Calibrate Bubble Coordinates (Critical for Accuracy)
The system needs to know the exact pixel locations of the question blocks on your OMR sheet. You must calibrate this for your specific template.

- Open the file `omr_processing/processor.py`.
- Find the `self.question_blocks` list inside the `OMREvaluator` class.
- This list contains tuples `(x, y, width, height)` that define the rectangular areas for the question blocks.
- To find these coordinates:
  - Open your `omr_template.png` in an image editor (like MS Paint, GIMP, or Preview on Mac).
  - Resize the image to 800x1000 pixels.
  - Hover your cursor over the top-left corner of the first question block (for questions 1-20) to get the `x` and `y` coordinates.
  - Determine the `width` and `height` of the block.
  - Update the first tuple in the list with these values.
  - Repeat for all 5 question blocks.

### ▶️ How to Run the Application
Navigate to the `web_app` directory in your terminal:

```bash
cd web_app
```

Run the Streamlit application:

```bash
streamlit run app.py
```

Open your web browser and go to the local URL provided by Streamlit, which is typically `http://localhost:8501`.

### Using the Web Interface
1. **Select Key**: Choose the correct answer key version (e.g., "Set A") from the sidebar dropdown.
2. **Upload**: Drag and drop your OMR sheet images or use the file browser.
3. **Evaluate**: Click the "🚀 Start Evaluation" button.
4. **View Results**: A summary table will appear. You can expand each row to see a detailed side-by-side comparison of the original and processed images.
5. **Download**: Click the "📥 Download Results as CSV" button to save a report.

## 🤔 Troubleshooting
- **Error: "Could not find OMR sheet contour"**
  - This usually means the image quality is poor. Ensure the image is well-lit, not blurry, and the entire sheet (including all four corners) is visible.
- **Incorrect Scores or Bubbles Detected**
  - This is almost always due to incorrect calibration. Please re-do **Step 5: Calibrate Bubble Coordinates** carefully. The accuracy of the coordinates is paramount.
- **Error: "No answer keys found" in the app**
  - This means you haven't generated the JSON keys yet. Please run the command from **Step 4: Generate JSON Answer Keys**.
=======
# Automated OMR Evaluation System 

## 📝 Overview
This project provides a complete, scalable system to automatically evaluate OMR (Optical Mark Recognition) sheets from images. It addresses the challenges of manual grading for placement readiness assessments, transforming a time-consuming, error-prone, and resource-intensive process into a fast, accurate, and automated workflow.

The system is designed to process thousands of OMR sheets captured via mobile phone cameras, correcting for distortions and accurately scoring them against predefined answer keys. It provides subject-wise scores, total scores, and a user-friendly web interface for evaluators to manage the entire process, reducing the evaluation turnaround time from days to mere minutes.

### Key Benefits
- **Speed**: Evaluates an entire batch of OMR sheets in minutes.
- **Accuracy**: Achieves an error tolerance of <0.5% through robust computer vision techniques.
- **Efficiency**: Frees up evaluators to focus on student feedback and engagement rather than manual grading.
- **Scalability**: Capable of handling thousands of sheets from a single exam day.
- **Transparency**: Generates visual overlays on processed sheets for a clear audit trail.

## ✨ Features
- **Image Ingestion**: Accepts OMR sheet images (.jpg, .png) captured from any mobile device.
- **Advanced Preprocessing**: Automatically corrects for:
  - Perspective distortion (images taken at an angle).
  - Rotation and skew.
  - Lighting variations.
- **Accurate Bubble Detection**: Uses classical computer vision (OpenCV) to precisely identify the grid of bubbles and determine which ones are marked.
- **Multi-Version Support**: Seamlessly handles 2-4 different versions (e.g., Set A, Set B) of an exam by matching against the correct answer key.
- **Detailed Scoring**: Calculates and displays:
  - Subject-wise scores (0–20 for each of the 5 subjects).
  - Total score (0–100).
- **Interactive Web Dashboard**: A user-friendly interface built with Streamlit for:
  - Uploading multiple OMR sheets in a single batch.
  - Selecting the appropriate answer key version.
  - Viewing a summary of results in a clean, tabular format.
  - Drilling down to review individual sheets with visual feedback.
- **Visual Audit Trail**: For each sheet, the system saves a processed image showing:
  - Correct answers highlighted in green.
  - Incorrectly marked answers highlighted in red.
- **Data Export**: Allows evaluators to download the complete results of a batch as a single CSV file for reporting and further analysis.

## ⚙️ System Workflow
The end-to-end process is designed for simplicity and efficiency.

1. **Capture**: Students fill out the standard OMR sheets during an assessment. Afterward, an evaluator captures an image of each sheet using a mobile phone.
2. **Upload**: The evaluator navigates to the web application, selects the correct exam version (e.g., "Set A"), and uploads the batch of captured images.
3. **Automated Processing**: Upon clicking "Start Evaluation," the backend pipeline executes for each image:
   - The system detects the sheet's outline.
   - A perspective transform is applied to get a flat, top-down view.
   - The image is thresholded to isolate marked bubbles.
   - The system iterates through predefined question blocks, identifies the marked response for each question, and stores the student's answers.
4. **Scoring & Matching**: The extracted answers are compared against the selected answer key. Subject-wise and total scores are calculated.
5. **Result Display**: The web dashboard updates with a summary table of the results.
6. **Review & Export**: The evaluator can expand each entry to see the original and processed images side-by-side for verification. Finally, they can download a consolidated CSV report of all the scores.

## 🛠️ Tech Stack
The system is built with a powerful and efficient stack of open-source technologies.

### Core OMR Engine:
- **Python**: The primary programming language for the entire backend logic.
- **OpenCV**: The core library for all computer vision tasks, including image preprocessing, contour detection, perspective correction, and bubble analysis.
- **NumPy**: Used for high-performance numerical operations on image arrays.

### Web Application & Data Handling:
- **Streamlit**: A rapid application development framework used to build the interactive front-end for evaluators.
- **Pandas**: Used for organizing the final results into a structured DataFrame for display and CSV export.

## 📁 Project Structure
The codebase is organized into distinct modules for clarity and maintainability.

```
automated-omr-system/
|-- omr_processing/        # Core computer vision logic
|   |-- __init__.py        # Makes the directory a Python package
|   |-- processor.py       # Main evaluation pipeline class
|   |-- utils.py           # Image processing helper functions
|   |-- omr_template.png   # CRITICAL: Your blank OMR sheet template
|
|-- web_app/               # Streamlit application
|   |-- app.py             # The web app code
|   |-- answer_keys/       # Folder for generated JSON answer keys
|   |-- uploads/           # Temporarily stores uploaded images
|   |-- results/           # Stores all output files (images, JSON, CSV)
|
|-- scripts/               # Helper scripts for data preparation
|   |-- convert_keys.py    # Script to convert CSV keys to JSON
|   |-- source_keys/       # Folder for your raw answer key CSV files
|
|-- requirements.txt       # Python dependencies
|-- README.md              # This file
```

## 🚀 Setup and Installation Guide
Follow these steps to get the system running on your local machine.

### Prerequisites
- Python 3.8 or higher.
- pip (Python package installer).

### Step 1: Clone the Repository
Open your terminal and clone this project:

```bash
git clone <repository-url>
cd automated-omr-system
```

### Step 2: Install Dependencies
Install all the required Python libraries using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 3: Prepare Your Assets (Mandatory)
- **OMR Template**:
  - Get a high-quality, clean, and blank image of your OMR sheet. A scanned image is ideal.
  - Save it as `omr_template.png` and place it inside the `omr_processing/` folder, replacing the placeholder file. The system's accuracy depends entirely on this template.
- **Answer Key CSVs**:
  - Place your raw answer key CSV files (e.g., `Key (Set A and B).xlsx - Set - A.csv`) inside the `scripts/source_keys/` directory.

### Step 4: Generate JSON Answer Keys
The application uses JSON files for answer keys. Run the provided script to convert your source CSVs into the required format.

```bash
python scripts/convert_keys.py
```

This command reads the CSVs from `scripts/source_keys/` and creates `set_a.json` and `set_b.json` in `web_app/answer_keys/`.

### Step 5: Calibrate Bubble Coordinates (Critical for Accuracy)
The system needs to know the exact pixel locations of the question blocks on your OMR sheet. You must calibrate this for your specific template.

- Open the file `omr_processing/processor.py`.
- Find the `self.question_blocks` list inside the `OMREvaluator` class.
- This list contains tuples `(x, y, width, height)` that define the rectangular areas for the question blocks.
- To find these coordinates:
  - Open your `omr_template.png` in an image editor (like MS Paint, GIMP, or Preview on Mac).
  - Resize the image to 800x1000 pixels.
  - Hover your cursor over the top-left corner of the first question block (for questions 1-20) to get the `x` and `y` coordinates.
  - Determine the `width` and `height` of the block.
  - Update the first tuple in the list with these values.
  - Repeat for all 5 question blocks.

### ▶️ How to Run the Application
Navigate to the `web_app` directory in your terminal:

```bash
cd web_app
```

Run the Streamlit application:

```bash
streamlit run app.py
```

Open your web browser and go to the local URL provided by Streamlit, which is typically `http://localhost:8501`.

### Using the Web Interface
1. **Select Key**: Choose the correct answer key version (e.g., "Set A") from the sidebar dropdown.
2. **Upload**: Drag and drop your OMR sheet images or use the file browser.
3. **Evaluate**: Click the "🚀 Start Evaluation" button.
4. **View Results**: A summary table will appear. You can expand each row to see a detailed side-by-side comparison of the original and processed images.
5. **Download**: Click the "📥 Download Results as CSV" button to save a report.

## 🤔 Troubleshooting
- **Error: "Could not find OMR sheet contour"**
  - This usually means the image quality is poor. Ensure the image is well-lit, not blurry, and the entire sheet (including all four corners) is visible.
- **Incorrect Scores or Bubbles Detected**
  - This is almost always due to incorrect calibration. Please re-do **Step 5: Calibrate Bubble Coordinates** carefully. The accuracy of the coordinates is paramount.
- **Error: "No answer keys found" in the app**
  - This means you haven't generated the JSON keys yet. Please run the command from **Step 4: Generate JSON Answer Keys**.

>>>>>>> 78c965661daec79ed68ac5bfc8774a537ebfc9b0
