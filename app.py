import streamlit as st
from orchestrator import build_workflow

st.set_page_config(
    page_title="Aria — Customer Help Center",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SVG icons ---
ICON_SPARKLE = '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#00b4d8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"/><path d="M19 14l1 3 3 1-3 1-1 3-1-3-3-1 3-1z"/></svg>'
ICON_CHECK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
ICON_SEARCH = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
ICON_ROUTE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="19" r="3"/><circle cx="18" cy="5" r="3"/><path d="M6 16V8a5 5 0 0 1 5-5h4"/></svg>'
ICON_BOOK = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>'
ICON_PEN = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5z"/></svg>'
ICON_SHIELD = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>'
ICON_MESSAGE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00b4d8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'

# --- Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp, .stMarkdown, h1, h2, h3, h4, p, label, button, span, div {
    font-family: 'Inter', -apple-system, sans-serif !important;
}

.stApp {
    background: linear-gradient(180deg, #0a0e1a 0%, #0f1424 100%);
}


.stDeployButton {display: none;}
.block-container {
    padding-top: 2rem !important;
    max-width: 1280px !important;
}

/* ── HERO */
.hero-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.hero-brand-name {
    font-size: 3.5rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -2.5px;
    margin: 0;
    line-height: 1;
}

.hero-tagline {
    font-size: 2.5rem;
    color: #ffffff;
    font-weight: 600;
    margin: 0 0 10px 0;
    letter-spacing: -0.5px;
}

.hero-description {
    font-size: 1rem;
    color: #a5adc5;
    line-height: 1.65;
    margin: 0 0 12px 0;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 180, 216, 0.08);
    border: 1px solid rgba(0, 180, 216, 0.4);
    color: #00b4d8;
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}

/* Vertical divider between hero columns */
.hero-divider-vertical {
    width: 1px;
    background: #1f2438;
    align-self: stretch;
    margin: 0 auto;
}

.input-label {
    color: #d6dceb;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    margin-bottom: 12px;
    margin-top: 18px;
    display: block;
}

/* Horizontal divider below hero */
.hero-divider {
    height: 1px;
    background: #1f2438;
    margin: 40px 0 32px 0;
}

/* ── INPUTS */
.stTextArea textarea {
    background-color: #161c2e !important;
    border: 1px solid #2a3148 !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 16px !important;
    resize: none !important;
}

.stTextArea > div > div > textarea:focus {
    border-color: #00b4d8 !important;
    box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.12) !important;
    outline: none !important;
}

.stTextArea > div > div,
[data-baseweb="textarea"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* ── PRIMARY BUTTON */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00b4d8 0%, #0096c7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(0, 180, 216, 0.3) !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(0, 180, 216, 0.4) !important;
}

.stButton > button[kind="primary"]:focus {
    outline: 2px solid #00b4d8 !important;
    outline-offset: 2px !important;
}

.stButton > button[kind="primary"]:disabled {
    background: #2a3148 !important;
    color: #6b7593 !important;
    cursor: not-allowed !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── FAQ BUTTONS */
.stButton > button:not([kind="primary"]) {
    background-color: #161c2e !important;
    color: #d6dceb !important;
    border: 1px solid #2a3148 !important;
    border-radius: 10px !important;
    padding: 16px 18px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    height: 180px !important;
    width: 100% !important;
    white-space: normal !important;
    line-height: 1.4 !important;
    transition: all 0.18s ease !important;
}

.stButton > button:not([kind="primary"]):hover {
    border-color: #00b4d8 !important;
    background-color: #1a2138 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 180, 216, 0.15);
}

.stButton > button:not([kind="primary"]):focus {
    outline: 2px solid #00b4d8 !important;
    outline-offset: 2px !important;
}

/* ── SECTION HEADINGS */
.section-heading {
    color: #d6dceb;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    margin: 28px 0 6px 0;
}

.section-subheading {
    color: #a5adc5;
    font-size: 0.95rem;
    margin: 0 0 16px 0;
}

/* ── RESPONSE CARD */
.response-card {
    background: linear-gradient(135deg, #131a2e 0%, #161e36 100%);
    border: 1px solid rgba(0, 180, 216, 0.4);
    border-radius: 16px;
    padding: 24px 28px;
    margin-top: 8px;
    margin-bottom: 12px;
    box-shadow: 0 8px 30px rgba(0, 180, 216, 0.08);
}

.response-label {
    color: #00b4d8;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.response-text {
    color: #ffffff;
    font-size: 1.05rem;
    line-height: 1.7;
    margin: 0;
}

/* ── METRIC TILES */
.metric-tile {
    background: #161c2e;
    border: 1px solid #2a3148;
    border-radius: 12px;
    padding: 16px 20px;
    height: 100%;
    min-height: 150px;
}

.metric-label {
    color: #a5adc5;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
    font-weight: 600;
}

.metric-value {
    color: #ffffff;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}

/* ── TRACE CARDS */
.trace-card {
    background: #161c2e;
    border: 1px solid #2a3148;
    border-radius: 14px;
    padding: 18px 20px;
    margin: 12px;
    height: 100%;
    min-height: 250px;
    box-sizing: border-box;
}

.trace-card-success { border-color: rgba(0, 180, 216, 0.35); }
.trace-card-warning { border-color: rgba(245, 158, 11, 0.4); }

.trace-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.trace-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #00b4d8 0%, #0096c7 100%);
    border-radius: 9px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.trace-icon-warning {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
}

.trace-step-num {
    color: #8b93b0;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 2px;
}

.trace-step-title {
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: -0.2px;
}

.trace-detail {
    color: #c0c8de;
    font-size: 0.9rem;
    line-height: 1.55;
    margin: 0;
}

.trace-highlight {
    color: #00b4d8;
    font-weight: 600;
}

/* ── FOOTER */
.footer-note {
    color: #6b7593;
    font-size: 0.8rem;
    text-align: center;
    margin: 48px 0 16px 0;
    padding: 16px;
    border-top: 1px solid #1f2438;
}

/* ── COLUMN UTILITIES */
[data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
}

[data-testid="stColumn"] .stButton { width: 100%; }
</style>
""", unsafe_allow_html=True)

col_left, col_div, col_right = st.columns([1, 0.04, 1], gap="small", vertical_alignment="top")

with col_left:
    st.markdown(f"""
    <div class="hero-brand">
        {ICON_SPARKLE}
        <h1 class="hero-brand-name">Aria</h1>
    </div>
    <p class="hero-tagline">Smart help, instantly.</p>
    <p class="hero-description">
        Ask Aria anything about your order, billing, deliveries, or technical issues.
        You'll get a clear answer based on our policies — and if your question needs
        extra attention, we'll connect you to a real person right away.
    </p>
    <div class="status-pill">
        {ICON_CHECK}<span style="margin-left:4px;">Available 24/7</span>
    </div>
    """, unsafe_allow_html=True)

# Visual divider — pure HTML, no Streamlit widget noise
with col_div:
    st.markdown('<div class="hero-divider-vertical"></div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<span class="input-label">How can we help you today?</span>', unsafe_allow_html=True)

    query = st.text_area(
        "Customer question",
        value=st.session_state.get("query", ""),
        height=160,
        placeholder="Type your question or concern here...",
        label_visibility="collapsed",
    )

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    is_input_valid = bool(query and len(query.strip()) >= 3)
    process = st.button(
        "Get Help →",
        type="primary",
        use_container_width=True,
        disabled=not is_input_valid,
    )

st.markdown('<div class="hero-divider"></div>', unsafe_allow_html=True)


# ── Workflow 
@st.cache_resource
def get_workflow():
    return build_workflow()

workflow = get_workflow()


# ── FAQ SECTION
st.markdown('<div class="section-heading">Common Questions</div>', unsafe_allow_html=True)
st.markdown('<p class="section-subheading">Click any of these to see how Aria handles real customer questions</p>', unsafe_allow_html=True)

faqs = [
    ("I was charged twice for my order",  "My credit card was charged twice for the same order"),
    ("My package hasn't arrived yet",      "Where is my package? It was supposed to arrive yesterday"),
    ("I'd like to return a product",       "I want my money back, this product is terrible"),
    ("The app keeps crashing",             "The app keeps crashing when I try to log in"),
    ("I want to share feedback",           "Hi, just wanted to say thanks for the great service!"),
    ("Other questions",                    "asdf qwerty random nonsense"),
]

faq_cols = st.columns(3, gap="small")
for i, (label, msg) in enumerate(faqs):
    with faq_cols[i % 3]:
        if st.button(label, key=f"faq_{i}", use_container_width=True, help=f"Ask: {msg}"):
            st.session_state["query"] = msg
            st.rerun()


# ── PROCESS QUERY 
if process and query and query.strip():
    initial_state = {
        "customer_message": query,
        "intent": None, "confidence": None, "classification_reasoning": None,
        "relevant_policies": None, "sources": None,
        "draft_response": None, "final_response": None,
        "needs_human_review": None, "review_notes": None,
        "escalation_reason": None,
    }

    with st.spinner("Aria is thinking..."):
        result = workflow.invoke(initial_state)

    confidence    = result.get("confidence", 0) or 0
    needs_review  = result.get("needs_human_review", False)
    sources_used  = len(result.get("sources", []) or [])

    # Response card
    st.markdown('<div class="section-heading">Aria\'s answer for you</div>', unsafe_allow_html=True)

    if result.get("final_response"):
        st.markdown(f"""
        <div class="response-card">
            <div class="response-label">
                {ICON_MESSAGE}<span>Your answer</span>
            </div>
            <p class="response-text">{result["final_response"]}</p>
        </div>
        """, unsafe_allow_html=True)

    # Metrics
    confidence_label = (
        "Very confident"   if confidence > 0.8 else
        "Mostly confident" if confidence > 0.5 else
        "Needs more info"
    )
    review_label = "A human will follow up" if needs_review else "Answered automatically"

    m1, m2, m3 = st.columns(3, gap="small")
    with m1:
        st.markdown(f'<div class="metric-tile"><div class="metric-label">How sure is Aria?</div><div class="metric-value">{confidence_label}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-tile"><div class="metric-label">What happens next?</div><div class="metric-value">{review_label}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-tile"><div class="metric-label">Policies referenced</div><div class="metric-value">{sources_used}</div></div>', unsafe_allow_html=True)

    # Trace cards
    st.markdown('<div class="section-heading">How we helped</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-subheading">A peek behind the scenes at how Aria handled your request</p>', unsafe_allow_html=True)

    is_low_confidence = confidence < 0.5
    is_out_of_scope   = result.get("intent") == "other" and not is_low_confidence

    trace_cards = []

    # Step 1 — Understanding
    trace_cards.append(("success", f"""
    <div class="trace-card trace-card-success">
        <div class="trace-card-header">
            <div class="trace-icon">{ICON_SEARCH}</div>
            <div>
                <div class="trace-step-num">Step 1</div>
                <div class="trace-step-title">Understanding your question</div>
            </div>
        </div>
        <p class="trace-detail">
            We identified your question as a <span class="trace-highlight">{result.get('intent', 'general')}</span>
            inquiry. {result.get('classification_reasoning', '')}
        </p>
    </div>
    """))

    # Step 2 — Decision
    if is_low_confidence:
        step2_state = "warning"
        step2_text  = "Your question needs personal attention. We're connecting you with a real support agent who will respond shortly."
    elif is_out_of_scope:
        step2_state = "warning"
        step2_text  = "Your message doesn't fit our usual support topics. We've sent a friendly note pointing you to the right place."
    else:
        step2_state = "success"
        step2_text  = f"Your question fits our <span class='trace-highlight'>{result.get('intent')}</span> support area, so we proceeded to find the right answer."

    icon_class = "trace-icon-warning" if step2_state == "warning" else ""
    trace_cards.append((step2_state, f"""
    <div class="trace-card trace-card-{step2_state}">
        <div class="trace-card-header">
            <div class="trace-icon {icon_class}">{ICON_ROUTE}</div>
            <div>
                <div class="trace-step-num">Step 2</div>
                <div class="trace-step-title">Deciding how to help</div>
            </div>
        </div>
        <p class="trace-detail">{step2_text}</p>
    </div>
    """))

    # Step 3 — Policies
    if result.get("relevant_policies"):
        trace_cards.append(("success", f"""
        <div class="trace-card trace-card-success">
            <div class="trace-card-header">
                <div class="trace-icon">{ICON_BOOK}</div>
                <div>
                    <div class="trace-step-num">Step 3</div>
                    <div class="trace-step-title">Looking up our policies</div>
                </div>
            </div>
            <p class="trace-detail">
                We checked <span class="trace-highlight">{len(result['relevant_policies'])}</span>
                relevant policy sections to make sure your answer is accurate.
            </p>
        </div>
        """))

    # Step 4 — Draft
    if result.get("draft_response"):
        trace_cards.append(("success", f"""
        <div class="trace-card trace-card-success">
            <div class="trace-card-header">
                <div class="trace-icon">{ICON_PEN}</div>
                <div>
                    <div class="trace-step-num">Step 4</div>
                    <div class="trace-step-title">Writing your answer</div>
                </div>
            </div>
            <p class="trace-detail">
                We wrote an initial answer based only on what our policies allow — no guessing, no made-up details.
            </p>
        </div>
        """))

    # Step 5 — Quality check
    if result.get("review_notes"):
        review_state = "warning" if needs_review else "success"
        review_icon  = "trace-icon-warning" if needs_review else ""
        step5_text   = (
            "We double-checked the answer and flagged it for a human to review before sending it to you."
            if needs_review else
            "We double-checked the answer for accuracy and tone — everything looked good."
        )
        trace_cards.append((review_state, f"""
        <div class="trace-card trace-card-{review_state}">
            <div class="trace-card-header">
                <div class="trace-icon {review_icon}">{ICON_SHIELD}</div>
                <div>
                    <div class="trace-step-num">Step 5</div>
                    <div class="trace-step-title">Quality check</div>
                </div>
            </div>
            <p class="trace-detail">{step5_text}</p>
        </div>
        """))

    rows_of_three = [trace_cards[i:i + 3] for i in range(0, len(trace_cards), 3)]
    for row in rows_of_three:
        cols = st.columns(3, gap="small")
        for i, (_state, html) in enumerate(row):
            with cols[i]:
                st.markdown(html, unsafe_allow_html=True)
        for i in range(len(row), 3):
            with cols[i]:
                st.markdown('<div style="visibility:hidden;min-height:220px;"></div>', unsafe_allow_html=True)

elif process:
    st.warning("Please type your question first — at least a few words so Aria can help.")


# ── Footer 
st.markdown("""
<div class="footer-note">
    Aria is a portfolio demonstration of multi-agent AI customer support.
    Built with LangGraph, Pydantic validation, and RAG-grounded responses.
</div>
""", unsafe_allow_html=True)