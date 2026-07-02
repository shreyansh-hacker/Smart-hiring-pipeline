import streamlit as st
import os
import json
import math
import pandas as pd
import yaml
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import the core logic from rank.py to maintain consistency
from rank import (
    load_config, read_jd_text, detect_honeypot, is_consulting_only, build_candidate_text,
    score_experience, score_skills, score_behavior, score_location,
    score_notice_period, score_salary, score_career_trajectory,
    generate_reasoning
)

# Page configuration
st.set_page_config(
    page_title="Redrob Talent Intelligence Sandbox",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium UI Styling (Layout tweaks)
st.markdown("""
<style>
    /* Custom font style if desired */
    h1, h2, h3 {
        font-family: 'Outfit', 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Redrob AI Talent Intelligence Portal")
st.caption("Intelligent Candidate Discovery & Ranking Engine Sandbox Demo")

# Load baseline config
config = load_config(None)

# ----------------- SIDEBAR: PARAMETERS & CONFIGS -----------------
st.sidebar.header("⚙️ Model Configuration")

# Scoring Weights tuning
st.sidebar.subheader("Scoring Dimension Weights")
weights = config.get("weights", {})
w_semantic = st.sidebar.slider("Semantic Similarity", 0.0, 1.0, float(weights.get("semantic_similarity", 0.15)), 0.05)
w_skills = st.sidebar.slider("Skills Match", 0.0, 1.0, float(weights.get("skills_match", 0.25)), 0.05)
w_exp = st.sidebar.slider("Experience Match", 0.0, 1.0, float(weights.get("experience_match", 0.15)), 0.05)
w_trajectory = st.sidebar.slider("Career Trajectory", 0.0, 1.0, float(weights.get("title_and_career_trajectory", 0.15)), 0.05)
w_behavior = st.sidebar.slider("Behavioral Engagement", 0.0, 1.0, float(weights.get("behavioral_engagement", 0.15)), 0.05)
w_loc = st.sidebar.slider("Location Compatibility", 0.0, 1.0, float(weights.get("location_compatibility", 0.05)), 0.05)
w_notice = st.sidebar.slider("Notice Period Compatibility", 0.0, 1.0, float(weights.get("notice_period_compatibility", 0.05)), 0.05)
w_sal = st.sidebar.slider("Salary Compatibility", 0.0, 1.0, float(weights.get("salary_compatibility", 0.05)), 0.05)

# Validate sum of weights
total_weight = w_semantic + w_skills + w_exp + w_trajectory + w_behavior + w_loc + w_notice + w_sal
st.sidebar.markdown(f"**Total Weight Sum**: `{total_weight:.2f}`")
if not math.isclose(total_weight, 1.0, abs_tol=0.01):
    st.sidebar.warning("⚠️ Weights should sum to 1.0 for normalized scoring.")

# Threshold Configuration
st.sidebar.subheader("Experience & Notice Thresholds")
thresholds = config.get("thresholds", {})
exp_min = st.sidebar.number_input("Ideal Exp Min (Years)", 0, 20, int(thresholds.get("ideal_experience_min_years", 5)))
exp_max = st.sidebar.number_input("Ideal Exp Max (Years)", 0, 30, int(thresholds.get("ideal_experience_max_years", 9)))
notice_pref = st.sidebar.number_input("Max Notice Days Preferred", 0, 180, int(thresholds.get("max_notice_period_days_preferred", 30)))
notice_acc = st.sidebar.number_input("Max Notice Days Acceptable", 0, 180, int(thresholds.get("max_notice_period_days_acceptable", 60)))

# Dynamic config override
ui_config = {
    "features": config.get("features", {}),
    "thresholds": {
        "ideal_experience_min_years": exp_min,
        "ideal_experience_max_years": exp_max,
        "absolute_min_experience_years": thresholds.get("absolute_min_experience_years", 3),
        "absolute_max_experience_years": thresholds.get("absolute_max_experience_years", 15),
        "max_notice_period_days_preferred": notice_pref,
        "max_notice_period_days_acceptable": notice_acc,
        "stale_profile_days": thresholds.get("stale_profile_days", 180)
    },
    "weights": {
        "semantic_similarity": w_semantic,
        "skills_match": w_skills,
        "experience_match": w_exp,
        "title_and_career_trajectory": w_trajectory,
        "behavioral_engagement": w_behavior,
        "location_compatibility": w_loc,
        "notice_period_compatibility": w_notice,
        "salary_compatibility": w_sal
    },
    "penalties": config.get("penalties", {})
}

# ----------------- MAIN PANEL: PIPELINE EXECUTION -----------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Job Description Details")
    # Read the local JD file or input custom text
    default_jd_path = "job_description.docx"
    default_jd = read_jd_text(default_jd_path)
    
    jd_input = st.text_area("Job Description Context", default_jd, height=220)

with col2:
    st.subheader("📂 Upload Candidate Pool")
    uploaded_file = st.file_uploader("Upload candidates.jsonl or sample_candidates.json", type=["jsonl", "json"])
    
    # Use bundled sample data if no file is uploaded
    sample_btn = st.button("🚀 Run with Bundled Sample Candidates")

candidates = []

# Load candidates from upload or sample
if uploaded_file is not None:
    try:
        content = uploaded_file.getvalue().decode("utf-8")
        if uploaded_file.name.endswith(".jsonl"):
            for line in content.splitlines():
                if line.strip():
                    candidates.append(json.loads(line))
        else:
            candidates = json.loads(content)
        st.success(f"Successfully loaded {len(candidates)} candidates from file.")
    except Exception as e:
        st.error(f"Error loading candidates: {e}")
elif sample_btn:
    sample_path = "d:/[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/sample_candidates.json"
    if not os.path.exists(sample_path):
        sample_path = "sample_candidates.json"
    if os.path.exists(sample_path):
        try:
            with open(sample_path, "r", encoding="utf-8") as f:
                candidates = json.load(f)
            st.success(f"Successfully loaded {len(candidates)} candidates from {sample_path}.")
        except Exception as e:
            st.error(f"Error loading sample candidates: {e}")
    else:
        st.error("Sample candidates file not found in path.")

# ----------------- SCORING & VISUALIZATION -----------------
if candidates:
    st.markdown("---")
    st.subheader("📊 Ranking Engine Execution")
    
    with st.spinner("Processing candidate matching..."):
        # 1. Semantic Similarity using TF-IDF
        corpus = [jd_input]
        for c in candidates:
            corpus.append(build_candidate_text(c))
            
        vectorizer = TfidfVectorizer(stop_words='english', max_features=15000, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Determine max date for activity calculations
        max_active_date = "2026-07-02"
        for c in candidates[:200]:
            act = c.get("redrob_signals", {}).get("last_active_date", "")
            if act and act > max_active_date:
                max_active_date = act
                
        scored_candidates = []
        honeypot_count = 0
        
        for idx, c in enumerate(candidates):
            cid = c["candidate_id"]
            profile = c.get("profile", {})
            signals = c.get("redrob_signals", {})
            skills = c.get("skills", [])
            career_history = c.get("career_history", [])
            
            # Honeypot Check
            honeypot_detected, honeypot_reason = detect_honeypot(c)
            if honeypot_detected:
                honeypot_count += 1
                
            # Score Components
            semantic_score = similarities[idx]
            skill_score = score_skills(skills, signals)
            exp_score = score_experience(profile.get("years_of_experience", 0.0), ui_config["thresholds"])
            trajectory_score = score_career_trajectory(c)
            behavior_score = score_behavior(signals, max_active_date)
            location_score = score_location(profile.get("location", ""), profile.get("country", ""), signals.get("willing_to_relocate", False))
            notice_score = score_notice_period(signals.get("notice_period_days", 180), ui_config["thresholds"])
            sal_score = score_salary(signals.get("expected_salary_range_inr_lpa", {}))
            
            # Base score
            base_score = (
                semantic_score * ui_config["weights"]["semantic_similarity"] +
                skill_score * ui_config["weights"]["skills_match"] +
                exp_score * ui_config["weights"]["experience_match"] +
                trajectory_score * ui_config["weights"]["title_and_career_trajectory"] +
                behavior_score * ui_config["weights"]["behavioral_engagement"] +
                location_score * ui_config["weights"]["location_compatibility"] +
                notice_score * ui_config["weights"]["notice_period_compatibility"] +
                sal_score * ui_config["weights"]["salary_compatibility"]
            )
            
            # Multiplicative penalties
            multiplier = 1.0
            if honeypot_detected:
                multiplier *= ui_config["penalties"].get("honeypot_flag", 0.0)
            if is_consulting_only(career_history):
                multiplier *= ui_config["penalties"].get("consulting_only_career", 0.6)
            
            # Notice Period Penalty
            if signals.get("notice_period_days", 0) > ui_config["thresholds"]["max_notice_period_days_acceptable"]:
                multiplier *= ui_config["penalties"].get("high_notice_period", 0.8)
                
            # Profile completeness penalty
            if not profile.get("location") or not profile.get("summary") or signals.get("profile_completeness_score", 100.0) < 50.0:
                multiplier *= ui_config["penalties"].get("missing_basic_info", 0.7)
                
            final_score = base_score * multiplier
            
            scored_candidates.append({
                "candidate_id": cid,
                "name": profile.get("anonymized_name", "Anonymous"),
                "title": profile.get("current_title", "N/A"),
                "experience": profile.get("years_of_experience", 0.0),
                "location": profile.get("location", "N/A"),
                "score": round(final_score, 4),
                "honeypot": honeypot_detected,
                "honeypot_reason": honeypot_reason,
                "candidate_data": c
            })
            
        # Sort descending by score, ascending by candidate_id
        scored_candidates.sort(key=lambda x: (-x["score"], x["candidate_id"]))
        
        # Display Key Analytics Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Candidates", f"{len(candidates):,}")
        with m2:
            st.metric("Honeypots Disqualified", f"{honeypot_count:,}", delta=f"-{honeypot_count:,} (Filtered)", delta_color="inverse")
        with m3:
            st.metric("Honeypot Filter Rate", f"{((honeypot_count / len(candidates)) * 100):.1f}%")

        # Build Output DataFrame for the Top 100
        output_rows = []
        top_n = min(100, len(scored_candidates))
        
        for rank_idx in range(top_n):
            item = scored_candidates[rank_idx]
            cand = item["candidate_data"]
            score = item["score"]
            cid = item["candidate_id"]
            
            # Generate unique reasoning
            reason = generate_reasoning(cand, score, item["honeypot"])
            output_rows.append({
                "Rank": rank_idx + 1,
                "Candidate ID": cid,
                "Name": item["name"],
                "Current Title": item["title"],
                "Score": score,
                "Location": item["location"],
                "Reasoning": reason
            })
            
        df_results = pd.DataFrame(output_rows)
        
        # Download Section
        st.subheader("📥 Export Final Rankings")
        csv_data = df_results[["Candidate ID", "Rank", "Score", "Reasoning"]].rename(
            columns={"Candidate ID": "candidate_id", "Rank": "rank", "Score": "score", "Reasoning": "reasoning"}
        ).to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="Download submission.csv",
            data=csv_data,
            file_name="submission.csv",
            mime="text/csv"
        )
        
        # Display Rankings Table
        st.subheader("🏆 Top Ranked Candidates (Top 100)")
        st.dataframe(df_results, use_container_width=True)
        
        # Charts section
        st.markdown("---")
        st.subheader("📈 Candidate Pool Distribution (Top 100)")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Top Job Titles in Final Selection**")
            title_counts = df_results["Current Title"].value_counts()
            st.bar_chart(title_counts)
        with c2:
            st.markdown("**Top Locations in Final Selection**")
            loc_counts = df_results["Location"].value_counts().head(10)
            st.bar_chart(loc_counts)

else:
    st.info("💡 Please upload a candidate file or click 'Run with Bundled Sample Candidates' to start the pipeline.")
