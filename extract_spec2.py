import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document(r'd:\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\submission_spec.docx')
lines = [p.text for p in doc.paragraphs]
# print first 100 lines
for line in lines[:100]:
    print(line)
