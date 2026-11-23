import html
import json

import streamlit as st

from sparktrack_agent import PHASES, TOTAL, hours_text, readiness_text, run_agent

st.set_page_config(page_title="SparkTrack Milestone Agent", page_icon="⚡", layout="wide")

ICONS = ["📝", "🎨", "💻", "🧪", "🚀"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.block-container { max-width:1150px; padding-top:1.5rem; }

/* ===== Keyframes ===== */
@keyframes gradientShift {0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes fadeUp {from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn {from{opacity:0}to{opacity:1}}
@keyframes slideRight {from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:translateX(0)}}
@keyframes popIn {0%{opacity:0;transform:scale(.92)}60%{transform:scale(1.03)}100%{opacity:1;transform:scale(1)}}
@keyframes float {0%,100%{transform:translateY(0) rotate(-5deg)}50%{transform:translateY(-10px) rotate(5deg)}}
@keyframes pulse {0%{box-shadow:0 0 0 0 rgba(34,197,94,.6)}70%{box-shadow:0 0 0 12px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}
@keyframes pulseRed {0%{box-shadow:0 0 0 0 rgba(239,68,68,.6)}70%{box-shadow:0 0 0 12px rgba(239,68,68,0)}100%{box-shadow:0 0 0 0 rgba(239,68,68,0)}}
@keyframes fillBar {from{width:0}}
@keyframes shimmer {0%{transform:translateX(-120%)}100%{transform:translateX(260%)}}
@keyframes orbit {0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(34px,-22px) scale(1.18)}}
@keyframes glowPulse {0%,100%{box-shadow:0 10px 26px rgba(99,102,241,.35)}50%{box-shadow:0 10px 38px rgba(20,184,166,.55)}}
@keyframes borderFlow {0%{background-position:0% 50%}100%{background-position:200% 50%}}
@keyframes twinkle {0%,100%{opacity:.2;transform:scale(.6)}50%{opacity:1;transform:scale(1.2)}}
@keyframes blobMove {0%,100%{transform:translate(0,0)}50%{transform:translate(40px,30px)}}

/* ===== Background ===== */
.stApp{
 background:
  radial-gradient(900px 520px at 6% -6%, rgba(99,102,241,.16), transparent 60%),
  radial-gradient(800px 520px at 102% 8%, rgba(20,184,166,.16), transparent 60%),
  radial-gradient(700px 520px at 50% 112%, rgba(124,58,237,.12), transparent 60%);
}
::-webkit-scrollbar{width:10px}
::-webkit-scrollbar-thumb{background:linear-gradient(#6366f1,#14b8a6);border-radius:999px}

/* ===== Hero ===== */
.hero{position:relative;overflow:hidden;
 background:linear-gradient(120deg,#4f46e5,#7c3aed,#0ea5e9,#14b8a6);background-size:300% 300%;
 animation:gradientShift 10s ease infinite, popIn .8s ease both;border-radius:26px;padding:2.4rem 2.7rem;color:white;
 margin-bottom:1.6rem;display:flex;align-items:center;justify-content:space-between;
 box-shadow:0 22px 50px -18px rgba(79,70,229,.6), inset 0 1px 0 rgba(255,255,255,.28)}
.hero::before,.hero::after{content:"";position:absolute;border-radius:50%;background:rgba(255,255,255,.15);animation:orbit 9s ease-in-out infinite}
.hero::before{width:230px;height:230px;right:-60px;top:-100px}
.hero::after{width:150px;height:150px;left:40%;bottom:-80px;animation-delay:-4s;background:rgba(255,255,255,.10)}
.hero>div{position:relative;z-index:1}
.hero h1{margin:0;font-size:2.5rem;font-weight:800;letter-spacing:-.02em;text-shadow:0 4px 18px rgba(0,0,0,.25);animation:slideRight .8s ease both}
.hero p{margin:.55rem 0 0;opacity:.95;animation:slideRight .8s .15s ease both}
.hero .bolt{font-size:4.2rem;animation:float 3.2s ease-in-out infinite;filter:drop-shadow(0 8px 14px rgba(0,0,0,.3))}
.hero .shine{position:absolute;top:0;left:0;width:30%;height:100%;z-index:0;
 background:linear-gradient(100deg,transparent,rgba(255,255,255,.22),transparent);
 transform:translateX(-120%);animation:shimmer 6s ease-in-out infinite}

/* ===== Headings ===== */
h2, h3 {letter-spacing:-.01em}
[data-testid="stHeading"] h3 {animation:slideRight .6s ease both}

/* ===== Stat cards ===== */
.card{position:relative;overflow:hidden;
 background:linear-gradient(145deg,rgba(255,255,255,.12),rgba(255,255,255,0)),var(--secondary-background-color);
 border:1px solid rgba(128,128,128,.22);border-radius:20px;padding:1.2rem 1.4rem;animation:fadeUp .7s ease both;
 box-shadow:0 12px 30px -14px rgba(0,0,0,.2);
 transition:transform .3s cubic-bezier(.2,.8,.2,1), box-shadow .3s, border-color .3s}
.card::before{content:"";position:absolute;left:0;top:0;height:4px;width:100%;
 background:linear-gradient(90deg,#6366f1,#14b8a6,#6366f1);background-size:200% 100%;animation:borderFlow 4s linear infinite}
.card::after{content:"";position:absolute;top:0;left:0;width:40%;height:100%;
 background:linear-gradient(100deg,transparent,rgba(255,255,255,.3),transparent);transform:translateX(-120%)}
.card:hover{transform:translateY(-7px) scale(1.02);border-color:rgba(99,102,241,.55);box-shadow:0 24px 42px -16px rgba(99,102,241,.45)}
.card:hover::after{animation:shimmer 1.1s ease}
.card .lbl{font-size:.78rem;text-transform:uppercase;letter-spacing:.1em;opacity:.7;font-weight:600}
.card .val{font-size:2rem;font-weight:800;margin-top:.25rem}
.card .sub{font-size:.85rem;opacity:.65}
div[data-testid="column"]:nth-child(1) .card{animation-delay:.05s}
div[data-testid="column"]:nth-child(2) .card{animation-delay:.15s}
div[data-testid="column"]:nth-child(3) .card{animation-delay:.25s}
div[data-testid="column"]:nth-child(4) .card{animation-delay:.35s}

/* ===== Badge ===== */
.badge{display:inline-block;padding:.4rem 1rem;border-radius:999px;font-weight:800;color:white;font-size:1.05rem;letter-spacing:.04em}
.badge.ok{background:linear-gradient(135deg,#22c55e,#059669);animation:pulse 1.8s infinite}
.badge.no{background:linear-gradient(135deg,#ef4444,#be123c);animation:pulseRed 1.8s infinite}

/* ===== Progress bars ===== */
.phase{margin:.75rem 0;padding:.7rem .95rem;border-radius:14px;background:rgba(128,128,128,.07);
 border:1px solid rgba(128,128,128,.12);animation:fadeUp .6s ease both;transition:transform .25s, background .25s}
.phase:hover{transform:translateX(6px);background:rgba(99,102,241,.09)}
.phase .row{display:flex;justify-content:space-between;font-weight:600;font-size:.95rem}
.bar{height:14px;background:rgba(128,128,128,.22);border-radius:999px;overflow:hidden;margin-top:.45rem;box-shadow:inset 0 2px 4px rgba(0,0,0,.12)}
.bar>div{position:relative;height:100%;border-radius:999px;background:linear-gradient(90deg,#6366f1,#14b8a6);
 animation:fillBar 1.2s cubic-bezier(.2,.8,.2,1) both;transition:width .6s cubic-bezier(.2,.8,.2,1);box-shadow:0 0 12px rgba(99,102,241,.5)}
.bar>div::after{content:"";position:absolute;inset:0;background:linear-gradient(100deg,transparent,rgba(255,255,255,.55),transparent);animation:shimmer 2.4s ease-in-out infinite}
.bar>div.full{background:linear-gradient(90deg,#22c55e,#16a34a);box-shadow:0 0 14px rgba(34,197,94,.6)}

/* ===== Trace steps ===== */
.step{border-left:5px solid #6366f1;padding:.8rem 1.1rem;margin:.7rem 0;border-radius:0 16px 16px 0;
 background:linear-gradient(90deg,rgba(99,102,241,.10),transparent 60%),var(--secondary-background-color);
 box-shadow:0 8px 22px -14px rgba(0,0,0,.35);animation:slideRight .6s ease both;transition:transform .25s, box-shadow .25s}
.step:hover{transform:translateX(6px);box-shadow:0 14px 28px -14px rgba(99,102,241,.5)}
.step.tool{border-left-color:#14b8a6;background:linear-gradient(90deg,rgba(20,184,166,.12),transparent 60%),var(--secondary-background-color)}
.step.final{border-left-color:#22c55e;background:linear-gradient(90deg,rgba(34,197,94,.12),transparent 60%),var(--secondary-background-color)}
.step b{display:block;font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;opacity:.75;margin-bottom:.2rem}
.step code{white-space:pre-wrap}

/* ===== Buttons ===== */
.stButton>button, .stDownloadButton>button{border-radius:14px;font-weight:700;position:relative;overflow:hidden;
 transition:transform .2s cubic-bezier(.2,.8,.2,1), box-shadow .3s}
.stButton>button:hover, .stDownloadButton>button:hover{transform:translateY(-3px) scale(1.02)}
.stButton>button:active, .stDownloadButton>button:active{transform:scale(.97)}
.stButton>button[kind="primary"]{background:linear-gradient(120deg,#6366f1,#7c3aed,#0ea5e9,#14b8a6);background-size:300% 300%;
 animation:gradientShift 6s ease infinite, glowPulse 2.6s ease-in-out infinite;border:none;color:white;padding:.7rem 1rem;font-size:1.05rem}
.stButton>button[kind="primary"]:hover{box-shadow:0 16px 36px rgba(99,102,241,.55)}
.stButton>button[kind="primary"]::after{content:"";position:absolute;top:0;left:0;width:35%;height:100%;
 background:linear-gradient(100deg,transparent,rgba(255,255,255,.4),transparent);transform:translateX(-120%);animation:shimmer 3s ease-in-out infinite}
.stDownloadButton>button{border:1px solid rgba(99,102,241,.5)}
.stDownloadButton>button:hover{box-shadow:0 10px 24px -8px rgba(99,102,241,.5);border-color:#6366f1}

/* ===== Expanders & checkboxes ===== */
[data-testid="stExpander"]{border-radius:18px;border:1px solid rgba(128,128,128,.22);overflow:hidden;
 box-shadow:0 8px 24px -14px rgba(0,0,0,.25);animation:fadeUp .6s ease both;transition:transform .25s, box-shadow .25s, border-color .25s}
[data-testid="stExpander"]:hover{transform:translateY(-3px);border-color:rgba(99,102,241,.5);box-shadow:0 16px 32px -16px rgba(99,102,241,.45)}
[data-testid="stExpander"] summary{font-weight:700;transition:background .2s}
[data-testid="stExpander"] summary:hover{background:rgba(99,102,241,.08)}
[data-testid="stExpander"] details[open]>div{animation:fadeIn .5s ease both}
[data-testid="stCheckbox"]{padding:.15rem .4rem;border-radius:10px;transition:background .2s, transform .2s}
[data-testid="stCheckbox"]:hover{background:rgba(99,102,241,.09);transform:translateX(5px)}
[data-testid="stCheckbox"]:active label span:first-child{transform:scale(.8)}

/* ===== Inputs / radio ===== */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input{border-radius:12px;transition:box-shadow .25s, transform .2s}
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus{box-shadow:0 0 0 3px rgba(99,102,241,.35);transform:translateY(-1px)}
[data-testid="stNumberInput"] button{transition:transform .15s}
[data-testid="stNumberInput"] button:hover{transform:scale(1.15)}
[data-testid="stRadio"] label{padding:.35rem .8rem;border-radius:999px;transition:background .2s, transform .2s}
[data-testid="stRadio"] label:hover{background:rgba(99,102,241,.12);transform:translateY(-2px)}

/* ===== Sidebar ===== */
[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(99,102,241,.10),rgba(20,184,166,.08)),var(--secondary-background-color);
 border-right:1px solid rgba(128,128,128,.2)}
[data-testid="stSidebar"]>div{animation:slideRight .7s ease both}
[data-testid="stSidebar"] [data-testid="stAlert"]{border-radius:14px}

/* ===== Alerts / divider ===== */
[data-testid="stAlert"]{border-radius:16px;animation:popIn .6s ease both;box-shadow:0 10px 26px -16px rgba(0,0,0,.4)}
hr{border:none!important;height:3px!important;border-radius:999px;background:linear-gradient(90deg,transparent,#6366f1,#14b8a6,transparent)!important;opacity:.6}
[data-testid="stCaptionContainer"]{animation:fadeIn .8s ease both}

@media (prefers-reduced-motion: reduce){
 *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}
}
</style>
<div class="hero"><div class="shine"></div><div><h1>SparkTrack Milestone Agent</h1>
<p>Tick the subtopics your team has completed. The AI agent checks if you are on track.</p></div>
<div class="bolt">⚡</div></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    model = st.text_input("Ollama model", value="qwen2.5:3b")
    st.info("Keep `ollama serve` running in another window.")
    team_name = st.text_input("Team name", value="Team Alpha")
    st.caption("Connecting the real SparkTrack site is future work.")

left, right = st.columns([1.2, 1])

# ---------- Left: team ticks completed subtopics ----------
done_per_phase = []
with left:
    st.subheader("✅ Mark completed subtopics")
    for pi, (phase, subs) in enumerate(PHASES.items()):
        with st.expander(f"{ICONS[pi]} {phase}", expanded=True):
            ticks = [st.checkbox(s, key=f"{pi}_{si}") for si, s in enumerate(subs)]
            done_per_phase.append(sum(ticks))

completed = sum(done_per_phase)
remaining = TOTAL - completed
pct = completed / TOTAL * 100

# ---------- Right: live progress ----------
with right:
    st.subheader("📊 Milestone progress")
    for pi, (phase, subs) in enumerate(PHASES.items()):
        d, n = done_per_phase[pi], len(subs)
        cls = "full" if d == n else ""
        st.markdown(
            f'<div class="phase" style="animation-delay:{pi * 0.12}s"><div class="row"><span>{ICONS[pi]} {phase}</span><span>{d}/{n}</span></div>'
            f'<div class="bar"><div class="{cls}" style="width:{d / n * 100}%"></div></div></div>',
            unsafe_allow_html=True)
    st.markdown("**Deadline details**")
    days = st.number_input("Days left until submission", min_value=1, value=5)
    hps = st.number_input("Hours needed per subtopic", min_value=0.5, value=2.0, step=0.5)

# ---------- Cards ----------
badge = ('<span class="badge ok">ON TRACK</span>' if pct >= 80
         else '<span class="badge no">NOT READY</span>')
cards = [("Status", badge, "target: 80% of subtopics"),
         ("Completed", f"{completed}/{TOTAL}", f"{pct:.1f}% of subtopics"),
         ("Remaining", str(remaining), "subtopics to finish"),
         ("Hours per day", f"{remaining * hps / days:.2f}", f"{days} days at {hps:g} h each")]
for col, (lbl, val, sub) in zip(st.columns(4), cards):
    col.markdown(f'<div class="card"><div class="lbl">{lbl}</div><div class="val">{val}</div>'
                 f'<div class="sub">{sub}</div></div>', unsafe_allow_html=True)

# ---------- Ask the agent ----------
st.markdown("---")
mode = st.radio("What should the agent answer?",
                ["Readiness only (one tool)", "Readiness + hours per day (two tools)"], horizontal=True)
if st.button("⚡ Ask the agent", type="primary", use_container_width=True):
    if mode.startswith("Readiness only"):
        q = (f"{team_name} has completed {completed} of {TOTAL} subtopics. "
             "Are we on track for submission?")
    else:
        q = (f"{team_name} has completed {completed} of {TOTAL} subtopics, has {days} days left "
             f"and needs about {hps:g} hours per subtopic. Are we on track, and how many hours "
             "per day must we work?")
    st.write(f"**Question sent to agent:** {q}")
    try:
        with st.spinner("The agent is thinking... (CPU mode can take up to a minute)"):
            run = run_agent(q, model)
    except Exception as exc:
        st.error(f"Agent failed: {exc}")
        st.info("Check that `ollama serve` is running and the model name is correct.")
        st.stop()

    st.subheader("🤖 Agent result")
    st.success(run["final_answer"] or "No answer returned.")
    st.subheader("🔎 Tool trace")
    steps = []
    for item in run["message_trace"]:
        if item["step"] == "model" and item["tool_calls"]:
            steps.append(("MODEL calls", json.dumps(item["tool_calls"]), ""))
        elif item["step"] == "model":
            steps.append(("MODEL final answer", item["content"], "final"))
        elif item["step"] == "tool":
            steps.append((f"TOOL {item['name']}", item["content"], "tool"))
    for n, (label, text, cls) in enumerate(steps):
        st.markdown(f'<div class="step {cls}" style="animation-delay:{n * 0.35}s"><b>{html.escape(label)}</b>'
                    f'<code>{html.escape(str(text))}</code></div>', unsafe_allow_html=True)
    st.caption("Plain-Python cross-check: " + readiness_text(completed) + " " + hours_text(completed, days, hps))
    st.download_button("Download trace JSON", json.dumps(run, indent=2), "trace.json", "application/json")
