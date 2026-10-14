"""Streamlit UI for the AI Resume Screener."""

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from screener import DEFAULT_MODEL, extract_text, get_client, screen_resume

load_dotenv()

st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")
st.title("📄 AI Resume Screener")
st.caption("Rank resumes against a job description. Decision support only: a human should make the final call.")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Gemini model", value=DEFAULT_MODEL)
    min_score = st.slider("Shortlist threshold", 0, 100, 70)
    st.markdown("---")
    st.markdown("**Fairness:** the model is instructed to ignore name, gender, age, and other protected traits. "
                "Always review results manually before acting on them.")

col1, col2 = st.columns([1, 1])
with col1:
    jd = st.text_area("Job description", height=300, placeholder="Paste the full job description here...")
    must_haves = st.text_area("Must-have requirements (optional)", height=100,
                              placeholder="e.g. 3+ years Python, AWS experience")
with col2:
    files = st.file_uploader("Upload resumes (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"],
                             accept_multiple_files=True)
    st.write(f"{len(files)} file(s) selected" if files else "No files yet")

if st.button("Screen resumes", type="primary", disabled=not (jd.strip() and files)):
    try:
        client = get_client()
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    results, errors = [], []
    progress = st.progress(0.0, text="Starting...")
    for i, f in enumerate(files, start=1):
        progress.progress((i - 1) / len(files), text=f"Screening {f.name} ({i}/{len(files)})")
        try:
            text = extract_text(f.name, f.getvalue())
            res = screen_resume(client, jd, text, model=model, must_haves=must_haves)
            res["file"] = f.name
            results.append(res)
        except Exception as e:  # keep going if one resume fails
            errors.append(f"{f.name}: {e}")
    progress.progress(1.0, text="Done")

    st.session_state["results"] = sorted(results, key=lambda r: r["score"], reverse=True)
    st.session_state["errors"] = errors

for err in st.session_state.get("errors", []):
    st.warning(err)

results = st.session_state.get("results", [])
if results:
    st.subheader("Ranked candidates")
    df = pd.DataFrame([{
        "Rank": i + 1,
        "Candidate": r["candidate_name"],
        "File": r["file"],
        "Score": r["score"],
        "Recommendation": r["recommendation"],
        "Years exp.": r["years_experience"],
        "Matched skills": ", ".join(r["matched_skills"]),
        "Missing skills": ", ".join(r["missing_skills"]),
        "Shortlisted": r["score"] >= min_score,
    } for i, r in enumerate(results)])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="screening_results.csv", mime="text/csv")

    st.subheader("Details")
    for r in results:
        with st.expander(f"{r['candidate_name']} — {r['score']}/100 — {r['recommendation']}"):
            st.write(r["summary"])
            a, b = st.columns(2)
            a.markdown("**Strengths**\n" + "\n".join(f"- {s}" for s in r["strengths"]))
            b.markdown("**Concerns**\n" + "\n".join(f"- {s}" for s in r["concerns"]))
            st.markdown("**Suggested interview questions**\n" + "\n".join(f"{n}. {q}" for n, q in enumerate(r["interview_questions"], 1)))
