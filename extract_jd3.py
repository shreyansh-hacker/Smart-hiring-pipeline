import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document(r'd:\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\job_description.docx')
lines = [p.text for p in doc.paragraphs]
for i, line in enumerate(lines[:40]):
    print(f"[{i}] {line}")
