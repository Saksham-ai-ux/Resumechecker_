import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_docx, extract_skills

st.title("Welcome to Smart Resume Evaluation System")

jd_file = st.file_uploader("Upload Job Description (PDF or DOCX)", type=["pdf", "docx"])
if 'jd_text' not in st.session_state:
    st.session_state['jd_text'] = ""

if jd_file:
    ext = jd_file.name.split('.')[-1]
    with open("jd_temp." + ext, "wb") as f:
        f.write(jd_file.getbuffer())
    if ext == "pdf":
        st.session_state['jd_text'] = extract_text_from_pdf("jd_temp." + ext)
    else:
        st.session_state['jd_text'] = extract_text_from_docx("jd_temp." + ext)
    st.success("Job Description uploaded!")
    st.write(st.session_state['jd_text'][:500] + "...")

if st.session_state['jd_text']:
    jd_skills = extract_skills(st.session_state['jd_text'])
    st.write("Extracted Skills from JD:", ", ".join(jd_skills))
