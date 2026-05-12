import streamlit as st
import time
from dotenv import load_dotenv

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="MinuteCraftAI · AI Video Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# ── Lazy imports so the page still renders even without heavy deps ───────────
@st.cache_resource(show_spinner=False)
def get_pipeline_modules():
    from utils.audio_processor import process_input
    from core.transcriber import transcribe_all
    from core.summarizer import summarize, generate_title
    from core.extractor import extract_action_items, extract_key_decisions, extract_questions
    from core.rag_engine import build_rag_chain, ask_question
    return process_input, transcribe_all, summarize, generate_title, \
           extract_action_items, extract_key_decisions, extract_questions, \
           build_rag_chain, ask_question


# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* ── Root tokens ── */
:root {
    --bg:        #0a0b0f;
    --surface:   #111218;
    --surface2:  #16181f;
    --border:    #1f2130;
    --accent:    #6ee7b7;      /* mint green */
    --accent2:   #38bdf8;      /* sky blue   */
    --accent3:   #f472b6;      /* pink       */
    --muted:     #6b7280;
    --text:      #e5e7eb;
    --text-dim:  #9ca3af;
    --radius:    14px;
    --radius-lg: 22px;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Top gradient bar ── */
.top-bar {
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3));
    border-radius: 0 0 4px 4px;
    margin-bottom: 2rem;
}

/* ── Hero / brand header ── */
.hero {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 0.5rem;
}
.hero-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0; padding: 0;
    background: linear-gradient(135deg, #fff 40%, var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 0.82rem;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0;
}

/* ── Metric cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 1.5rem 0;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-color, var(--accent));
}
.metric-card .label {
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 6px;
}
.metric-card .value {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent-color, var(--accent));
}
.metric-card .sub {
    font-size: 0.75rem;
    color: var(--text-dim);
    margin-top: 2px;
}

/* ── Section cards ── */
.section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 1rem;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
}

/* ── Transcript box ── */
.transcript-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    max-height: 380px;
    overflow-y: auto;
    font-size: 0.88rem;
    line-height: 1.8;
    color: var(--text-dim);
    white-space: pre-wrap;
    word-break: break-word;
}
.transcript-box::-webkit-scrollbar { width: 4px; }
.transcript-box::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── Action item / decision tags ── */
.tag-list { display: flex; flex-direction: column; gap: 10px; }
.tag-item {
    display: flex; align-items: flex-start; gap: 12px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px 16px;
    font-size: 0.88rem;
    line-height: 1.55;
}
.tag-icon {
    width: 26px; height: 26px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 1px;
}
.tag-icon.action  { background: rgba(110,231,183,.12); }
.tag-icon.decision{ background: rgba(56,189,248,.12); }
.tag-icon.question{ background: rgba(244,114,182,.12); }

/* ── Chat bubbles ── */
.chat-wrap { display: flex; flex-direction: column; gap: 14px; margin-top: 8px; }
.bubble { display: flex; gap: 12px; align-items: flex-start; }
.bubble.user  { flex-direction: row-reverse; }
.bubble-avatar {
    width: 34px; height: 34px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}
.bubble.user .bubble-avatar  { background: linear-gradient(135deg,var(--accent),var(--accent2)); }
.bubble.ai   .bubble-avatar  { background: var(--surface2); border: 1px solid var(--border); }
.bubble-text {
    max-width: 78%;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 16px;
    font-size: 0.88rem;
    line-height: 1.65;
    color: var(--text);
}
.bubble.user .bubble-text {
    background: rgba(110,231,183,.08);
    border-color: rgba(110,231,183,.2);
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(110,231,183,.1);
    border: 1px solid rgba(110,231,183,.25);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.77rem;
    color: var(--accent);
    font-weight: 500;
    letter-spacing: 0.03em;
}
.pulse {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent);
    animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: .35; transform: scale(.7); }
}

/* ── Streamlit overrides ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    gap: 4px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 8px 18px !important;
    transition: all .2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* inputs & buttons */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #0a0b0f !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 0.55rem 1.6rem !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

.stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    border-radius: 4px !important;
}
.stAlert {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}
[data-testid="stDownloadButton"] > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "result": None,
        "chat_history": [],       # list of {"role": "user"|"ai", "text": str}
        "processing": False,
        "error": None,
        "source": "",
        "language": "english",
        "show_full_transcript": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE RUNNER
# ══════════════════════════════════════════════════════════════════════════════
def run_pipeline_ui(source: str, language: str):
    (process_input, transcribe_all, summarize, generate_title,
     extract_action_items, extract_key_decisions, extract_questions,
     build_rag_chain, ask_question) = get_pipeline_modules()

    status_placeholder = st.empty()
    prog = st.progress(0)

    steps = [
        (0.10, "🎵", "Processing audio / video …"),
        (0.25, "✍️", "Transcribing speech …"),
        (0.45, "🏷️", "Generating title …"),
        (0.58, "📋", "Summarising content …"),
        (0.70, "✅", "Extracting action items …"),
        (0.82, "🔑", "Identifying key decisions …"),
        (0.90, "❓", "Collecting open questions …"),
        (0.97, "🔗", "Building RAG knowledge base …"),
    ]

    def tick(i, msg):
        frac, icon, label = steps[i]
        prog.progress(frac)
        status_placeholder.markdown(
            f'<div class="status-badge"><span class="pulse"></span>{icon} {label}</div>',
            unsafe_allow_html=True,
        )

    tick(0, None)
    chunks = process_input(source)

    tick(1, None)
    transcript = transcribe_all(chunks, language=language)

    tick(2, None)
    title = generate_title(transcript)

    tick(3, None)
    summary = summarize(transcript)

    tick(4, None)
    action_items = extract_action_items(transcript)

    tick(5, None)
    decisions = extract_key_decisions(transcript)

    tick(6, None)
    questions = extract_questions(transcript)

    tick(7, None)
    rag_chain = build_rag_chain(transcript)

    prog.progress(1.0)
    status_placeholder.empty()

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_item": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="hero">
        <div class="hero-icon">🎙️</div>
        <div>
            <h1 style="font-size:1.3rem">MinuteCraftAI</h1>
            <p class="hero-sub">AI Video Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 New Analysis")

    input_mode = st.radio("Source Type", ["YouTube URL", "Upload File"], horizontal=True, label_visibility="collapsed")
    
    if input_mode == "YouTube URL":
        source = st.text_input(
            "YouTube URL",
            placeholder="https://youtu.be/...",
            value=st.session_state.source if st.session_state.source.startswith("http") else "",
        )
        uploaded_file = None
    else:
        uploaded_file = st.file_uploader("Drop video or audio file here", type=["mp4", "mp3", "wav", "m4a", "webm", "ogg"])
        source = ""

    language = st.selectbox(
        "Transcription language",
        ["english", "hinglish", "hindi", "spanish", "french", "german"],
        index=["english","hinglish","hindi","spanish","french","german"].index(
            st.session_state.language
        ),
    )

    analyse_btn = st.button("⚡ Analyse Now", use_container_width=True)

    if analyse_btn:
        final_source = None
        if input_mode == "YouTube URL":
            if not source.strip():
                st.error("Please enter a YouTube URL.")
            else:
                final_source = source.strip()
        else:
            if uploaded_file is None:
                st.error("Please upload a file.")
            else:
                import os
                os.makedirs("downloads", exist_ok=True)
                final_source = os.path.join("downloads", uploaded_file.name)
                with open(final_source, "wb") as f:
                    f.write(uploaded_file.getbuffer())

        if final_source:
            st.session_state.source   = final_source
            st.session_state.language = language
            st.session_state.result   = None
            st.session_state.chat_history = []
            st.session_state.error    = None
            st.session_state.processing = True

    st.markdown("---")

    # ── Capabilities list ──
    st.markdown("### 🧰 Capabilities")
    for cap in [
        ("📝", "Auto-transcription"),
        ("📋", "AI Summary"),
        ("✅", "Action Items"),
        ("🔑", "Key Decisions"),
        ("❓", "Open Questions"),
        ("💬", "Chat with RAG"),
        ("📥", "Export results"),
    ]:
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:center;'
            f'padding:6px 0;font-size:.85rem;color:var(--text-dim,#9ca3af)">'
            f'<span>{cap[0]}</span><span>{cap[1]}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        '<p style="font-size:.72rem;color:#4b5563;text-align:center">'
        'MinuteCraftAI · Powered by Whisper + LangChain</p>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN AREA — HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="top-bar"></div>', unsafe_allow_html=True)

# Hero title
st.markdown("""
<div class="hero" style="margin-bottom:.4rem">
    <div class="hero-icon" style="width:56px;height:56px;font-size:28px">🎙️</div>
    <div>
        <h1 style="font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;
                   margin:0;background:linear-gradient(135deg,#fff 40%,#6ee7b7);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   background-clip:text">
            MinuteCraftAI
        </h1>
        <p style="margin:0;color:#6b7280;font-size:.85rem;letter-spacing:.08em;
                  text-transform:uppercase">
            AI Video Intelligence Platform
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<p style="color:#6b7280;font-size:.9rem;margin-bottom:1.5rem">'
    'Drop in any YouTube link or local video — MinuteCraftAI transcribes, summarises, '
    'extracts decisions, and lets you <em>chat</em> with your content.</p>',
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE EXECUTION (triggered from sidebar button)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.processing and st.session_state.result is None:
    st.markdown("#### ⚙️ Running analysis pipeline …")
    try:
        result = run_pipeline_ui(st.session_state.source, st.session_state.language)
        st.session_state.result     = result
        st.session_state.processing = False
        st.rerun()
    except Exception as exc:
        st.session_state.error      = str(exc)
        st.session_state.processing = False
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  ERROR STATE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.error:
    st.error(f"**Pipeline error:** {st.session_state.error}")
    if st.button("🔄 Try again"):
        st.session_state.error = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  EMPTY / LANDING STATE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.result is None and not st.session_state.processing:
    col1, col2, col3 = st.columns(3)
    cards = [
        ("🎬", "Video & Audio", "YouTube links, MP4, MP3, WAV — any source", "#6ee7b7"),
        ("🤖", "AI-Powered", "Whisper transcription + LLM analysis", "#38bdf8"),
        ("💬", "Chat Interface", "Ask anything via RAG-based Q&A", "#f472b6"),
    ]
    for col, (icon, title, desc, clr) in zip([col1,col2,col3], cards):
        with col:
            st.markdown(f"""
            <div class="section-card" style="text-align:center;padding:32px 20px">
                <div style="font-size:2.2rem;margin-bottom:12px">{icon}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;
                            font-weight:700;color:{clr};margin-bottom:8px">{title}</div>
                <div style="font-size:.82rem;color:#6b7280;line-height:1.6">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<p style="text-align:center;color:#4b5563;font-size:.85rem">'
        '👈 Enter a URL or file path in the sidebar to begin</p>',
        unsafe_allow_html=True,
    )
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS — loaded
# ══════════════════════════════════════════════════════════════════════════════
result = st.session_state.result

# ── Derive quick stats ──────────────────────────────────────────────────────
transcript_text = result.get("transcript", "")
word_count      = len(transcript_text.split())

def _filter_items(raw: str, empty_phrase: str):
    if not raw or empty_phrase in raw.lower():
        return []
    return [l.strip().lstrip("-•*123456789. ") for l in raw.split("\n") if l.strip()]

action_lines    = _filter_items(result.get("action_item", ""), "no action items found")
decision_lines  = _filter_items(result.get("key_decisions", ""), "no key decisions found")
question_lines  = _filter_items(result.get("open_questions", ""), "no open questions found")

read_min        = max(1, word_count // 200)

# ── Metric row ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card" style="--accent-color:#6ee7b7">
      <div class="label">Words Transcribed</div>
      <div class="value">{word_count:,}</div>
      <div class="sub">≈ {read_min} min read</div>
  </div>
  <div class="metric-card" style="--accent-color:#38bdf8">
      <div class="label">Action Items</div>
      <div class="value">{len(action_lines)}</div>
      <div class="sub">Tasks identified</div>
  </div>
  <div class="metric-card" style="--accent-color:#a78bfa">
      <div class="label">Key Decisions</div>
      <div class="value">{len(decision_lines)}</div>
      <div class="sub">From the content</div>
  </div>
  <div class="metric-card" style="--accent-color:#f472b6">
      <div class="label">Open Questions</div>
      <div class="value">{len(question_lines)}</div>
      <div class="sub">Awaiting answers</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Title banner ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="section-card" style="margin-bottom:1.2rem;
     background:linear-gradient(135deg,rgba(110,231,183,.07),rgba(56,189,248,.07));
     border-color:rgba(110,231,183,.2)">
    <div class="section-title"><span class="dot"></span>Detected Title</div>
    <div style="font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:700;
                color:#fff">{result.get('title','—')}</div>
    <div style="font-size:.78rem;color:#6b7280;margin-top:6px">
        Source: {st.session_state.source[:80]}{'…' if len(st.session_state.source)>80 else ''} ·
        Language: {st.session_state.language.title()}
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📋 Summary",
    "📝 Transcript",
    "✅ Action Items",
    "🔑 Key Decisions",
    "❓ Open Questions",
    "💬 Chat (RAG)",
    "📥 Export",
])


# ── TAB 0 — Summary ──────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("#### 📋 AI-Generated Summary")
    summary_text = result.get("summary", "No summary available.")

    st.markdown(f"""
    <div class="section-card">
        <div class="section-title"><span class="dot"></span>Executive Summary</div>
        <div style="font-size:.92rem;line-height:1.85;color:#d1d5db;
                    white-space:pre-wrap">{summary_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick highlights as bullet chips
    lines = [l.strip() for l in summary_text.split(".") if len(l.strip()) > 30][:5]
    if lines:
        st.markdown("##### 💡 Key Highlights")
        for line in lines:
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:10px;'
                f'margin-bottom:8px">'
                f'<span style="color:#6ee7b7;font-size:1.1rem;margin-top:1px">▸</span>'
                f'<span style="font-size:.88rem;color:#9ca3af;line-height:1.6">{line}.</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── TAB 1 — Transcript ───────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("#### 📝 Full Transcript")

    col_a, col_b = st.columns([3, 1])
    with col_b:
        search_term = st.text_input("🔍 Search transcript", placeholder="keyword …")

    display_text = transcript_text
    if search_term:
        highlighted = transcript_text.replace(
            search_term,
            f'<mark style="background:rgba(110,231,183,.3);color:#fff;'
            f'border-radius:3px;padding:0 3px">{search_term}</mark>',
        )
        st.markdown(
            f'<div class="transcript-box">{highlighted}</div>',
            unsafe_allow_html=True,
        )
        matches = transcript_text.lower().count(search_term.lower())
        st.caption(f"Found **{matches}** occurrence(s) of '{search_term}'")
    else:
        st.markdown(
            f'<div class="transcript-box">{display_text}</div>',
            unsafe_allow_html=True,
        )

    st.caption(f"Total: **{word_count:,} words** · ≈ {read_min} min read")


# ── TAB 2 — Action Items ─────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("#### ✅ Action Items")

    items = action_lines

    if items:
        st.markdown(f'<div class="tag-list">', unsafe_allow_html=True)
        for i, item in enumerate(items, 1):
            st.markdown(f"""
            <div class="tag-item">
                <div class="tag-icon action">✅</div>
                <div>
                    <span style="font-size:.72rem;color:#6ee7b7;
                                 font-weight:600;letter-spacing:.05em">
                        TASK #{i:02d}
                    </span><br>
                    <span style="color:#e5e7eb">{item}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No action items were identified.")


# ── TAB 3 — Key Decisions ────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("#### 🔑 Key Decisions")

    items = decision_lines

    if items:
        for i, item in enumerate(items, 1):
            st.markdown(f"""
            <div class="tag-item" style="margin-bottom:10px">
                <div class="tag-icon decision">🔑</div>
                <div>
                    <span style="font-size:.72rem;color:#38bdf8;
                                 font-weight:600;letter-spacing:.05em">
                        DECISION #{i:02d}
                    </span><br>
                    <span style="color:#e5e7eb">{item}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No key decisions were identified.")


# ── TAB 4 — Open Questions ───────────────────────────────────────────────────
with tabs[4]:
    st.markdown("#### ❓ Open Questions")

    items = question_lines

    if items:
        for i, item in enumerate(items, 1):
            st.markdown(f"""
            <div class="tag-item" style="margin-bottom:10px">
                <div class="tag-icon question">❓</div>
                <div>
                    <span style="font-size:.72rem;color:#f472b6;
                                 font-weight:600;letter-spacing:.05em">
                        QUESTION #{i:02d}
                    </span><br>
                    <span style="color:#e5e7eb">{item}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No open questions were identified.")


# ── TAB 5 — Chat (RAG) ───────────────────────────────────────────────────────
with tabs[5]:
    st.markdown("#### 💬 Chat with Your Content")
    st.markdown(
        '<p style="color:#6b7280;font-size:.85rem;margin-bottom:1.2rem">'
        'Ask anything about the video. The AI answers using only the actual content.</p>',
        unsafe_allow_html=True,
    )

    # render history
    if st.session_state.chat_history:
        html_bubbles = '<div class="chat-wrap">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                html_bubbles += f"""
                <div class="bubble user">
                    <div class="bubble-avatar">👤</div>
                    <div class="bubble-text">{msg['text']}</div>
                </div>"""
            else:
                html_bubbles += f"""
                <div class="bubble ai">
                    <div class="bubble-avatar">🤖</div>
                    <div class="bubble-text">{msg['text']}</div>
                </div>"""
        html_bubbles += "</div>"
        st.markdown(html_bubbles, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # suggested questions
    if not st.session_state.chat_history:
        st.markdown("##### 💡 Suggested questions")
        suggestions = [
            "What is the main topic discussed?",
            "Who are the key people mentioned?",
            "What were the most important conclusions?",
            "Are there any deadlines mentioned?",
        ]
        s_cols = st.columns(2)
        for idx, sug in enumerate(suggestions):
            with s_cols[idx % 2]:
                if st.button(sug, key=f"sug_{idx}", use_container_width=True):
                    st.session_state._pending_question = sug
                    st.rerun()

    # input
    user_q = st.text_input(
        "Your question",
        placeholder="Ask anything about the content …",
        key="chat_input",
        label_visibility="collapsed",
    )

    ask_col, clear_col = st.columns([5, 1])
    with ask_col:
        ask_btn = st.button("Send ➤", use_container_width=True)
    with clear_col:
        if st.button("🗑️", help="Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()

    # handle pending suggestion click
    pending = st.session_state.pop("_pending_question", None)
    final_q = pending or (user_q.strip() if ask_btn else None)

    if final_q:
        _, _, _, _, _, _, _, _, ask_question = get_pipeline_modules()
        st.session_state.chat_history.append({"role": "user", "text": final_q})
        with st.spinner("Thinking …"):
            try:
                answer = ask_question(result["rag_chain"], final_q)
            except Exception as e:
                answer = f"⚠️ Error: {e}"
        st.session_state.chat_history.append({"role": "ai", "text": answer})
        st.rerun()


# ── TAB 6 — Export ───────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown("#### 📥 Export Results")

    # build plain-text export
    export_txt = f"""MinuteCraftAI — AI Video Analysis Report
{'='*60}

📌 TITLE
{result.get('title','—')}

📋 SUMMARY
{result.get('summary','')}

✅ ACTION ITEMS
{result.get('action_item','')}

🔑 KEY DECISIONS
{result.get('key_decisions','')}

❓ OPEN QUESTIONS
{result.get('open_questions','')}

📝 FULL TRANSCRIPT
{transcript_text}
"""

    # build markdown export
    export_md = f"""# {result.get('title','Untitled')}

> *Analysed by MinuteCraftAI · AI Video Intelligence*

## 📋 Summary

{result.get('summary','')}

## ✅ Action Items

{result.get('action_item','')}

## 🔑 Key Decisions

{result.get('key_decisions','')}

## ❓ Open Questions

{result.get('open_questions','')}

## 📝 Full Transcript

{transcript_text}
"""

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="section-card" style="text-align:center">
            <div style="font-size:2rem;margin-bottom:8px">📄</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;
                        color:#6ee7b7;margin-bottom:6px">Plain Text</div>
            <div style="font-size:.8rem;color:#6b7280;margin-bottom:14px">
                Clean .txt for notes apps
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            "⬇ Download .txt",
            data=export_txt,
            file_name="minutecraftai_report.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2:
        st.markdown("""
        <div class="section-card" style="text-align:center">
            <div style="font-size:2rem;margin-bottom:8px">📝</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;
                        color:#38bdf8;margin-bottom:6px">Markdown</div>
            <div style="font-size:.8rem;color:#6b7280;margin-bottom:14px">
                Notion, Obsidian, GitHub
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            "⬇ Download .md",
            data=export_md,
            file_name="minutecraftai_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with c3:
        st.markdown("""
        <div class="section-card" style="text-align:center">
            <div style="font-size:2rem;margin-bottom:8px">💬</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;
                        color:#f472b6;margin-bottom:6px">Chat Log</div>
            <div style="font-size:.8rem;color:#6b7280;margin-bottom:14px">
                Export your Q&amp;A session
            </div>
        </div>
        """, unsafe_allow_html=True)
        chat_log = "\n\n".join(
            f"{'You' if m['role']=='user' else 'MinuteCraftAI'}: {m['text']}"
            for m in st.session_state.chat_history
        ) or "(No chat yet)"
        st.download_button(
            "⬇ Download chat",
            data=chat_log,
            file_name="minutecraftai_chat.txt",
            mime="text/plain",
            use_container_width=True,
        )