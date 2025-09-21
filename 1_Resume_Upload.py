import streamlit as st
from utils import (extract_text_from_pdf, extract_text_from_docx, extract_skills,
                   compute_semantic_score, calculate_final_score,
                   save_evaluation, extract_candidate_info)
import os

st.title("Resume Upload & Evaluation")

if 'jd_text' not in st.session_state or not st.session_state['jd_text']:
    st.warning("Please upload JD on Home Page first.")
    st.stop()

jd_text = st.session_state['jd_text']

resume_files = st.file_uploader("Upload Multiple Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

if resume_files:
    for resume_file in resume_files:
        ext = resume_file.name.split('.')[-1]
        with open("resume_temp." + ext, "wb") as f:
            f.write(resume_file.getbuffer())

        if ext == "pdf":
            resume_text = extract_text_from_pdf("resume_temp." + ext)
        else:
            resume_text = extract_text_from_docx("resume_temp." + ext)

        resume_skills = extract_skills(resume_text)
        semantic_score = compute_semantic_score(jd_text, resume_text)
        num_matched = len(set(extract_skills(jd_text)) & set(resume_skills))
        final_score = calculate_final_score(num_matched, len(extract_skills(jd_text)), semantic_score)
        missing_skills = set(extract_skills(jd_text)) - set(resume_skills)

        name, phone = extract_candidate_info(resume_text)

        st.subheader(resume_file.name)
        st.write(f"Candidate Name: {name or 'N/A'}")
        st.write(f"Candidate Phone: {phone or 'N/A'}")
        st.write(f"Relevance Score: {final_score}%")
        st.write(f"Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}")

        os.remove("resume_temp." + ext)

        save_evaluation(resume_file.name, final_score, missing_skills, jd_text, set(resume_skills) & set(extract_skills(jd_text)), candidate_name=name, candidate_phone=phone)

else:
    st.info("Please upload resumes to evaluate.")
