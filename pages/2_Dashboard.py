import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import base64
from utils import get_all_evaluations

def get_suitability(score):
    if score >= 75:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"

def candidate_initials(name):
    if not name or pd.isna(name):
        return "NA"
    parts = name.split()
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[1][0]).upper()

def create_download_link(df, filename="filtered_resumes.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">⬇️ Download Filtered Data</a>'
    return href

if 'shortlist' not in st.session_state:
    st.session_state['shortlist'] = set()

def add_to_shortlist(resume_name):
    st.session_state['shortlist'].add(resume_name)

def remove_from_shortlist(resume_name):
    st.session_state['shortlist'].discard(resume_name)

st.title("Resume Relevance Dashboard")

df = get_all_evaluations()

if df.empty:
    st.info("No evaluations found. Upload and evaluate resumes first.")
    st.stop()

df = df.sort_values("Score", ascending=False).drop_duplicates(subset="Resume Name", keep="first")
df["Score"] = df["Score"].apply(lambda x: min(x, 100))
df["Suitability"] = df["Score"].apply(get_suitability)
df["Initials"] = df["Candidate Name"].apply(candidate_initials)

cols = st.columns(3)
cols[0].markdown(f'<div style="background: linear-gradient(135deg, #fbc2eb, #fad0c4); border-radius: 12px; padding: 1rem; color: #6d1850; box-shadow: 0 0 12px #f5b7b1;"><h3>Average Score</h3><h2>{df["Score"].mean():.1f}%</h2></div>', unsafe_allow_html=True)
cols[1].markdown(f'<div style="background: linear-gradient(135deg, #a1c4fd, #c2e9fb); border-radius: 12px; padding: 1rem; color: #264a86; box-shadow: 0 0 12px #a1c4fd;"><h3>Top Score</h3><h2>{df["Score"].max():.1f}%</h2></div>', unsafe_allow_html=True)
cols[2].markdown(f'<div style="background: linear-gradient(135deg, #c2ffd8, #e0f9b5); border-radius: 12px; padding: 1rem; color: #256057; box-shadow: 0 0 12px #a1d2b8;"><h3>Total Evaluated</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)

st.subheader("Candidates Suitability Distribution")
col1, col2 = st.columns(2)
with col1:
    st.bar_chart(df["Suitability"].value_counts(), use_container_width=True)
with col2:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    counts = df["Suitability"].value_counts()
    colors = ["#fbc2eb", "#a1c4fd", "#c2ffd8"]
    ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
    st.pyplot(fig)

all_missing = ",".join(df["Missing Skills"].dropna())
skills_list = [s.strip() for s in all_missing.split(",") if s.strip()]
freq = Counter(skills_list)
freq_df = pd.DataFrame(freq.items(), columns=["Skill", "Frequency"]).sort_values(by="Frequency", ascending=False)
st.subheader("Missing Skills Frequency")
st.dataframe(freq_df)

if not freq_df.empty:
    st.info(f"Most candidates missing **{freq_df.iloc[0]['Skill']}** – consider a workshop or training.")

search_text = st.text_input("Search by Resume Name, Candidate Name or Skill")
suitability_filter = st.multiselect("Filter by Suitability", options=["High", "Medium", "Low"], default=["High","Medium","Low"])
filtered_df = df[
    (df["Suitability"].isin(suitability_filter)) &
    (
        df["Resume Name"].str.lower().str.contains(search_text.lower()) |
        df["Candidate Name"].str.lower().str.contains(search_text.lower()) |
        df["Matched Skills"].str.lower().str.contains(search_text.lower())
    )
]
st.markdown(create_download_link(filtered_df), unsafe_allow_html=True)

for idx, row in filtered_df.iterrows():
    initials = row["Initials"]
    col1, col2, col3, col4 = st.columns([0.15,3,1,1])
    with col1:
        st.markdown(f"<div style='background:#a1c4fd;color:#fff;border-radius:50%;width:35px;height:35px;display:flex;align-items:center;justify-content:center;font-weight:700'>{initials}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"**{row.get('Candidate Name','N/A')}**  \n{row['Resume Name']}")
        st.markdown(f"Score: {row['Score']}%")
    with col3:
        color_map = {"High": "#4CAF50", "Medium": "#FF9800", "Low": "#F44336"}
        st.markdown(f"<span style='padding:5px 10px;border-radius:15px;background-color:{color_map[row['Suitability']]};color:#fff;font-weight:bold'>{row['Suitability']}</span>", unsafe_allow_html=True)
    with col4:
        if row["Resume Name"] in st.session_state['shortlist']:
            if st.button("Remove Shortlist", key=f"remove_{idx}"):
                st.session_state['shortlist'].remove(row['Resume Name'])
        else:
            if st.button("Add to shortlist", key=f"add_{idx}"):
                st.session_state['shortlist'].add(row['Resume Name'])
# This is the new part to save shortlisted candidates as CSV and show Download Button
if st.session_state['shortlist']:
    shortlist_df = df[df['Resume Name'].isin(st.session_state['shortlist'])]
    st.markdown(create_download_link(shortlist_df, filename="shortlisted_candidates.csv"), unsafe_allow_html=True)
    if st.button("Clear Shortlist"):
        st.session_state['shortlist'].clear()

with st.expander("Show candidate details in shortlisted"):
    if st.session_state['shortlist']:
        for res in st.session_state['shortlist']:
            res_row = df[df['Resume Name'] == res].iloc[0]
            st.markdown(f"<strong>{res_row['Candidate Name']}</strong> - {res_row['Resume Name']}", unsafe_allow_html=True)
            st.markdown(f"Score: {res_row['Score']}%")
            st.markdown(f"Missing Skills: {res_row['Missing Skills']}")
            st.markdown(f"Matched Skills: {res_row['Matched Skills']}")
            st.markdown("---")

# Animated progress bar example (optional, use in upload page)
# import time
# def show_progress_bar():
#     progress_bar = st.progress(0)
#     for i in range(100):
#         time.sleep(0.01)
#         progress_bar.progress(i+1)
#     st.success("All resumes processed!")
