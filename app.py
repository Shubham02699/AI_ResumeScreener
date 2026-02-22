"""
app.py
AI Resume Screener — Main Streamlit Application
Run with: streamlit run app.py
"""

import streamlit as st
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from resume_parser import extract_text, get_candidate_name
from ats_scorer import score_all_resumes_ats
from ai_scorer import score_all_resumes_ai
from hybrid_scorer import combine_scores, add_final_score_ats_only, add_final_score_ai_only
from utils import (
    results_to_dataframe,
    export_to_csv,
    export_to_excel,
    get_score_color,
    validate_job_description,
)

# ─────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🤖",
    layout="wide",
)

# ─────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────
st.markdown(
    """
    <style>
    .top-candidate { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 8px; border-radius: 4px; }
    .score-badge { font-size: 1.4rem; font-weight: bold; }
    .section-header { font-size: 1.1rem; font-weight: 600; color: #444; margin-bottom: 0.3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────
# Header
# ─────────────────────────────────────────
st.title("🤖 AI Resume Screener")
st.caption("Screen, analyse, and rank resumes intelligently — powered by TF-IDF and Google Gemini.")
st.divider()

# ─────────────────────────────────────────
# Sidebar — Configuration
# ─────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    mode = st.radio(
        "Scoring Mode",
        options=["ATS Only", "AI Only", "Hybrid"],
        index=2,
        help=(
            "**ATS Only** — Fast keyword matching (offline)\n\n"
            "**AI Only** — Deep contextual analysis via Gemini\n\n"
            "**Hybrid** — Best of both (recommended)"
        ),
    )

    if mode == "Hybrid":
        st.markdown("**Score Weights**")
        ats_weight = st.slider("ATS Weight (%)", 0, 100, 40, step=5) / 100
        ai_weight = round(1 - ats_weight, 2)
        st.caption(f"AI Weight: {int(ai_weight * 100)}%")
    else:
        ats_weight = 0.4
        ai_weight = 0.6

    st.divider()
    st.caption("Max 50 resumes per session · PDF & DOCX supported")

# ─────────────────────────────────────────
# Main Layout — Two columns
# ─────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<p class="section-header">📋 Job Description</p>', unsafe_allow_html=True)
    job_description = st.text_area(
        label="Paste the job description here",
        height=280,
        placeholder="e.g. We are looking for a Senior Python Developer with 5+ years experience in Django, REST APIs, and cloud infrastructure (AWS/GCP)...",
        label_visibility="collapsed",
    )

with col_right:
    st.markdown('<p class="section-header">📁 Upload Resumes</p>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        label="Upload resumes",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Upload between 1 and 50 resume files (PDF or DOCX).",
    )

    if uploaded_files:
        if len(uploaded_files) > 50:
            st.error("❌ Maximum 50 resumes allowed per session.")
        else:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            with st.expander("View uploaded files"):
                for f in uploaded_files:
                    st.text(f"• {f.name}")

# ─────────────────────────────────────────
# Run Analysis Button
# ─────────────────────────────────────────
st.divider()
run_col, _ = st.columns([1, 3])
with run_col:
    run_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

# ─────────────────────────────────────────
# Analysis Logic
# ─────────────────────────────────────────
if run_btn:

    # --- Validation ---
    jd_error = validate_job_description(job_description)
    if jd_error:
        st.error(f"❌ {jd_error}")
        st.stop()

    if not uploaded_files:
        st.error("❌ Please upload at least one resume file.")
        st.stop()

    if len(uploaded_files) > 50:
        st.error("❌ Maximum 50 resumes allowed per session.")
        st.stop()

    # --- Parse all resumes ---
    st.info("📖 Reading and parsing resume files...")
    resumes = []
    parse_errors = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(tmpdir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            try:
                text = extract_text(file_path)
                name = get_candidate_name(file_path)
                resumes.append({"name": name, "text": text})
            except ValueError as e:
                parse_errors.append(str(e))

    if parse_errors:
        for err in parse_errors:
            st.warning(f"⚠️ {err}")

    if not resumes:
        st.error("❌ No readable resumes found. Please check your files and try again.")
        st.stop()

    # --- Scoring ---
    results = []

    if mode == "ATS Only":
        with st.spinner("⚙️ Running ATS analysis..."):
            ats_results = score_all_resumes_ats(job_description, resumes)
            results = add_final_score_ats_only(ats_results)

    elif mode == "AI Only":
        progress_bar = st.progress(0, text="Starting AI analysis...")

        def ai_progress(current, total, name):
            pct = current / total
            progress_bar.progress(pct, text=f"🤖 Analysing {name} ({current}/{total})...")

        try:
            ai_results = score_all_resumes_ai(job_description, resumes, progress_callback=ai_progress)
            results = add_final_score_ai_only(ai_results)
            progress_bar.empty()
        except EnvironmentError as e:
            st.error(f"❌ {e}")
            st.stop()

    else:  # Hybrid
        with st.spinner("⚙️ Running ATS analysis..."):
            ats_results = score_all_resumes_ats(job_description, resumes)

        progress_bar = st.progress(0, text="Starting AI analysis...")

        def hybrid_progress(current, total, name):
            pct = current / total
            progress_bar.progress(pct, text=f"🤖 AI scoring {name} ({current}/{total})...")

        try:
            ai_results = score_all_resumes_ai(job_description, resumes, progress_callback=hybrid_progress)
            progress_bar.empty()
        except EnvironmentError as e:
            st.error(f"❌ {e}")
            st.stop()

        results = combine_scores(ats_results, ai_results, ats_weight=ats_weight, ai_weight=ai_weight)

    # ─────────────────────────────────────
    # Display Results
    # ─────────────────────────────────────
    st.divider()
    st.subheader(f"📊 Results — {mode} Mode ({len(results)} candidates)")

    # Top 3 podium
    top3 = results[:3]
    medals = ["🥇", "🥈", "🥉"]
    cols = st.columns(len(top3))
    for i, (col, candidate) in enumerate(zip(cols, top3)):
        with col:
            score = candidate["final_score"]
            color = get_score_color(score)
            st.markdown(
                f"""
                <div style="border:2px solid {color}; border-radius:10px; padding:16px; text-align:center;">
                    <div style="font-size:2rem;">{medals[i]}</div>
                    <div style="font-weight:700; font-size:1rem; margin:6px 0;">{candidate['name']}</div>
                    <div class="score-badge" style="color:{color};">{score:.1f}</div>
                    <div style="font-size:0.75rem; color:#888;">Final Score</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Full ranked table
    df = results_to_dataframe(results, mode)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Detailed cards for each candidate
    with st.expander("📄 Detailed Candidate Cards"):
        for rank, r in enumerate(results, start=1):
            medal = medals[rank - 1] if rank <= 3 else f"#{rank}"
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{medal} {r['name']}**")
                    if r.get("ai_reason"):
                        st.caption(r["ai_reason"])
                with c2:
                    score = r["final_score"]
                    color = get_score_color(score)
                    st.markdown(
                        f'<div style="text-align:right;"><span style="color:{color};font-size:1.5rem;font-weight:bold;">{score:.1f}</span><br><span style="font-size:0.75rem;color:#888;">Final</span></div>',
                        unsafe_allow_html=True,
                    )
                    if r.get("ats_score") is not None:
                        st.caption(f"ATS: {r['ats_score']:.1f}")
                    if r.get("ai_score") is not None:
                        st.caption(f"AI: {r['ai_score']:.1f}")
                st.divider()

    # ─────────────────────────────────────
    # Export
    # ─────────────────────────────────────
    st.subheader("💾 Export Results")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        csv_data = export_to_csv(df)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="resume_screening_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with exp_col2:
        excel_data = export_to_excel(df)
        st.download_button(
            label="⬇️ Download Excel",
            data=excel_data,
            file_name="resume_screening_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
