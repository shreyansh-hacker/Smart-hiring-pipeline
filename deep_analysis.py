"""Deep analysis of sample candidates to inform feature engineering and honeypot detection."""
import sys
import json
from collections import Counter, defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

with open(r'd:\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\sample_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

print(f"Total sample candidates: {len(candidates)}")
print()

# ===== TITLE DISTRIBUTION =====
titles = Counter(c['profile']['current_title'] for c in candidates)
print("=== TITLE DISTRIBUTION ===")
for title, count in titles.most_common():
    print(f"  {title}: {count}")

# ===== COUNTRY DISTRIBUTION =====
countries = Counter(c['profile']['country'] for c in candidates)
print("\n=== COUNTRY DISTRIBUTION ===")
for country, count in countries.most_common():
    print(f"  {country}: {count}")

# ===== INDUSTRY DISTRIBUTION =====
industries = Counter(c['profile']['current_industry'] for c in candidates)
print("\n=== INDUSTRY DISTRIBUTION ===")
for ind, count in industries.most_common():
    print(f"  {ind}: {count}")

# ===== EXPERIENCE STATS =====
exps = [c['profile']['years_of_experience'] for c in candidates]
print(f"\n=== EXPERIENCE STATS ===")
print(f"  Min: {min(exps)}, Max: {max(exps)}, Mean: {sum(exps)/len(exps):.1f}")

# ===== SKILL ANALYSIS =====
all_skills = []
for c in candidates:
    for s in c.get('skills', []):
        all_skills.append(s['name'])
skill_counts = Counter(all_skills)
print(f"\n=== TOP 30 SKILLS ===")
for skill, count in skill_counts.most_common(30):
    print(f"  {skill}: {count}")

# ===== HONEYPOT DETECTION PATTERNS =====
print("\n=== POTENTIAL HONEYPOT PATTERNS ===")
for c in candidates:
    cid = c['candidate_id']
    signals = c['redrob_signals']
    
    # Check salary min > max
    sal = signals['expected_salary_range_inr_lpa']
    if sal['min'] > sal['max']:
        print(f"  {cid}: Salary min ({sal['min']}) > max ({sal['max']})")
    
    # Check signup after last_active
    signup = signals.get('signup_date', '')
    last_active = signals.get('last_active_date', '')
    if signup and last_active and signup > last_active:
        print(f"  {cid}: signup_date ({signup}) > last_active_date ({last_active})")
    
    # Check expert skills with 0 duration
    for s in c.get('skills', []):
        if s['proficiency'] in ('advanced', 'expert') and s.get('duration_months', 0) == 0:
            print(f"  {cid}: {s['name']} proficiency={s['proficiency']} but duration=0")
    
    # Check title-summary mismatch (templated summaries)
    summary = c['profile'].get('summary', '')
    title = c['profile'].get('current_title', '')
    if 'marketing manager' in summary.lower() and 'marketing' not in title.lower():
        pass  # Very common - template text
    
    # Check career description mismatch with title
    for job in c.get('career_history', []):
        job_title = job.get('title', '')
        desc = job.get('description', '')
        # Flag if title is engineering but description is completely unrelated
        
    # Check profile_completeness vs actual completeness
    # Check assessment scores vs proficiency claims

# ===== TEMPLATE SUMMARY DETECTION =====
print("\n=== TEMPLATE SUMMARY PATTERNS ===")
summary_starts = Counter()
for c in candidates:
    summary = c['profile'].get('summary', '')
    first_sentence = summary.split('.')[0] if summary else ''
    if len(first_sentence) > 20:
        # Normalize
        key = first_sentence[:60]
        summary_starts[key] += 1

for pattern, count in summary_starts.most_common(10):
    print(f"  [{count}x] {pattern}...")

# ===== SKILL PROFICIENCY VS ASSESSMENT =====
print("\n=== SKILL PROFICIENCY vs ASSESSMENT SCORE MISMATCHES ===")
for c in candidates[:20]:
    cid = c['candidate_id']
    assessments = c['redrob_signals'].get('skill_assessment_scores', {})
    for s in c.get('skills', []):
        if s['name'] in assessments:
            score = assessments[s['name']]
            prof = s['proficiency']
            if prof in ('advanced', 'expert') and score < 40:
                print(f"  {cid}: {s['name']} proficiency={prof} but assessment={score}")
            elif prof == 'beginner' and score > 80:
                print(f"  {cid}: {s['name']} proficiency={prof} but assessment={score}")

# ===== CAREER HISTORY ANALYSIS =====
print("\n=== CAREER HISTORY ANOMALIES ===")
for c in candidates[:50]:
    cid = c['candidate_id']
    history = c.get('career_history', [])
    
    # Check total career duration vs years_of_experience
    total_months = sum(j.get('duration_months', 0) for j in history)
    claimed_years = c['profile'].get('years_of_experience', 0)
    
    if total_months > 0 and abs(total_months/12 - claimed_years) > 3:
        print(f"  {cid}: claimed {claimed_years}yr but career_history sums to {total_months/12:.1f}yr")
    
    # Check for overlapping dates
    for i, j1 in enumerate(history):
        for j2 in history[i+1:]:
            s1 = j1.get('start_date', '')
            e1 = j1.get('end_date', '')
            s2 = j2.get('start_date', '')
            e2 = j2.get('end_date', '')
            # Simple overlap check
            if e1 and s2 and s1 and s1 < e2 if e2 else True:
                pass  # would need proper date parsing

# ===== COMPANY ANALYSIS =====
print("\n=== COMPANY DISTRIBUTION ===")
companies = Counter()
for c in candidates:
    companies[c['profile']['current_company']] += 1
for company, count in companies.most_common(15):
    print(f"  {company}: {count}")

# ===== AI/ML RELEVANT TITLE ANALYSIS =====
print("\n=== AI/ML RELEVANT TITLES ===")
ai_titles = ['ML Engineer', 'Data Scientist', 'AI Engineer', 'Machine Learning', 
             'NLP Engineer', 'Deep Learning', 'Research Scientist', 'Data Engineer',
             'Backend Engineer', 'Software Engineer', 'Senior Machine Learning']
for c in candidates:
    title = c['profile']['current_title']
    if any(t.lower() in title.lower() for t in ['ml', 'ai', 'machine learning', 'data scientist', 'nlp', 'deep learning']):
        print(f"  {c['candidate_id']}: {title} ({c['profile']['years_of_experience']}yr) at {c['profile']['current_company']}")

# ===== WORK MODE DISTRIBUTION =====
print("\n=== WORK MODE DISTRIBUTION ===")
modes = Counter(c['redrob_signals']['preferred_work_mode'] for c in candidates)
for mode, count in modes.most_common():
    print(f"  {mode}: {count}")

# ===== NOTICE PERIOD DISTRIBUTION =====
print("\n=== NOTICE PERIOD DISTRIBUTION ===")
notices = Counter(c['redrob_signals']['notice_period_days'] for c in candidates)
for np, count in sorted(notices.items()):
    print(f"  {np} days: {count}")
