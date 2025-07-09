# granite_chat_model.py (Ollama version with real-time progress bar and accuracy checker)

import pandas as pd
import ollama
import time
from tqdm import tqdm
from difflib import SequenceMatcher
import threading

# Load Granite model through Ollama
MODEL_NAME = "granite3.3:2b"  # Ensure you've pulled it via `ollama pull granite3.3:2b`

# Spinner-style progress bar with threading
class Spinner:
    def __init__(self, message="Generating response"):
        self.stop_running = False
        self.message = message
        self.thread = threading.Thread(target=self.spin)

    def spin(self):
        spinner_chars = ['|', '/', '-', '\\']
        idx = 0
        print(self.message, end=' ', flush=True)
        while not self.stop_running:
            print(spinner_chars[idx % len(spinner_chars)], end='\r', flush=True)
            time.sleep(0.1)
            idx += 1

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_running = True
        self.thread.join()
        print("Done.\n")

def chat_with_model(prompt):
    print("[INFO] Sending prompt to Ollama...")
    spinner = Spinner("Generating response...\n")
    spinner.start()
    response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
    spinner.stop()
    return response['message']['content']

def read_excel_summary(df, max_rows=10):
    # Accepts a DataFrame instead of file path
    sample = df.head(max_rows)
    return sample.to_string()

def generate_prompt(file_path, user_question):
    sheet_summary = read_excel_summary(file_path)
    prompt = f"""
You are a helpful assistant skilled in analyzing Excel data.
Here is a preview of the dataset:

{sheet_summary}

Your task is to answer the following question based on the data provided in the Excel file. Please ensure your response is clear, concise, and directly addresses the question.
The dataset contains various columns, including Sample ID, Patient Name, and Test Type, among others.
The column Test Type contanins acronomes and their full forms are as follows:
FTS - First Trimester Screening 
QD - Quadruple Screening 
FTPE - First Trimester Screening+ Pre Eclampsia 
EFTS - Enhanced First Trimester Screening 
NBS - New Born Screening 
KT - Karyotyping 
QFPCR - Quantitative Fluorescence Polymerase Chain Reaction 
MCC - Maternal Cell Contamination 
KBoBs - Karyolite BoBs
PBoBs - Prenatal BoBs 
YMD - Y- Micro Deletion 
DES - DNA Extraction & Storage 
WES - Whole Exome Sequencing 
KFAM - Known Familial Mutation 
WGS - Whole Genome Sequencing 
CMA - Chromosomal Microarray

Instructions:
- When asked to summarize provide detailed paragraph-style explanations.
- when summarizing, include all details from the row to provide a comprehensive overview.
- Ensure the response reads like a professional tone.
- If the question is about a specific sample, provide the relevant details.
- Make the responce stright to the point.

Now answer the following question:
{user_question}
"""
    return prompt

def generate_prompt_from_df(df, user_question):
    # New function for Streamlit: uses DataFrame directly
    sheet_summary = read_excel_summary(df)
    prompt = f"""
You are a helpful assistant skilled in analyzing Excel data.

Here is a preview of the dataset:

{sheet_summary}

Your task is to answer the following question based on the data provided in the Excel file. Please ensure your response is clear, concise, and directly addresses the question.
The dataset contains various columns, including Sample ID, Patient Name, and Test Type, among others.
The column Test Type contanins acronomes and their full forms are as follows:
FTS - First Trimester Screening 
QD - Quadruple Screening 
FTPE - First Trimester Screening+ Pre Eclampsia 
EFTS - Enhanced First Trimester Screening 
NBS - New Born Screening 
KT - Karyotyping 
QFPCR - Quantitative Fluorescence Polymerase Chain Reaction 
MCC - Maternal Cell Contamination 
KBoBs - Karyolite BoBs
PBoBs - Prenatal BoBs 
YMD - Y- Micro Deletion 
DES - DNA Extraction & Storage 
WES - Whole Exome Sequencing 
KFAM - Known Familial Mutation 
WGS - Whole Genome Sequencing 
CMA - Chromosomal Microarray

Instructions:
- When asked to summarize provide detailed paragraph-style explanations.
- when summarizing, include all details from the row to provide a comprehensive overview.
- Ensure the response reads like a professional tone.
- If the question is about a specific sample, provide the relevant details.
- Make the responce stright to the point.

Now answer the following question:
{user_question}
"""
    return prompt

def calculate_accuracy(expected_answer, model_response):
    similarity = SequenceMatcher(None, expected_answer.lower(), model_response.lower()).ratio()
    return round(similarity * 100, 2)

# Continuous prompt-response loop
if __name__ == "__main__":
    excel_file = "Data_BDC_2022_-_23.xlsx"  # Keep this as-is
    print("\n[Granite Chat - Type 'bye' to exit]\n")

    while True:
        user_question = input("You: ") # What is the Patient Name of the Sample ID 'QD22004354'?
        if user_question.strip().lower() == "bye":
            print("[Session ended]")
            break

        expected_answer = input("Expected Answer (for accuracy check): ") # The Patient Name associated with the Sample ID 'QD22004354' is Mrs. Nabisha Mohideen.
        prompt = generate_prompt(excel_file, user_question)
        response = chat_with_model(prompt)
        print("\nGranite: ", response, "\n")

        if expected_answer.strip():
            accuracy = calculate_accuracy(expected_answer, response)
            print(f"[Accuracy]: {accuracy}%\n")
