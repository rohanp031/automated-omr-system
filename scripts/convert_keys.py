import pandas as pd
import json
import os
import re

def convert_csv_to_json(csv_path, json_path):
    df = pd.read_csv(csv_path, header=0)
    answer_key = {}

    for col in df.columns:
        for item in df[col].dropna():
            item = str(item).strip()
            match = re.match(r'(\d+)\s*[-.]?\s*([a-zA-Z])', item)
            if match:
                question_num = match.group(1)
                answer = match.group(2).upper()
                answer_key[question_num] = answer

    sorted_answer_key = {k: v for k, v in sorted(answer_key.items(), key=lambda item: int(item[0]))}

    with open(json_path, 'w') as f:
        json.dump(sorted_answer_key, f, indent=4)
    print(f"Successfully converted {csv_path} to {json_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    source_dir = os.path.join(base_dir, "source_keys")
    output_dir = os.path.join(base_dir, "..", "web_app", "answer_keys")

    os.makedirs(output_dir, exist_ok=True)

    files_to_convert = {
        "Key (Set A and B).xlsx - Set - A.csv": "set_a.json",
        "Key (Set A and B).xlsx - Set - B.csv": "set_b.json",
    }

    for csv_file, json_file in files_to_convert.items():
        csv_input_path = os.path.join(source_dir, csv_file)
        json_output_path = os.path.join(output_dir, json_file)

        if os.path.exists(csv_input_path):
            convert_csv_to_json(csv_input_path, json_output_path)
        else:
            print(f"Warning: Source file not found at {csv_input_path}")