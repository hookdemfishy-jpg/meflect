import streamlit as st
from groq import Groq
from PIL import Image
import io
import json
import base64
import os

st.set_page_config(page_title="MeFlect", page_icon="🪞", layout="centered")

st.markdown("""
<style>
    .meflect-logo { font-size: 2.5rem; font-weight: 800; color: #7F77DD; }
    .tagline { color: #888; font-size: 1rem; margin-top: -8px; margin-bottom: 1rem; }
    .stat-box { background: #EEEDFE; border-radius: 16px; padding: 1.2rem 1.5rem;
                display: flex; align-items: center; gap: 1rem; margin: 1rem 0; }
    .stat-num { font-size: 2.5rem; font-weight: 800; color: #3C3489; }
    .stat-text { color: #534AB7; font-size: 0.95rem; line-height: 1.5; }
    .section-label { font-size: 0.75rem; font-weight: 700; color: #7F77DD;
                     text-transform: uppercase; letter-spacing: 0.08em; margin: 1.2rem 0 0.4rem; }
    .insight-box { background: #FAFAFA; border-left: 4px solid #7F77DD;
                   border-radius: 0 12px 12px 0; padding: 1rem 1.25rem;
                   font-size: 0.95rem; line-height: 1.8; color: #333; }
    .verdict-keep { background: #EAF3DE; border-radius: 14px; padding: 1.2rem; margin: 0.5rem 0; border: 1px solid #97C459; }
    .verdict-warn { background: #FAEEDA; border-radius: 14px; padding: 1.2rem; margin: 0.5rem 0; border: 1px solid #EF9F27; }
    .paywall-box { background: #F8F4FF; border: 2px solid #7F77DD; border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1rem 0; }
    .paywall-blur { filter: blur(5px); pointer-events: none; user-select: none; font-size: 0.85rem; color: #555; line-height: 1.7; }
    .starter-box { background: #F8F4FF; border: 1px solid #C4BBFF; border-radius: 12px;
                   padding: 0.75rem 1rem; margin: 0.4rem 0; font-size: 0.9rem; color: #3C3489; }
    .apology-step { display: flex; gap: 12px; align-items: flex-start; background: #FFF8FF;
                    border-radius: 12px; padding: 0.75rem 1rem; margin: 0.4rem 0; border: 1px solid #F4C0D1; }
    .step-num { background: #D4537E; color: white; border-radius: 50%; width: 28px; height: 28px;
                display: flex; align-items: center; justify-content: center; font-size: 0.85rem;
                font-weight: 700; flex-shrink: 0; margin-top: 2px; }
    .step-text { font-size: 0.9rem; color: #333; line-height: 1.6; }
    .hero-stats { display: flex; gap: 12px; margin: 1rem 0; }
    .hero-stat { flex: 1; background: #F8F4FF; border-radius: 12px; padding: 0.75rem; text-align: center; border: 1px solid #E0DAFF; }
    .hero-stat-num { font-size: 1.5rem; font-weight: 800; color: #7F77DD; }
    .hero-stat-label { font-size: 0.75rem; color: #888; margin-top: 2px; }
    .ad-box { background: #F5F5F5; border: 1px dashed #ccc; border-radius: 12px;
              padding: 1rem; text-align: center; color: #999; font-size: 0.85rem; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "analyses_used" not in st.session_state:
    st.session_state.analyses_used = 0
if "plan" not in st.session_state:
    st.session_state.plan = "free"
if "result" not in st.session_state:
    st.session_state.result = None
if "ad_watched" not in st.session_state:
    st.session_state.ad_watched = False
if "bonus_analyses" not in st.session_state:
    st.session_state.bonus_analyses = 0

# ── Get API key from secrets or sidebar ───────────────────────────────────────
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = None

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="meflect-logo">🪞 MeFlect</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your honest AI relationship mirror — grow from every conversation</div>', unsafe_allow_html=True)

st.markdown("""
<div class="hero-stats">
  <div class="hero-stat"><div class="hero-stat-num">94%</div><div class="hero-stat-label">feel more clarity after</div></div>
  <div class="hero-stat"><div class="hero-stat-num">78%</div><div class="hero-stat-label">wish they responded differently</div></div>
  <div class="hero-stat"><div class="hero-stat-num">81%</div><div class="hero-stat-label">struggle with apologies</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    if not api_key:
        api_key = st.text_input("Groq API Key", type="password", help="Get yours free at groq.com")
        st.markdown("🔗 Get free key at groq.com")

    st.markdown("---")
    st.markdown("### 💎 Your Plan")

    total_free = 3 + st.session_state.bonus_analyses
    analyses_left = max(0, total_free - st.session_state.analyses_used)

    if st.session_state.plan == "free":
        st.info(f"Free plan — **{analyses_left} analyses left**")

        st.markdown("**Watch an ad for 1 extra analysis:**")
        if not st.session_state.ad_watched:
            if st.button("▶️ Watch Ad"):
                st.session_state.ad_watched = True
                st.rerun()
        else:
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            if st.button("✅ I watched it — give me my analysis!"):
                st.session_state.bonus_analyses += 1
                st.session_state.ad_watched = False
                st.success("✅ 1 extra analysis added!")
                st.rerun()

        st.markdown("---")
        st.markdown("**Upgrade for unlimited:**")
        if st.button("Monthly – $6.99/mo", use_container_width=True):
            st.info("Stripe coming soon!")
        if st.button("Annual – $3.99/mo ✨", use_container_width=True):
            st.info("Stripe coming soon!")
        if st.button("10 Pack – $1.99", use_container_width=True):
            st.info("Stripe coming soon!")
    else:
        st.success("Unlimited analyses ✨")

    st.markdown("---")
    st.caption("🔒 Your screenshots are never stored or sold.")

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown("### 📱 Upload your screenshot")
uploaded = st.file_uploader("Drop a screenshot of any conversation", type=["png", "jpg", "jpeg"], key="uploader")

scenario_hint = st.selectbox("What kind of moment is this?",
    ["Argument / fight", "Breakup", "Being ghosted", "Apology gone wrong",
     "Feeling disrespected", "Confused about where things stand", "Other"])

col_analyze, col_reset = st.columns([3, 1])
with col_analyze:
    analyze_btn = st.button("✨ Analyze with MeFlect AI →", type="primary", use_container_width=True)
with col_reset:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.result = None
        st.rerun()

st.markdown("""
<div class="stat-box">
  <div class="stat-num">78%</div>
  <div class="stat-text">of people say they wish they had handled at least one important conversation differently. You are not alone.</div>
</div>
""", unsafe_allow_html=True)

# ── Analysis function ─────────────────────────────────────────────────────────
def analyze_screenshot(image_bytes, scenario, key):
    client = Groq(api_key=key)
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = f"""You are Dr. MeFlect, a warm, honest, modern relationship therapist.
Analyze this conversation screenshot. This is a '{scenario}' situation.
Respond ONLY with valid JSON, no markdown, no backticks:
{{
  "tension_score": 7,
  "empathy_score": 4,
  "resolution_score": 3,
  "what_happened": "2-3 sentences explaining the dynamic in plain language",
  "patterns": ["Pattern 1", "Pattern 2", "Pattern 3"],
  "stat_pct": 81,
  "stat_text": "of people struggle with exactly this communication pattern",
  "better_response": "A specific realistic script they could have used instead",
  "how_to_grow": "2-3 sentences of actionable growth advice",
  "verdict": "keep",
  "verdict_title": "Short verdict title",
  "verdict_text": "2-3 sentences explaining the verdict honestly",
  "sentence_starters": ["Starter 1", "Starter 2", "Starter 3", "Starter 4"],
  "apology_steps": ["Step 1 description", "Step 2 description", "Step 3 description", "Step 4 description"]
}}
verdict must be exactly keep or reconsider.
sentence_starters: 4 specific openers they can use RIGHT NOW to respond better.
apology_steps: 4 clear steps to apologize properly if needed."""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]}],
        max_tokens=1200
    )
    raw = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

# ── Results ───────────────────────────────────────────────────────────────────
def show_results(data):
    st.markdown("---")
    st.markdown("### 🧠 Your MeFlect Report")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔥 Tension", f"{data['tension_score']}/10")
    with col2:
        st.metric("💜 Empathy", f"{data['empathy_score']}/10")
    with col3:
        st.metric("🕊️ Resolution", f"{data['resolution_score']}/10")

    st.markdown('<div class="section-label">📖 What happened here</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-box">{data["what_happened"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">🔍 Patterns detected</div>', unsafe_allow_html=True)
    cols = st.columns(len(data["patterns"]))
    colors = ["#FCEBEB", "#FAEEDA", "#EAF3DE"]
    text_colors = ["#A32D2D", "#854F0B", "#27500A"]
    for i, (col, pattern) in enumerate(zip(cols, data["patterns"])):
        col.markdown(f'<span style="background:{colors[i%3]};color:{text_colors[i%3]};padding:5px 12px;border-radius:20px;font-size:0.8rem;font-weight:600">{pattern}</span>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-box" style="margin-top:1rem">
      <div class="stat-num">{data['stat_pct']}%</div>
      <div class="stat-text"><strong>of people</strong> {data['stat_text']}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">💬 How you could have responded</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-box">{data["better_response"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">💡 Sentence starters you can use right now</div>', unsafe_allow_html=True)
    for starter in data.get("sentence_starters", []):
        st.markdown(f'<div class="starter-box">💬 "{starter}"</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">🙏 How to apologize properly</div>', unsafe_allow_html=True)
    for i, step in enumerate(data.get("apology_steps", []), 1):
        st.markdown(f"""
        <div class="apology-step">
          <div class="step-num">{i}</div>
          <div class="step-text">{step}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">🌱 How to grow from this</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-box">{data["how_to_grow"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">⚖️ Verdict</div>', unsafe_allow_html=True)
    v_class = "verdict-keep" if data["verdict"] == "keep" else "verdict-warn"
    icon = "🟢" if data["verdict"] == "keep" else "🟡"
    st.markdown(f'<div class="{v_class}"><strong>{icon} {data["verdict_title"]}</strong><br><span style="font-size:0.9rem">{data["verdict_text"]}</span></div>', unsafe_allow_html=True)

    if st.session_state.plan == "free":
        st.markdown("""
        <div class="ad-box">
          📢 <strong>Ad space</strong> — Watch an ad in the sidebar to earn more analyses!
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="paywall-box">', unsafe_allow_html=True)
    st.markdown("### 🔒 Unlock your full report")
    st.markdown('<div class="paywall-blur">Word-by-word breakdown. Full emotional timeline. Attachment style analysis. Custom 7-day plan. Follow-up script.</div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.button("Monthly $6.99/mo", use_container_width=True)
    with col_b:
        st.button("Annual $3.99/mo ✨", use_container_width=True)
    with col_c:
        st.button("10 Pack $1.99", use_container_width=True)
    st_markdown = st.markdown('</div>', unsafe_allow_html=True)

# ── Main logic ────────────────────────────────────────────────────────────────
if analyze_btn:
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar. It is free at groq.com!")
    elif not uploaded:
        st.warning("Please upload a screenshot first.")
    elif st.session_state.plan == "free" and st.session_state.analyses_used >= total_free:
        st.error("No analyses left! Watch an ad in the sidebar for 1 more, or upgrade.")
    else:
        image_bytes = uploaded.read()
        st.image(Image.open(io.BytesIO(image_bytes)), caption="Your screenshot", use_container_width=True)
        with st.spinner("Dr. MeFlect is reading your conversation..."):
            try:
                result = analyze_screenshot(image_bytes, scenario_hint, api_key)
                st.session_state.analyses_used += 1
                st.session_state.result = result
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.caption("Make sure your Groq API key is correct and try again.")

if st.session_state.result:
    show_results(st.session_state.result)
