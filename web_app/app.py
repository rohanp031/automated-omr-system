import streamlit as st
import os
import sys
import pandas as pd
import json
import cv2
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from omr_processing.processor import OMREvaluator

st.set_page_config(
    page_title="Innomatics OMR Evaluation System",
    page_icon="📝",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
CSV_DIR = os.path.join(RESULTS_DIR, "csv")
JSON_DIR = os.path.join(RESULTS_DIR, "json")
IMG_DIR = os.path.join(RESULTS_DIR, "processed_images")
KEYS_DIR = os.path.join(BASE_DIR, "answer_keys")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

def get_answer_keys():
    keys = {}
    if not os.path.exists(KEYS_DIR):
        return keys
    for f in os.listdir(KEYS_DIR):
        if f.endswith(".json"):
            key_name = os.path.splitext(f)[0].replace("_", " ").title()
            keys[key_name] = os.path.join(KEYS_DIR, f)
    return keys

st.title("📝 Automated OMR Evaluation System")
st.markdown("### Welcome to the Innomatics Research Labs OMR evaluation portal.")

with st.sidebar:
    st.header("⚙️ Settings")
    
    available_keys = get_answer_keys()
    if not available_keys:
        st.error("No answer keys found. Please run the key conversion script first.")
        selected_key_name = None
        answer_key_path = None
    else:
        selected_key_name = st.selectbox(
            "Select Answer Key Version",
            options=sorted(list(available_keys.keys()))
        )
        answer_key_path = available_keys.get(selected_key_name)

    uploaded_files = st.file_uploader(
        "Upload OMR Sheet Images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    
    start_button = st.button("🚀 Start Evaluation", use_container_width=True, disabled=(not available_keys))

if start_button and uploaded_files:
    if not answer_key_path:
        st.error("Please select a valid answer key.")
    else:
        st.info(f"Processing {len(uploaded_files)} sheets using **{selected_key_name}**...")
        
        progress_bar = st.progress(0)
        results_list = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            file_path = os.path.join(UPLOADS_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            evaluator = OMREvaluator(image_path=file_path, answer_key_path=answer_key_path)
            result_data, overlay_image = evaluator.run_evaluation()
            
            if result_data:
                flat_data = {
                    "filename": uploaded_file.name,
                    "total_score": result_data["total_score"],
                    **result_data["subject_scores"],
                    "evaluated_at": datetime.now().isoformat()
                }
                results_list.append(flat_data)

                filename_base = os.path.splitext(uploaded_file.name)[0]
                cv2.imwrite(os.path.join(IMG_DIR, f"{filename_base}_processed.png"), overlay_image)
                with open(os.path.join(JSON_DIR, f"{filename_base}_result.json"), 'w') as f:
                    json.dump(result_data, f, indent=4)
            else:
                 st.warning(f"Could not process `{uploaded_file.name}`. It might be distorted or unclear.")

            progress_bar.progress((i + 1) / len(uploaded_files))

        st.success("✅ Evaluation complete!")

        if results_list:
            results_df = pd.DataFrame(results_list)
            st.dataframe(results_df)

            csv_data = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_data,
                file_name=f"omr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
            
            st.subheader("🔍 Detailed Review")
            for result in results_list:
                with st.expander(f"View details for **{result['filename']}**"):
                    col1, col2 = st.columns(2)
                    filename_base = os.path.splitext(result['filename'])[0]
                    
                    with col1:
                        st.image(os.path.join(UPLOADS_DIR, result['filename']), caption="Original Image")
                    with col2:
                        st.image(os.path.join(IMG_DIR, f"{filename_base}_processed.png"), caption="Processed & Graded Image")

elif start_button and not uploaded_files:
    st.warning("Please upload at least one OMR sheet image.")