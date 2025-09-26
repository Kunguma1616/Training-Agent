import os
import json
import time
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple
import ast
from pathlib import Path
from collections import defaultdict

import streamlit as st
from retell import Retell

# ==============================
# ENV / DEMO CREDENTIALS
# ==============================
ADMIN_EMAIL = os.getenv("ASPECT_ADMIN_EMAIL", "Alex.Bacon@aspect.co.uk")
ADMIN_PASSWORD = os.getenv("ASPECT_ADMIN_PASSWORD", "Alex.Bacon#123")

COMMON_USER_EMAIL = os.getenv("ASPECT_USER_EMAIL", "user@aspect.co.uk")
COMMON_USER_PASSWORD = os.getenv("ASPECT_USER_PASSWORD", "Aspect#123")

# --- API KEY CONFIGURATION ---
RETELL_API_KEY = os.getenv("RETELL_API_KEY", "key_0700957698e5713c93f7a4b1c267")
RETELL_AGENT_ID = os.getenv("RETELL_AGENT_ID", "agent_c3f46c38e6348846dc844fe9d1")
FROM_NUMBER = os.getenv("RETELL_FROM_NUMBER", "+441479787918")

# --- Branding / Footer ---
COMPANY_NAME = os.getenv("ASPECT_COMPANY_NAME", "Aspect Maintenance Services Ltd.")
SUPPORT_EMAIL = os.getenv("ASPECT_SUPPORT_EMAIL", "support@aspect.co.uk")
SUPPORT_PHONE = os.getenv("ASPECT_SUPPORT_PHONE", "+44 20 1234 5678")

# --- Logo ---
LOGO_FILE = Path(os.getenv("ASPECT_LOGO_FILE", "aspect_maintenance_ltd_logo.jpg"))
LOGO_URL = os.getenv("ASPECT_LOGO_URL", "")

# =================================
# PAGE CONFIG
# =================================
st.set_page_config(
    page_title="Aspect Training Portal",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =================================
# PROFESSIONAL CSS THEME
# =================================
st.markdown("""
<style>
    :root {
        --brand-primary: #1f5eff; /* blue */
        --brand-accent: #0ea5a3;   /* teal */
        --bg-grad-start: #eef2f7;
        --bg-grad-end: #dbe4f0;
        --card-bg: #ffffff;
        --text-main: #1f2937;
        --text-muted: #6b7280;
        --border: #e5e7eb;
        --success: #22c55e;
        --error: #ef4444;
        --warning: #f59e0b;
        --purple1: #667eea;
        --purple2: #764ba2;
        --green1: #28a745;
        --green2: #20c997;
    }
    .stApp {
        background: linear-gradient(180deg, var(--bg-grad-start), var(--bg-grad-end));
        color: var(--text-main);
        font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    }
    .hero {
        background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-accent) 100%);
        border-radius: 18px;
        padding: 1.8rem;
        color: #fff;
        box-shadow: 0 18px 40px rgba(31, 94, 255, 0.18);
        margin: 1.2rem 0;
    }
    .hero h1 { margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: .2px; }
    .hero p { margin: .35rem 0 0 0; opacity: .95; font-weight: 500; }
    .card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.06);
        transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
        min-height: 140px;
        display: flex; 
        flex-direction: column;
        justify-content: space-between;
    }
    .card h3 { margin: 0 0 6px 0; font-weight: 800; color: var(--text-main); }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #eef2ff;
        color: var(--brand-primary); border: 1px solid #dbeafe; font-size: 12px; font-weight: 700; margin-left: 8px; }
    .muted { color: var(--text-muted); font-size: .95rem; line-height: 1.4; }
    .panel {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.06);
        margin-top: 8px;
    }
    .footer {
        margin-top: 32px;
        padding: 24px 12px;
        text-align: center;
        color: var(--text-muted);
        border-top: 1px solid var(--border);
    }
    .footer a { color: var(--brand-primary); text-decoration: none; font-weight: 600; }
    .logo-wrap { display: inline-flex; align-items: center; justify-content: center;
        background: #EEF200; border-radius: 14px; padding: .6rem .9rem; border: 1px solid #1d2a57; margin-right: 12px; }
    .logo-ph { font-weight: 900; color:#1d2a57; letter-spacing: .5px; }
    .title-container {
        background: linear-gradient(135deg, var(--purple1) 0%, var(--purple2) 100%);
        padding: 2rem; border-radius: 18px; margin: 1.2rem auto 1.4rem auto;
        box-shadow: 0 16px 40px rgba(0,0,0,0.25); max-width: 1100px; color:#fff;
    }
    .title-text { text-align: center; font-size: 2.4rem; font-weight: 800; margin: 0; letter-spacing: 0.5px; }
    .subtitle-text { color: rgba(255,255,255,0.92); text-align: center; font-size: 1rem; margin-top: 0.45rem; }
    .level-card {
        background: linear-gradient(135deg, var(--purple1) 0%, var(--purple2) 100%);
        color: white; padding: 1rem; border-radius: 12px; margin: 1rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.18);
    }
    .score-card { background: white; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; box-shadow: 0 2px 12px rgba(0,0,0,0.12); text-align: center; }
    .transcript-box { background: white; padding: 1rem; border-radius: 12px; max-height: 420px; overflow-y: auto; margin: 1rem 0; }
    .customer-msg { color: #e74c3c; font-weight: 700; }
    .trainee-msg { color: #2980b9; font-weight: 700; }
    .trainee-name-card {
        background: linear-gradient(135deg, var(--green1) 0%, var(--green2) 100%);
        color: white; padding: 1.1rem; border-radius: 14px; margin: .8rem 0 .6rem; text-align: center;
        box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }
    .trainee-name-text { font-size: 1.2rem; font-weight: 800; margin: 0; }
    .pill { display:inline-block; padding: .28rem .7rem; border-radius: 999px; background: #fff; border:1px solid #e6e6e6; margin:.25rem .5rem .25rem 0; font-size:.85rem;}
    .stButton > button {
        background: linear-gradient(135deg, var(--purple1) 0%, var(--purple2) 100%);
        color: white; border: none; border-radius: 999px; padding: 0.6rem 1.3rem;
        font-weight: 700; transition: all 0.2s ease; letter-spacing: .3px;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(0,0,0,0.22); }
    
    .red-progress .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, var(--error), #f87171);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# AUTH STATE
# =========================
if "auth_role" not in st.session_state:
    st.session_state.auth_role = None
if "auth_email" not in st.session_state:
    st.session_state.auth_email = None
if "admin_history_loaded" not in st.session_state:
    st.session_state.admin_history_loaded = False

# ==============
# RETELL CLIENT
# ==============
@st.cache_resource
def init_retell():
    try:
        client = Retell(api_key=RETELL_API_KEY)
        return client
    except Exception as e:
        st.error(f"❌ Error initializing Retell client: {e}")
        st.stop()

# ===========================
# LOGIN UX HELPERS
# ===========================
def email_valid(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))

def mask_email(email: str) -> str:
    try:
        name, domain = email.split("@")
        if len(name) <= 2: name_mask = name[0] + "•"
        else: name_mask = name[0] + "•"*(len(name)-2) + name[-1]
        domain_parts = domain.split(".")
        domain_mask = domain_parts[0][0] + "•"*(len(domain_parts[0])-1)
        return f"{name_mask}@{domain_mask}.{'.'.join(domain_parts[1:])}"
    except Exception:
        return email

def render_logo_header():
    st.markdown(
        f"<div class='hero'><h1>{COMPANY_NAME}</h1><p>Training & Evaluation Portal</p></div>",
        unsafe_allow_html=True
    )

def success_card(title: str, subtitle: str = "", details: str = ""):
    st.markdown(
        f"""
        <div class="panel" style="border-left: 4px solid var(--success);">
            <h3 style="margin:0 0 4px 0;">{title}</h3>
            <div class="muted">{subtitle}</div>
            <div style="margin-top:8px;">{details}</div>
        </div>
        """, unsafe_allow_html=True
    )

def error_card(title: str, subtitle: str = "", details: str = ""):
    st.markdown(
        f"""
        <div class="panel" style="border-left: 4px solid var(--error);">
            <h3 style="margin:0 0 4px 0;">{title}</h3>
            <div class="muted">{subtitle}</div>
            <div style="margin-top:8px;">{details}</div>
        </div>
        """, unsafe_allow_html=True
    )

def warn_card(title: str, subtitle: str = "", details: str = ""):
    st.markdown(
        f"""
        <div class="panel" style="border-left: 4px solid var(--warning);">
            <h3 style="margin:0 0 4px 0;">{title}</h3>
            <div class="muted">{subtitle}</div>
            <div style="margin-top:8px;">{details}</div>
        </div>
        """, unsafe_allow_html=True
    )

# ===========================
# UNIFIED LOGIN SYSTEM
# ===========================
def render_login_screen():
    render_logo_header()
    st.markdown("### Sign In")
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign In")
    if submitted:
        if not email_valid(email):
            error_card("Invalid email", details="Please enter a valid email address.")
            return
        if not password:
            error_card("Password required", details="Please enter your password.")
            return
        with st.spinner("Authenticating..."):
            time.sleep(0.5)
        if email.strip().lower() == ADMIN_EMAIL.lower():
            if password != ADMIN_PASSWORD:
                error_card("Invalid credentials", details="Incorrect admin password.")
                return
            st.session_state.auth_role = "admin"
            st.session_state.auth_email = email.strip()
            success_card("Admin access granted", f"Welcome {mask_email(email)}")
            st.rerun()
        elif email.strip().lower() == COMMON_USER_EMAIL.lower():
            if password != COMMON_USER_PASSWORD:
                error_card("Invalid credentials", details="Incorrect user password.")
                return
            st.session_state.auth_role = "user"
            st.session_state.auth_email = email.strip()
            success_card("Welcome back!", f"Signed in as {mask_email(email)}")
            st.rerun()
        else:
            error_card("Email not recognized", details="This email is not in the system.")

# ===========================
# EVALUATION PARSING HELPERS
# ===========================
def extract_structured_evaluation(evaluation_data: Any) -> Optional[Dict[str, Any]]:
    def parse_text_scores(text: str) -> Dict[str, float]:
        scores = {}
        patterns = [
            r'Product Knowledge[:\s]+(\d+(?:\.\d+)?)', r'Costs?\s*(?:&|and)?\s*Booking[:\s]+(\d+(?:\.\d+)?)',
            r'Tone\s*(?:of)?\s*Voice[:\s]+(\d+(?:\.\d+)?)', r'Objection\s*Handling[:\s]+(\d+(?:\.\d+)?)',
            r'Call\s*Control\/Flow[:\s]+(\d+(?:\.\d+)?)'
        ]
        score_keys = ['product_knowledge', 'costs_booking', 'tone_voice', 'objection_handling', 'call_control']
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try: scores[score_keys[i]] = float(match.group(1))
                except (ValueError, IndexError): pass
        json_match = re.search(r'\{[^}]*"product_knowledge"[^}]*\}', text, re.IGNORECASE | re.DOTALL)
        if json_match:
            try: scores.update(json.loads(json_match.group()))
            except json.JSONDecodeError: pass
        return scores
    def validate_scores(scores: Dict[str, float]) -> Dict[str, float]:
        validated = {}
        for key, value in scores.items():
            if isinstance(value, (int, float)):
                if value > 10: value = value / 10 if value <= 100 else 10
                validated[key] = max(0, min(10, float(value)))
        return validated
    text_to_parse = ""
    temp_eval_data = evaluation_data
    if isinstance(temp_eval_data, str):
        try: temp_eval_data = json.loads(temp_eval_data)
        except json.JSONDecodeError: text_to_parse = temp_eval_data
    if not text_to_parse and isinstance(temp_eval_data, dict):
        if 'detailed_feedback' in temp_eval_data and isinstance(temp_eval_data['detailed_feedback'], str):
            text_to_parse = temp_eval_data['detailed_feedback']
        elif 'Evaluation Score' in temp_eval_data and isinstance(temp_eval_data['Evaluation Score'], str):
            text_to_parse = temp_eval_data['Evaluation Score']
        elif 'evaluation' in temp_eval_data and isinstance(temp_eval_data['evaluation'], str):
            text_to_parse = temp_eval_data['evaluation']
    if not text_to_parse: text_to_parse = str(evaluation_data)
    parsed_scores = parse_text_scores(text_to_parse)
    if isinstance(temp_eval_data, dict):
        if 'evaluation_score' in temp_eval_data and isinstance(temp_eval_data['evaluation_score'], dict):
            parsed_scores.update(temp_eval_data['evaluation_score'])
        fields = ['product_knowledge', 'costs_booking', 'tone_voice', 'objection_handling', 'call_control']
        if any(f in temp_eval_data for f in fields):
            structured_scores = {f: temp_eval_data.get(f, 0) for f in fields}
            parsed_scores.update(structured_scores)
    if not parsed_scores and not re.search(r'\d/10', text_to_parse): return None
    
    # Let generate_detailed_feedback handle coaching tips extraction with its improved patterns
    return {
        'scores': validate_scores(parsed_scores), 'source': 'parsed_payload',
        'additional_data': {'detailed_feedback': text_to_parse, 'coaching_tips': []}  # Empty initially
    }
def generate_detailed_feedback(evaluation_data: str) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    parsed_feedback: Dict[str, Dict[str, Any]] = {}
    
    # Updated regex pattern to handle markdown formatting properly
    score_reasoning_pattern = re.compile(
        r"[-\*\s]*\*?\*?(Product Knowledge|Costs?[\s&]*Booking|Tone(?:\s*of)?\s*Voice|Objection Handling|Call Control[/\s]*Flow)\*?\*?\s*:\s*\*?\*?(\d+(?:\.\d+)?)\/10\*?\*?"
        r"([\s\S]*?)"
        r"(?=[-\*\s]*\*?\*?(?:Product Knowledge|Costs?[\s&]*Booking|Tone(?:\s*of)?\s*Voice|Objection Handling|Call Control[/\s]*Flow)\*?\*?\s*:|\*\*Critical Misses:\*\*|\*\*Conversion Potential:\*\*|\*\*Weighted Overall Score:\*\*|\Z)",
        re.IGNORECASE
    )
    
    score_matches = score_reasoning_pattern.findall(evaluation_data or "")
    
    score_mapping = {
        'product knowledge': 'product_knowledge', 
        'costs & booking': 'costs_booking', 
        'costs and booking': 'costs_booking',
        'costs booking': 'costs_booking', 
        'tone of voice': 'tone_voice', 
        'tone voice': 'tone_voice',
        'objection handling': 'objection_handling', 
        'call control/flow': 'call_control',
        'call control flow': 'call_control'
    }
    
    for title_raw, score_text, reasoning in score_matches:
        key_cleaned = re.sub(r'[\s&/]+', ' ', title_raw.strip().lower())
        key = score_mapping.get(key_cleaned, key_cleaned.replace(' ', '_'))
        
        try: 
            score_value = float(score_text)
        except: 
            score_value = 0.0
        
        # Clean up the reasoning text - remove arrow symbols and extra formatting
        reasoning_cleaned = reasoning.strip()
        reasoning_cleaned = re.sub(r'^\s*→\s*', '', reasoning_cleaned)  # Remove arrow at start
        reasoning_cleaned = re.sub(r'\n\s*', ' ', reasoning_cleaned)  # Replace newlines with spaces
        reasoning_cleaned = re.sub(r'\s+', ' ', reasoning_cleaned)  # Normalize whitespace
        
        # Look for bullet points or structured content
        bullets = re.findall(r'(?:•|-|\*|\d+\.)\s+(.*?)(?=(?:•|-|\*|\d+\.)|$)', reasoning_cleaned, re.MULTILINE)
        
        if bullets: 
            html = "<ul>" + "".join([f"<li>{re.sub(r'<[^>]*>', '', b).strip()}</li>" for b in bullets if b.strip()]) + "</ul>"
        else: 
            html = f"<p>{reasoning_cleaned}</p>"
        
        parsed_feedback[key] = {'score_text': f"{score_value}", 'reasoning': html}
    
    # Extract coaching tips
    coaching_tips = []
    coaching_patterns = [
        r'\*\*💡\s*Coaching Tips.*?:\*\*\s*\n(.*?)(?=\*\*.*?:\*\*|\Z)',  # Main pattern
        r'💡\s*COACHING TIPS.*?\n(.*?)(?=\*\*.*?:\*\*|\Z)',  # Alternative pattern
        r'\*\*COACHING TIPS.*?:\*\*\s*\n(.*?)(?=\*\*.*?:\*\*|\Z)'  # Without emoji
    ]
    
    for pattern in coaching_patterns:
        coaching_match = re.search(pattern, evaluation_data, re.IGNORECASE | re.DOTALL)
        if coaching_match:
            coaching_section = coaching_match.group(1).strip()
            # Extract numbered/bulleted items from coaching section
            tip_items = re.findall(r'^\s*(?:\d+\.|\*|-|•)\s*\*?\*?(.*?)(?=\n\s*(?:\d+\.|\*|-|•)|\Z)', 
                                 coaching_section, re.MULTILINE | re.DOTALL)
            
            for tip in tip_items:
                # Clean up the tip text
                tip_cleaned = re.sub(r'\n\s*', ' ', tip.strip())  # Replace newlines with spaces
                tip_cleaned = re.sub(r'\s+', ' ', tip_cleaned)  # Normalize whitespace
                tip_cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', tip_cleaned)  # Remove bold markdown
                tip_cleaned = tip_cleaned.strip()
                
                if tip_cleaned and len(tip_cleaned) > 10:  # Filter out very short tips
                    coaching_tips.append(tip_cleaned)
            
            if coaching_tips:
                break  # Found tips, no need to try other patterns
    
    overall_data = {'coaching_tips': coaching_tips}
    
    return parsed_feedback, overall_data
def calc_overall_score(scores: Dict[str, float]) -> float:
    weights = {'product_knowledge': 0.3, 'costs_booking': 0.25, 'tone_voice': 0.2, 'objection_handling': 0.15, 'call_control': 0.1}
    return sum(scores.get(k, 0) * w for k, w in weights.items())
def extract_real_call_score_and_tips(evaluation_data: Any) -> Tuple[Optional[float], List[str]]:
    se = extract_structured_evaluation(evaluation_data)
    tips: List[str] = []
    if se:
        add = se.get("additional_data", {})
        if isinstance(add, dict) and isinstance(add.get("coaching_tips"), list) and add["coaching_tips"]:
            tips.extend([t for t in add["coaching_tips"] if isinstance(t, str) and t.strip()])
        if not tips and isinstance(add, dict) and isinstance(add.get("detailed_feedback"), str):
            _, overall_tips_from_generate = generate_detailed_feedback(add["detailed_feedback"])
            if isinstance(overall_tips_from_generate.get("coaching_tips"), list):
                tips.extend([t for t in overall_tips_from_generate["coaching_tips"] if isinstance(t, str) and t.strip()])
        overall = calc_overall_score(se.get("scores", {})) if se.get("scores") else None
        seen = set(); tips_dedup = []
        for t in tips:
            tt = t.strip()
            if tt and tt not in seen: tips_dedup.append(tt); seen.add(tt)
        return overall, tips_dedup
    return None, []
@st.dialog("Detailed Evaluation")
def show_evaluation_dialog(score_label, score_value, reasoning, has_reasoning: bool):
    st.markdown(f"### {score_label}: {score_value:.1f}/10")
    st.markdown("---")
    if has_reasoning: st.markdown(reasoning, unsafe_allow_html=True)
    else: st.warning("No detailed reasoning was provided by the evaluator for this criterion.")
    if st.button("Close"): st.session_state.show_dialog = False; st.rerun()
def display_evaluation_scores_improved(evaluation_data: Any, trainee_name: str = ""):
    structured_eval = extract_structured_evaluation(evaluation_data)
    if structured_eval and structured_eval.get('scores'):
        scores = structured_eval['scores']
        additional_data = structured_eval.get('additional_data', {})
        per_category_feedback, _ = {}, {}
        if 'detailed_feedback' in additional_data: per_category_feedback, _ = generate_detailed_feedback(additional_data['detailed_feedback'])
        st.markdown("### Training Evaluation Scores")
        if trainee_name: st.markdown(f"""<div class="trainee-name-card"><h3 class="trainee-name-text">Trainee: {trainee_name}</h3><p style="margin: 0; opacity: 0.9;">Evaluation Results</p></div>""", unsafe_allow_html=True)
        st.success(f"Scores successfully extracted from: {structured_eval['source']}")
        required_scores = ['product_knowledge', 'costs_booking', 'tone_voice', 'objection_handling', 'call_control']
        missing_scores = [s for s in required_scores if s not in scores or scores.get(s) == 0]
        if missing_scores: st.warning(f"Missing or zero scores for: {', '.join(missing_scores)}")
        # Replace the score display and dialog sections in display_evaluation_scores_improved:

        score_configs = [
            ('product_knowledge', 'Product Knowledge', '30%'), ('costs_booking', 'Costs & Booking', '25%'),
            ('tone_voice', 'Tone of Voice', '20%'), ('objection_handling', 'Objection Handling', '15%'),
            ('call_control', 'Call Control/Flow', '10%')
        ]

        # Initialize dialog state
        if "show_dialog" not in st.session_state:
            st.session_state.show_dialog = False

        score_cols = st.columns(5, gap="medium")
        for idx, (score_key, label, weight) in enumerate(score_configs):
            score_value = scores.get(score_key, 0.0)
            with score_cols[idx]:
                st.markdown(f"""<div class="score-card"><h6>{label}</h6><h2 style="color: var(--purple1);">{score_value:.1f}/10</h2><p>Weight: {weight}</p></div>""", unsafe_allow_html=True)
                st.progress(score_value / 10)
                if score_key in per_category_feedback:
                    # Use a simpler, more reliable key
                    button_key = f"dialog_{score_key}_{idx}"
                    if st.button("Why this score?", key=button_key):
                        st.session_state.show_dialog = True
                        st.session_state.dialog_content = {
                            "label": label, 
                            "value": score_value, 
                            "reasoning": per_category_feedback[score_key]['reasoning']
                        }
                        # st.rerun()
        # Keep the existing show_evaluation_dialog function as is:
        @st.dialog("Detailed Evaluation")
        def show_evaluation_dialog(score_label, score_value, reasoning, has_reasoning: bool):
            st.markdown(f"### {score_label}: {score_value:.1f}/10")
            st.markdown("---")
            if has_reasoning: 
                st.markdown(reasoning, unsafe_allow_html=True)
            else: 
                st.warning("No detailed reasoning was provided by the evaluator for this criterion.")
            if st.button("Close"): 
                st.session_state.show_dialog = False
                st.rerun()

        # Show dialog if triggered
        if st.session_state.get("show_dialog", False):
            dialog_content = st.session_state.get("dialog_content", {})
            show_evaluation_dialog(
                dialog_content.get("label", ""), 
                dialog_content.get("value", 0.0), 
                dialog_content.get("reasoning", ""), 
                bool(dialog_content.get("reasoning"))
            )

        
        if "show_dialog" in st.session_state and st.session_state.show_dialog:
            show_evaluation_dialog(st.session_state.dialog_content["label"], st.session_state.dialog_content["value"], st.session_state.dialog_content["reasoning"], True if st.session_state.dialog_content.get("reasoning") else False)
        overall_score = calc_overall_score(scores)
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Overall Training Score")
            if overall_score >= 8: grade, color = "Excellent", "#28a745"
            elif overall_score >= 6: grade, color = "Good", "#ffc107"
            else: grade, color = "Needs Work", "#dc3545"
            st.markdown(f"""<div style="text-align: center; padding: 2rem; border-radius: 10px; background: linear-gradient(135deg, {color} 0%, {color}aa 100%); margin: 1rem 0;"><h1 style="color: white; font-size: 4rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{overall_score:.1f}/10</h1><h3 style="color: white; margin: 0;">{grade}</h3></div>""", unsafe_allow_html=True)
        st.markdown("### Detailed Score Breakdown")
        breakdown_data = []
        for (key, label, weight_str), weight in zip(score_configs, [0.3, 0.25, 0.2, 0.15, 0.1]):
            score_value = scores.get(key, 0)
            weighted_contribution = score_value * weight
            breakdown_data.append({'Criteria': label, 'Raw Score': f"{score_value:.1f}/10", 'Weight': weight_str, 'Weighted Score': f"{weighted_contribution:.2f}", 'Performance': "Good" if score_value >= 7 else "Average" if score_value >= 5 else "Needs Work"})
        st.table(breakdown_data)
        st.markdown("### Full Detailed Evaluation")
        with st.expander("View Complete Evaluation", expanded=True):
            raw_text_content = additional_data.get('detailed_feedback', '')
            if raw_text_content: st.markdown(raw_text_content, unsafe_allow_html=True)
            else: st.warning("No detailed text feedback found in the evaluation payload.")
        return True
    else:
        st.markdown("### Evaluation Scores Not Found")
        st.error("Unable to extract structured evaluation scores from the provided data.")
        st.info("This can happen if the post-call analysis is still running or was not configured correctly for the agent.")
        st.code(str(evaluation_data), language="text")
        return False
def _coerce_start_dt(call) -> Optional[datetime]:
    ts = None
    if hasattr(call, "start_timestamp") and call.start_timestamp:
        ts = int(call.start_timestamp)
        if ts > 1_000_000_000_000: ts //= 1_000
        elif ts > 10_000_000_000:  ts //= 1_000
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if hasattr(call, "start_time") and call.start_time:
        ts = int(call.start_time)
        if ts > 1_000_000_000_000: ts //= 1_000
        elif ts > 10_000_000_000:  ts //= 1_000
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if hasattr(call, "created_at") and call.created_at:
        v = call.created_at
        try:
            if isinstance(v, (int, float)):
                ts = int(v)
                if ts > 1_000_000_000_000: ts //= 1_000
                elif ts > 10_000_000_000:  ts //= 1_000
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            elif isinstance(v, str):
                if v.isdigit():
                    ts = int(v)
                    if ts > 1_000_000_000_000: ts //= 1_000
                    elif ts > 10_000_000_000:  ts //= 1_000
                    return datetime.fromtimestamp(ts, tz=timezone.utc)
                else:
                    return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception: pass
    return None
@st.cache_data(ttl=300)
def list_all_calls(_client, start_date: datetime, end_date: datetime):
    out = []
    page_size = 50
    cursor = None
    tries = 0
    start_bound = start_date.replace(tzinfo=timezone.utc)
    end_bound = end_date.replace(tzinfo=timezone.utc)
    while tries < 5:
        tries += 1
        try:
            kwargs = {"limit": page_size}
            if cursor: kwargs["cursor"] = cursor
            resp = _client.call.list(**kwargs)
            calls = getattr(resp, "data", None)
            if calls is None: calls = resp or []
            if not calls: break
            for call in calls:
                dt = _coerce_start_dt(call)
                if dt and start_bound <= dt <= end_bound: out.append(call)
            has_more = bool(getattr(resp, "has_more", False))
            next_cur = getattr(resp, "next_cursor", None) or getattr(resp, "cursor", None)
            if not has_more or not next_cur: break
            cursor = next_cur
            if len(out) >= 100: break
        except Exception as e:
            st.warning(f"API call failed on attempt {tries}: {str(e)}")
            break
    out.sort(key=lambda c: _coerce_start_dt(c) or datetime.fromtimestamp(0, tz=timezone.utc), reverse=True)
    return out[:100]

# =========================
# USER VIEW
# =========================
def render_user_view(client: Retell):
    st.markdown("""<div class="title-container"><h1 class="title-text">Aspect AI Training Agent</h1><p class="subtitle-text">Advanced Role-Play Simulation for Booking Agents</p></div>""", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("## Training Configuration")
        level_options = {
            "1": {"name": "Level 1: Foundation", "description": "Cooperative customers with basic booking needs", "details": "Basic plumbing, electrical, heating issues. Customers are cooperative but cautious."},
            "2": {"name": "Level 2: Objection Handling", "description": "Pushy customers with competitive comparisons", "details": "Customers compare prices, challenge guarantees, resist giving information."},
            "3": {"name": "Level 3: Advanced", "description": "Complex scenarios with multiple trade requirements", "details": "Confused customers, multiple trades needed, commercial scenarios."}
        }
        selected_level = st.selectbox("Choose Training Level:", options=list(level_options.keys()), format_func=lambda x: f"{level_options[x]['name']}")
        level_info = level_options[selected_level]
        st.markdown(f"""<div class="level-card"><h4>{level_info['name']}</h4><p><strong>Focus:</strong> {level_info['description']}</p><p><small>{level_info['details']}</small></p></div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Training Parameters")
        trainee_name = st.text_input("👤 Trainee Name", placeholder="Enter your name (e.g., Jane Doe)", help="Used in your Retell metadata and to fetch your evaluations")
        session_duration = st.selectbox("Session Duration", options=[5, 10, 15, 20, 30], index=2, format_func=lambda x: f"{x} minutes")
        scenario_count = st.selectbox("Number of Scenarios", options=[3, 5, 7, 10], index=1, help="Number of customer scenarios to practice")
        difficulty_focus = st.multiselect("Focus Areas", options=["Plumbing & Cold Water","Heating & Hot Water","Electrical work","Drainage","Leak Detection","Roofing", "HVAC","Multi-Trade","Decoration","Fire Safety","Insurance","Commercial"], default=["Plumbing & Cold Water", "Electrical work", "Heating & Hot Water"])
        st.markdown("### Call Settings")
        enable_recording = st.checkbox("Enable Call Recording", value=True)
        enable_transcript = st.checkbox("Generate Live Transcript", value=True)
        enable_analysis = st.checkbox("Post-Call Analysis", value=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("## Voice Training Session")
        if trainee_name:
            st.markdown(f"""<div class="trainee-name-card"><h3 class="trainee-name-text">Current Trainee: {trainee_name}</h3><p style="margin: 0; opacity: 0.9;">Ready to begin your training session</p></div>""", unsafe_allow_html=True)
        phone_number = st.text_input("Enter your phone number:", placeholder="+447123456789", help="Include country code (e.g., +44 for UK)")
        def is_valid_phone(phone): return phone.startswith('+') and len(phone.replace('+', '').replace('-', '').replace(' ', '')) >= 10
        if phone_number and not is_valid_phone(phone_number):
            st.warning("Please enter a valid phone number with country code")
        session_metadata = {
            "training_level": selected_level, "level_name": level_info['name'],
            "trainee_name": trainee_name or "Anonymous", "session_duration_minutes": session_duration,
            "scenario_count": scenario_count, "focus_areas": ", ".join(difficulty_focus) if difficulty_focus else "General",
            "session_id": f"session_{int(time.time())}", "timestamp": datetime.now().isoformat(),
            "settings": {"recording_enabled": enable_recording, "transcript_enabled": enable_transcript, "analysis_enabled": enable_analysis}
        }
        llm_dynamic_variables = {
            "training_level": str(selected_level), "level_description": str(level_info['description']),
            "scenario_count": str(scenario_count), "focus_areas": ", ".join(difficulty_focus) if difficulty_focus else "General",
            "trainee_name": str(trainee_name or "trainee"), "session_type": "booking_practice"
        }
        
        if st.button("Start Training Session", disabled=not phone_number or not is_valid_phone(phone_number) or not trainee_name):
            try:
                with st.spinner("Initiating training session..."):
                    

                    response = client.call.create_phone_call(
                        from_number=FROM_NUMBER,
                        to_number=phone_number,
                        override_agent_id=RETELL_AGENT_ID,
                        retell_llm_dynamic_variables=llm_dynamic_variables,
                        metadata=session_metadata
                    )
                st.session_state.current_call_id = response.call_id
                st.session_state.session_metadata = session_metadata
                st.session_state.training_active = True
                st.success("🎯 Training session initiated!")
                st.info(f"📞 Expect a call shortly. **Level {selected_level}** with {scenario_count} scenarios.")
                with st.expander("Session Summary", expanded=True):
                    st.write(f"**Call ID:** {response.call_id}")
                    st.write(f"**Trainee:** {trainee_name or 'Anonymous'}")
                    st.write(f"**Training Level:** {level_info['name']}")
                    st.write(f"**Scenarios:** {scenario_count}")
                    st.write(f"**Focus Areas:** {', '.join(difficulty_focus) if difficulty_focus else 'General'}")
                    st.write(f"**Duration:** {session_duration} minutes")
            except Exception as e:
                st.error(f"❌ Error starting training session: {e}")
                st.info("Check your phone format and that you have assigned a default agent to your number in the Retell Dashboard.")
    if hasattr(st.session_state, 'training_active') and st.session_state.training_active:
        if hasattr(st.session_state, 'current_call_id'):
            st.markdown("---")
            st.markdown("## Live Training Session")
            try:
                call_details = client.call.retrieve(st.session_state.current_call_id)
                colA, colB, colC = st.columns(3)
                with colA: st.metric("Call Status", call_details.call_status.title())
                with colB:
                    if hasattr(call_details, 'duration_ms') and call_details.duration_ms:
                        duration_sec = call_details.duration_ms / 1000
                        st.metric("Duration", f"{int(duration_sec//60)}:{int(duration_sec%60):02d}")
                    else: st.metric("Duration", "Active")
                with colC:
                    if st.button("End Session"):
                        try:
                            client.call.cancel(call_id=st.session_state.current_call_id)
                            st.session_state.training_active = False
                            st.success("Training session ended!")
                            st.rerun()
                        except Exception as e: st.error(f"Error ending call: {e}")
                if enable_transcript and hasattr(call_details, 'transcript_object') and call_details.transcript_object:
                    st.markdown("### Live Transcript")
                    transcript_html = '<div class="transcript-box">'
                    for entry in call_details.transcript_object[-15:]:
                        role = "Customer" if entry.role == "user" else "Trainee"
                        content = entry.content if hasattr(entry, 'content') else str(entry)
                        if role == "Customer": transcript_html += f'<p><span class="customer-msg">{role}:</span> {content}</p>'
                        else: transcript_html += f'<p><span class="trainee-msg">{role}:</span> {content}</p>'
                    transcript_html += '</div>'
                    st.markdown(transcript_html, unsafe_allow_html=True)
            except Exception as e: st.warning(f"Unable to fetch live call data: {e}")
    if hasattr(st.session_state, 'current_call_id') and st.session_state.current_call_id:
        if st.session_state.get('training_active', False):
            try:
                call_status_check = client.call.retrieve(st.session_state.current_call_id)
                if call_status_check.call_status == "ended":
                    st.session_state.training_active = False
                    display_call_analysis_for_user(client, st.session_state.current_call_id)
            except Exception as e: st.warning(f"Unable to check call status: {e}")
    st.markdown("---")
    st.markdown("## Latest Evaluation")
    st.caption("Shows your most recent ended session's full evaluation.")
    lookback_days = st.number_input("Look back (days)", min_value=1, max_value=180, value=30, step=1, key="latest_eval_days")
    if st.button("Show My Latest Evaluation"):
        if not trainee_name:
            st.warning("Enter your Trainee Name in the sidebar first.")
        else:
            with st.spinner("Finding your most recent ended session..."):
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=int(lookback_days))
                calls = list_all_calls(client, start_dt, end_dt)
                calls = [c for c in calls if getattr(c, "call_status", "") == "ended" and (getattr(c, "metadata", {}) or {}).get("trainee_name", "").strip().lower() == trainee_name.strip().lower()]
                if not calls: st.info("No ended sessions found for that trainee name in the selected window.")
                else:
                    latest = calls[0]
                    evaluation_data = None
                    with st.spinner("Fetching evaluation details..."):
                        full = client.call.retrieve(latest.call_id)
                        if hasattr(full, 'call_analysis') and full.call_analysis and getattr(full.call_analysis, 'custom_analysis_data', None): evaluation_data = full.call_analysis.custom_analysis_data
                        if evaluation_data is None and hasattr(full, 'metadata') and full.metadata: evaluation_data = full.metadata.get("evaluation") or (full.metadata if "evaluation_score" in full.metadata else None)
                        if evaluation_data is None and hasattr(full, 'transcript'): evaluation_data = full.transcript
                    if evaluation_data: display_evaluation_scores_improved(evaluation_data, trainee_name)
                    else: st.warning("No structured evaluation data available for your latest session.")
    st.markdown("---")
    st.markdown("## Your Performance & Attempts")
    st.caption("Summary by your trainee name. Shows attempts count, average score, and past sessions.")
    perf_days = st.number_input("Look back (days)", min_value=1, max_value=180, value=30, step=1, key="user_perf_days")
    max_rows = st.number_input("Max sessions to show", min_value=1, max_value=50, value=10, step=1, key="user_perf_max")
    if st.button("Load My Performance"):
        if not trainee_name:
            st.warning("Enter your Trainee Name in the sidebar first.")
        else:
            with st.spinner("Loading your attempts and past evaluations..."):
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=int(perf_days))
                calls = list_all_calls(client, start_dt, end_dt)
                calls = [c for c in calls if (getattr(c, "metadata", {}) or {}).get("trainee_name", "").strip().lower() == trainee_name.strip().lower()]
                attempts = len(calls)
                ended = [c for c in calls if getattr(c, "call_status", "") == "ended"]
                per_call_score = {}
                rows = []
                for c in ended[:int(max_rows)]:
                    ev = None
                    call_analysis = getattr(c, 'call_analysis', None)
                    if call_analysis: ev = getattr(call_analysis, 'custom_analysis_data', None)
                    if ev is None:
                        metadata = getattr(c, 'metadata', None)
                        if isinstance(metadata, dict): ev = metadata.get("evaluation") or (metadata if "evaluation_score" in metadata else None)
                    if ev is None: ev = getattr(c, 'transcript', None)
                    se = extract_structured_evaluation(ev) if ev else None
                    overall = calc_overall_score(se["scores"]) if se and se.get("scores") else None
                    per_call_score[c.call_id] = overall
                    dt = _coerce_start_dt(c)
                    dt_str = dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M') if dt else "N/A"
                    level = (getattr(c, "metadata", {}) or {}).get("training_level", "—")
                    rows.append({"Date (UTC)": dt_str, "Call ID": c.call_id[:10], "Level": level, "Overall": f"{overall:.1f}" if isinstance(overall, (int, float)) else "—", "Action": f"view_{c.call_id}"})
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Attempts (range)", attempts)
                with c2:
                    valid_scores = [v for v in per_call_score.values() if isinstance(v, (int, float))]
                    st.metric("Avg Score", f"{(sum(valid_scores)/len(valid_scores)):.2f}" if valid_scores else "—")
                with c3: st.metric("Ended Sessions", len(ended))
                if rows:
                    st.markdown("### Past Sessions")
                    for r in rows:
                        colA, colB, colC, colD, colE = st.columns([2,2,1,1,1])
                        with colA: st.write(r["Date (UTC)"])
                        with colB: st.write(f"Call {r['Call ID']}...")
                        with colC: st.write(f"Level {r['Level']}")
                        with colD: st.write(f"Score: {r['Overall']}")
                        with colE:
                            if st.button("View Evaluation", key=r["Action"]):
                                st.session_state.current_call_id = r["Action"].replace("view_", "")
                                st.session_state.training_active = False
                                st.rerun()
                else: st.info("No ended sessions in the selected range for this trainee name.")
    st.markdown("---")
    st.markdown("## Coaching Tips")
    st.caption("Pulled from your real evaluation output.")
    tips_days = st.number_input("Look back (days)", min_value=1, max_value=90, value=14, step=1)
    tips_limit = st.number_input("Max sessions to include", min_value=1, max_value=20, value=5, step=1)
    if st.button("Load Coaching Tips"):
        if not trainee_name: st.warning("Enter your Trainee Name in the sidebar first.")
        else:
            with st.spinner("Gathering your recent coaching tips..."):
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=int(tips_days))
                calls = list_all_calls(client, start_dt, end_dt)
                calls = [c for c in calls if getattr(c, "call_status", "") == "ended" and (getattr(c, "metadata", {}) or {}).get("trainee_name", "").strip().lower() == trainee_name.strip().lower()]
                calls = calls[:int(tips_limit)]
                found_any = False
                if not calls: st.info("No recent ended sessions found for that trainee.")
                else:
                    for c in calls:
                        ev = None; full = None
                        try: full = client.call.retrieve(c.call_id)
                        except Exception: pass
                        if full:
                            if hasattr(full, 'call_analysis') and full.call_analysis and getattr(full.call_analysis, 'custom_analysis_data', None): ev = full.call_analysis.custom_analysis_data
                            if ev is None and hasattr(full, 'metadata') and full.metadata: ev = full.metadata.get("evaluation") or (full.metadata if "coaching_tips" in full.metadata or "evaluation_score" in full.metadata else None)
                            if ev is None and hasattr(full, 'transcript'): ev = full.transcript
                        overall, tips = extract_real_call_score_and_tips(ev) if ev is not None else (None, [])
                        dt = _coerce_start_dt(c)
                        dt_str = dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M') if dt else "N/A"
                        st.markdown(f"**Session #{c.call_id[:8]} • {dt_str} UTC**")
                        if overall is not None: st.caption(f"Overall Score: **{overall:.1f}/10**")
                        if tips:
                            found_any = True
                            for i, tip in enumerate(tips, 1): st.info(f"**{i}.** {tip}")
                        else: st.warning("No coaching tips found in the evaluation payload for this session.")
                    if not found_any:
                        with st.expander("Why no tips? Click for setup checklist.", expanded=False):
                            st.markdown("""**To receive real coaching tips, ensure your evaluation payload includes them:**\n- Include a `COACHING TIPS:` section in your agent's evaluation output.\n- The parser looks for that heading and extracts bullet points or numbered lists that follow.""")
    st.markdown("""<div style='text-align: center; color: #6c757d; padding: 1.2rem;'><p>Powered by Aspect AI Training System | Built with Streamlit & Retell AI</p><p><strong>Version 4.0 — Final Working Version</strong></p></div>""", unsafe_allow_html=True)

def display_call_analysis_for_user(client, call_id):
    try:
        with st.spinner("Fetching latest evaluation data..."):
            call_details = client.call.retrieve(call_id)
        if call_details.call_status != "ended": return
        st.markdown("---")
        st.markdown("## Your Training Session Results")
        trainee_name = ""
        if hasattr(st.session_state, 'session_metadata') and 'trainee_name' in st.session_state.session_metadata:
            trainee_name = st.session_state.session_metadata['trainee_name']
        elif hasattr(call_details, 'metadata') and call_details.metadata and 'trainee_name' in call_details.metadata:
            trainee_name = call_details.metadata['trainee_name']
        evaluation_data = None
        if hasattr(call_details, 'call_analysis') and call_details.call_analysis and hasattr(call_details.call_analysis, 'custom_analysis_data') and call_details.call_analysis.custom_analysis_data:
            evaluation_data = call_details.call_analysis.custom_analysis_data
        if not evaluation_data and hasattr(call_details, 'metadata') and call_details.metadata:
            evaluation_data = call_details.metadata.get("evaluation") or (call_details.metadata if "evaluation_score" in call_details.metadata else None)
        if not evaluation_data and hasattr(call_details, 'transcript'):
            evaluation_data = call_details.transcript
        if evaluation_data: display_evaluation_scores_improved(evaluation_data, trainee_name)
        else: st.info("No structured evaluation data found for this session yet.")
    except Exception as e: st.warning(f"Unable to load results: {e}")

def render_admin_view(client: Retell):
    st.markdown("""<div class="title-container"><h1 class="title-text">Aspect AI — Admin Console</h1><p class="subtitle-text">Per-Trainee Dashboards, Evaluation & Performance</p></div>""", unsafe_allow_html=True)
    top = st.columns([7,1])
    st.markdown("### Filters")
    colf1, colf2, colf3 = st.columns([1,1,1])
    with colf1:
        today = datetime.now().date()
        start_date = st.date_input("Start Date", value=today - timedelta(days=14), key="admin_start")
    with colf2: end_date = st.date_input("End Date", value=today, key="admin_end")
    with colf3: show_recent_n = st.number_input("Show Top N Recent", min_value=1, max_value=100, value=10, step=1, key="admin_recent_n")
    if st.button("Load History", type="primary"): st.session_state.admin_history_loaded = True
    if not st.session_state.get("admin_history_loaded", False): st.stop()
    with st.spinner(f"Loading calls from {start_date} to {end_date}..."):
        calls = list_all_calls(client, datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time()))
    if not calls:
        st.info("No calls found for the selected range.")
        return
    ended = [c for c in calls if getattr(c, "call_status", "") == "ended"]
    per_call_score: Dict[str, Optional[float]] = {}
    progress_container = st.container()
    total_calls_to_score = len(ended)
    if total_calls_to_score > 0:
        with progress_container:
            st.markdown('<div class="red-progress">', unsafe_allow_html=True)
            progress_text = "Pre-computing scores for a faster dashboard..."
            progress_bar = st.progress(0, text=progress_text)
            st.markdown('</div>', unsafe_allow_html=True)
        for i, c in enumerate(ended):
            ev = None; full = None
            try:
                if hasattr(c, 'call_analysis') and c.call_analysis and getattr(c.call_analysis, 'custom_analysis_data', None): ev = c.call_analysis.custom_analysis_data
                else: full = client.call.retrieve(c.call_id)
            except Exception: pass
            if ev is None and full and hasattr(full, 'call_analysis') and full.call_analysis and getattr(full.call_analysis, 'custom_analysis_data', None): ev = full.call_analysis.custom_analysis_data
            if ev is None:
                source_obj = full if full else c
                if hasattr(source_obj, 'metadata') and source_obj.metadata: ev = source_obj.metadata.get("evaluation") or (source_obj.metadata if "evaluation_score" in source_obj.metadata else None)
            if ev is None:
                source_obj = full if full else c
                if hasattr(source_obj, 'transcript'): ev = source_obj.transcript
            se = extract_structured_evaluation(ev) if ev is not None else None
            overall = calc_overall_score(se["scores"]) if se and se.get("scores") else None
            per_call_score[c.call_id] = overall
            progress_bar.progress((i + 1) / total_calls_to_score, text=f"{progress_text} ({i + 1}/{total_calls_to_score})")
        time.sleep(0.5)
        progress_container.empty()
    trainees = defaultdict(list)
    for c in calls:
        tname = (getattr(c, "metadata", {}) or {}).get("trainee_name", "Unknown").strip()
        if not tname: tname = "Unknown"
        trainees[tname].append(c)
    st.markdown("---")
    st.markdown("## Per-Trainee Dashboards (Name-wise)")
    st.caption("Each trainee's attempts, average score, and full evaluations. Click to open a session's full details.")
    sorted_trainees = sorted(trainees.keys(), key=lambda s: (s == "Unknown", s.lower()))
    for tname in sorted_trainees:
        clist = trainees[tname]
        ended_for_t = [c for c in clist if getattr(c, "call_status", "") == "ended"]
        vals = []
        for c in ended_for_t:
            v = per_call_score.get(c.call_id)
            if isinstance(v, (int, float)): vals.append(v)
        avg_t = sum(vals) / len(vals) if vals else None
        attempts = len(clist)
        st.markdown(f"### 👤 {tname}")
        sub1, sub2, sub3 = st.columns(3)
        with sub1: st.metric("Attempts", attempts)
        with sub2: st.metric("Ended", len(ended_for_t))
        with sub3: st.metric("Avg Score", f"{avg_t:.2f}" if avg_t is not None else "—")
        if not clist:
            st.info("No sessions for this trainee in the selected window.")
            continue
        st.markdown("#### Sessions")
        sorted_sessions = sorted(clist, key=lambda x: (_coerce_start_dt(x) or datetime.fromtimestamp(0, tz=timezone.utc)), reverse=True)
        for c in sorted_sessions[:int(show_recent_n)]:
            dt = _coerce_start_dt(c)
            dt_str = dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M') if dt else "N/A"
            level = (getattr(c, "metadata", {}) or {}).get("training_level", "—")
            overall = per_call_score.get(c.call_id)
            colA, colB, colC, colD, colE = st.columns([2,2,1,1,1])
            with colA: st.write(dt_str)
            with colB: st.write(f"Call {c.call_id[:10]}...")
            with colC: st.write(f"Level {level}")
            with colD: st.write(f"Score: {f'{overall:.1f}' if isinstance(overall, (int, float)) else '—'}")
            with colE:
                if st.button("Open Full Evaluation", key=f"open_eval_{c.call_id}"):
                    st.session_state.current_call_id = c.call_id
                    st.session_state.training_active = False
                    st.rerun()
    if st.session_state.get("current_call_id"):
        st.markdown("---")
        st.markdown("## Full Evaluation View (Admin)")
        display_call_analysis_admin(client, st.session_state.current_call_id)

def _maybe_get_recording_url(call_details):
    """Best-effort fetch of a recording URL from common fields or metadata."""
    # Direct known attributes first
    for attr in ["recording_url", "audio_url", "url"]:
        if hasattr(call_details, attr) and getattr(call_details, attr):
            return getattr(call_details, attr)

    # Nested objects Retell might use
    if hasattr(call_details, "recording") and getattr(call_details, "recording"):
        rec = getattr(call_details, "recording")
        for attr in ["url", "recording_url", "audio_url"]:
            if hasattr(rec, attr) and getattr(rec, attr):
                return getattr(rec, attr)

    # Metadata fallback
    if hasattr(call_details, "metadata") and isinstance(call_details.metadata, dict):
        for k in ["recording_url", "audio_url", "recordingUri", "recording"]:
            v = call_details.metadata.get(k)
            if isinstance(v, str) and v.startswith(("http://", "https://")):
                return v
            if isinstance(v, dict):
                for kk in ["url", "recording_url", "audio_url"]:
                    if isinstance(v.get(kk), str) and v[kk].startswith(("http://", "https://")):
                        return v[kk]
    return None

def display_call_analysis_admin(client, call_id):
    try:
        with st.spinner("Fetching evaluation details..."):
            call_details = client.call.retrieve(call_id)
            if call_details.call_status != "ended":
                st.info("Call analysis will be available once the call is completed.")
                return
            trainee_name = ""
            if hasattr(call_details, 'metadata') and call_details.metadata and 'trainee_name' in call_details.metadata:
                trainee_name = call_details.metadata['trainee_name']
            evaluation_data = None
            if hasattr(call_details, 'call_analysis') and call_details.call_analysis and hasattr(call_details.call_analysis, 'custom_analysis_data') and call_details.call_analysis.custom_analysis_data:
                evaluation_data = call_details.call_analysis.custom_analysis_data
            if not evaluation_data and hasattr(call_details, 'metadata') and call_details.metadata:
                evaluation_data = call_details.metadata.get("evaluation") or (call_details.metadata if "evaluation_score" in call_details.metadata else None)
            if not evaluation_data and hasattr(call_details, 'transcript'):
                evaluation_data = call_details.transcript
        if evaluation_data:
            display_evaluation_scores_improved(evaluation_data, trainee_name)
        else:
            st.info("No structured evaluation data found for this session.")
        st.markdown("### Session Artifacts")
        colA, colB = st.columns(2)
        with colA:
            with st.expander("Full Transcript", expanded=False):
                if hasattr(call_details, 'transcript_object') and call_details.transcript_object:
                    html = '<div class="transcript-box">'
                    for entry in call_details.transcript_object:
                        role = "Customer" if getattr(entry, "role", "") == "user" else "Trainee"
                        content = getattr(entry, "content", "") or str(entry)
                        cls = "customer-msg" if role == "Customer" else "trainee-msg"
                        html += f'<p><span class="{cls}">{role}:</span> {content}</p>'
                    html += "</div>"
                    st.markdown(html, unsafe_allow_html=True)
                elif hasattr(call_details, 'transcript') and call_details.transcript:
                    st.text_area("Transcript (Raw)", call_details.transcript, height=300, label_visibility="collapsed")
                else:
                    st.info("No transcript available for this call.")
        with colB:
            recording_url = _maybe_get_recording_url(call_details)
            if recording_url:
                st.markdown(f"**Recording:** [Open audio]({recording_url})")
                st.audio(recording_url)
            else:
                st.info("No recording URL found in this call object or metadata.")
    except Exception as e:
        st.warning(f"Unable to load evaluation: {e}")

def main():
    if not st.session_state.auth_role:
        render_login_screen()
        st.markdown(
            f"""
            <div class="footer">
                <div><strong>{COMPANY_NAME}</strong></div>
                <div>© {datetime.now().year} {COMPANY_NAME}. All rights reserved.</div>
                <div style="margin-top:6px;">Support: <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a> · {SUPPORT_PHONE}</div>
                <div style="margin-top:6px;">For production, integrate a secure identity provider (SSO/OIDC) and HTTPS.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    client = init_retell()
    topbar = st.columns([7,1])
    with topbar[1]:
        if st.button("Sign out", key="main_signout"):
            st.session_state.clear()
            st.rerun()
    if st.session_state.auth_role == "admin":
        render_admin_view(client)
    else:
        render_user_view(client)
    st.markdown(
        f"""
        <div class="footer">
            <div><strong>{COMPANY_NAME}</strong></div>
            <div>© {datetime.now().year} {COMPANY_NAME}. All rights reserved.</div>
            <div style="margin-top:6px;">Support: <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a> · {SUPPORT_PHONE}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()