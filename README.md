# Smart Hiring Pipeline: Candidate Discovery & Ranking

A highly optimized and robust candidate discovery and ranking system built for the Redrob Intelligent Candidate Discovery & Ranking Challenge. It is designed to score and rank candidates against a job description, identify and filter out honeypot profiles, integrate complex behavioral engagement signals, and generate non-templated, contextual reasoning for each pick.

---

## Key Features

1. **Hybrid Scoring Engine**: Matches candidates based on 8 core dimensions loaded from `config.yaml`:
   - **Semantic Similarity** (weight: 0.15): Cosine similarity between TF-IDF vector representations of the Job Description and candidate profiles.
   - **Skills Match** (weight: 0.25): Required and desired skill match weighted by proficiency and verified skill assessment scores.
   - **Experience Match** (weight: 0.15): Perfect alignment with the 5–9 years experience range, scaling down for over/under-qualified candidates.
   - **Title and Career Trajectory** (weight: 0.15): Evaluates role relevance, average job tenure stability, and hands-on developer signal.
   - **Behavioral Engagement** (weight: 0.15): Modulates ranking based on profile completeness, activity level, response rate, and phone/email/LinkedIn verifications.
   - **Location Compatibility** (weight: 0.05): Prioritizes candidates located in target hubs (Noida, Pune, Bangalore, Delhi NCR, etc.) or willing to relocate.
   - **Notice Period Compatibility** (weight: 0.05): Scores shorter notice periods higher (preferred ≤ 30 days).
   - **Salary Compatibility** (weight: 0.05): Ensures salary expectations match standard budget ranges.

2. **Honeypot Filter**: Explicit checks for profile contradictions to disqualify fraudulent or keyword-stuffed records completely:
   - Expected salary min > max.
   - Profile signup date later than last active date.
   - Advanced/Expert proficiency in skills with 0 months of duration.
   - Contradictory career histories or claimed years of experience.
   - Templated/mismatched summaries (e.g. summary stating "marketing manager" while title is "Accountant" or "Operations").

3. **Multiplicative Penalties**: Downweights candidates with:
   - Consulting-only careers (TCS, Wipro, Infosys, etc.) without prior product company experience.
   - Stale/inactive profiles (>180 days since last activity).
   - Long notice periods (>60 days).
   - Missing basic contact or summary details.

4. **Context-Aware Reasoning**: Dynamic, non-templated reasoning generation using specific profile facts (years of experience, role titles, companies, key matched skills, location) to satisfy the validator and Stage 4 human review constraints.

---

## Setup & Installation

### Prerequisite
Make sure Python 3.8+ is installed on your system.

### Install Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

---

## How to Run

To run the ranking pipeline end-to-end and generate the submission file, execute:

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

### Options
- `--candidates`: Path to the input candidate pool (JSONL format, also supports gzipped `.jsonl.gz` format).
- `--out`: Destination path for the output CSV.
- `--config`: (Optional) Path to a custom `config.yaml` configuration file.

The script runs efficiently and completes processing of **100,000 candidates in under 40 seconds** on standard CPU platforms, requiring **less than 1 GB of RAM**.

### Launching the Web Portal (Sandbox Demo)
To start the interactive Streamlit web dashboard:
```bash
streamlit run app.py
```
This will open a local web server at `http://localhost:8501`, where you can:
- Adjust scoring weights and thresholds dynamically.
- Upload candidate `.jsonl` or `.json` files.
- Run rankings instantly on the bundled sample candidates dataset.
- View data distribution charts (top job titles and locations).
- Download the generated `submission.csv`.

---

## Repository Files

- `rank.py`: Core scoring, honeypot-filtering, ranking, and reasoning script.
- `app.py`: Streamlit-based web portal and interactive sandbox interface.
- `sample_candidates.json`: Bundled subset of candidate records for quick sandbox demo.
- `candidate-ranking/config.yaml`: Scoring weights, thresholds, and penalty config.
- `submission_metadata.yaml`: Portal metadata for validator replication.
- `requirements.txt`: Python package requirements.
