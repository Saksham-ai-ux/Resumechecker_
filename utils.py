import fitz
import docx
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
import re

# Load spaCy model safely (auto-download if missing)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

global_skills = {"python", "spark", "machine learning", "sql", "tableau", "power bi", "data analysis"}
CSV_FILENAME = "res_eval.csv"

def extract_text_from_pdf(pdf_path):
    # Extract plain text from pdf
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    # Extract plain text from docx file
    doc = docx.Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_skills(text):
    doc = nlp(text.lower())
    extracted_skills = set()
    for ent in doc.ents:
        if ent.text in global_skills:
            extracted_skills.add(ent.text)
    for skill in global_skills:
        if skill in text.lower():
            extracted_skills.add(skill)
    return list(extracted_skills)

def compute_semantic_score(jd_text, resume_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)

def calculate_final_score(matched_skills_count, total_skills_req, semantic_score, hard_weight=0.7, semantic_weight=0.3):
    hard_score = (matched_skills_count / total_skills_req) * 100 if total_skills_req else 0
    hard_score = min(hard_score, 100)
    semantic_score = min(semantic_score, 100)
    final = hard_weight * hard_score + semantic_weight * semantic_score
    return min(round(final, 2), 100.0)

def extract_candidate_info(text):
    name = None
    phone = None
    name_match = re.search(r"Name\s*[:\-]\s*(\w+ \w+)", text, re.I)
    if name_match:
        name = name_match.group(1)
    else:
        first_line = text.strip().split('\n')[0]
        if len(first_line.split()) <= 4:
            name = first_line
    phone_match = re.search(r"(\(?\+?\d{1,3}\)?[-.\s]?)?(\d{10,12})", text)
    if phone_match:
        phone = phone_match.group(0)
    return name, phone

def save_evaluation(resume_name, score, missing_skills, jd_text, matched_skills, candidate_name=None, candidate_phone=None):
    exist = os.path.exists(CSV_FILENAME)
    df = pd.DataFrame([{
        "Resume Name": resume_name,
        "Score": score,
        "Missing Skills": ", ".join(missing_skills),
        "JD Excerpt": jd_text[:80] + "...",
        "Matched Skills": ", ".join(matched_skills),
        "Candidate Name": candidate_name or "",
        "Candidate Phone": candidate_phone or ""
    }])
    if exist:
        df.to_csv(CSV_FILENAME, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_FILENAME, mode="w", header=True, index=False)

def get_all_evaluations():
    if os.path.exists(CSV_FILENAME):
        return pd.read_csv(CSV_FILENAME)
    else:
        return pd.DataFrame(columns=["Resume Name","Score","Missing Skills","JD Excerpt","Matched Skills","Candidate Name","Candidate Phone"])
