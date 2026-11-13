import uuid
import streamlit as st
from dotenv import load_dotenv
from langgraph.types import Command
from graph import build_blog_graph, MAX_REVISION

load_dotenv()
st.set_page_config(page_title="Atelier AI | Blog Studio", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html,body,[class*="css"],.stApp {font-family:'DM Sans',sans-serif}
.stApp {background:radial-gradient(ellipse at 78% 2%,#242044 0%,transparent 34%),#0b0c14;color:#f1f0fa}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em}
[data-testid="stSidebar"] {background:#11121e;border-right:1px solid #29293b}
[data-testid="stHeader"] {background:transparent}
.block-container {max-width:1280px;padding-top:2.2rem}
.stButton>button[kind="primary"] {background:linear-gradient(110deg,#7856fa,#ad6cff);border:0;color:white;font-weight:700;box-shadow:0 6px 24px #724fff33}
.stButton>button {border-radius:12px;min-height:44px;transition:.2s}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div {background:#171827!important;border:1px solid #353449!important;border-radius:12px!important;color:#f4f2ff!important}
[data-testid="stMetric"] {background:#171827;border:1px solid #292a3d;padding:18px;border-radius:16px}
[data-testid="stMetricValue"] {font-family:'Space Grotesk';color:#fff}
.stTabs [data-baseweb="tab-list"] {gap:16px}
.stTabs [data-baseweb="tab"] {color:#aaa7c0}
.stTabs [aria-selected="true"] {color:#bb9bff!important}
.hero {background:linear-gradient(115deg,#252044,#16172a 65%,#1a1831);border:1px solid #38314e;border-radius:24px;padding:34px;margin-bottom:25px}
.eyebrow {color:#b5a0ff;letter-spacing:.15em;font-size:12px;font-weight:700;text-transform:uppercase}
.hero h1 {font-size:clamp(30px,4vw,52px);margin:10px 0}
.muted {color:#a5a3b8}
.panel {background:#151624;border:1px solid #303045;border-radius:18px;padding:22px;margin:12px 0 18px}
.step {background:#1b1c2d;border:1px solid #36354b;border-radius:12px;padding:14px 16px;margin:8px 0;color:#e8e4fb}
.step-active {border-color:#9974ff;background:#2b2349}
hr {border-color:#2b2c3c}
</style>''', unsafe_allow_html=True)

if "graph" not in st.session_state:
    st.session_state.graph = build_blog_graph()
if "thread" not in st.session_state:
    st.session_state.thread = str(uuid.uuid4())
if "started" not in st.session_state:
    st.session_state.started = False
if "busy_error" not in st.session_state:
    st.session_state.busy_error = ""

def config():
    return {"configurable": {"thread_id": st.session_state.thread}}

def snapshot():
    return st.session_state.graph.get_state(config()) if st.session_state.started else None

def submit_graph(payload):
    try:
        with st.spinner("Your AI team is working..."):
            st.session_state.graph.invoke(payload, config=config())
        st.session_state.busy_error = ""
    except Exception as exc:
        st.session_state.busy_error = str(exc)
    st.rerun()

with st.sidebar:
    st.markdown("## ✦ ATELIER AI")
    st.caption("YOUR CREATIVE WORKSPACE")
    st.divider()
    st.markdown("**WORKSPACE**")
    st.markdown("✦ &nbsp; Blog Studio")
    st.markdown("◈ &nbsp; Multi-Agent Workflow")
    st.markdown("◉ &nbsp; Human Review")
    st.divider()
    st.markdown("**YOUR AI TEAM**")
    st.markdown("🔎 &nbsp; Researcher · Ideas & outline")
    st.markdown("✍️ &nbsp; Writer · Long-form draft")
    st.markdown("✨ &nbsp; Editor · Final polish")
    st.divider()
    if st.button("＋  New project", use_container_width=True):
        st.session_state.thread = str(uuid.uuid4())
        st.session_state.started = False
        st.session_state.busy_error = ""
        st.rerun()
    st.caption("Powered by LangGraph · Groq")

st.markdown('''<div class="hero"><div class="eyebrow">✦ THE INTELLIGENT WRITING STUDIO</div><h1>Ideas to articles.<br><span style="color:#b294ff">Beautifully orchestrated.</span></h1><div class="muted">Three specialized AI agents, one seamless creative workflow. You stay in control at every step.</div></div>''', unsafe_allow_html=True)

snap = snapshot()
values = snap.values if snap else {}
interrupts = snap.interrupts if snap else ()
pending = interrupts[0].value if interrupts else None
stage = pending.get("stage") if pending else ("finished" if values.get("final_blog") else "setup")

c1,c2,c3 = st.columns(3)
with c1: st.metric("AI specialists", "03")
with c2: st.metric("Draft revisions", f"{values.get('revision_count',0)} / {MAX_REVISION}")
with c3: st.metric("Project status", {"setup":"Ready", "research":"Research review", "draft":"Draft review", "finished":"Complete"}[stage])

left,right = st.columns([1.05,1],gap="large")
with left:
    st.markdown("### Create your next article")
    with st.form("new_blog"):
        topic = st.text_input("Blog topic", placeholder="e.g. How AI agents are transforming software development", disabled=st.session_state.started)
        audience = st.selectbox("Target audience", ["Developers", "General readers", "Students", "Business leaders", "AI enthusiasts", "Technical professionals"], disabled=st.session_state.started)
        start = st.form_submit_button("✦  Generate research", type="primary", use_container_width=True, disabled=st.session_state.started)
    if start:
        if not topic.strip():
            st.warning("Enter a blog topic to get started.")
        else:
            st.session_state.started = True
            submit_graph({"topic":topic.strip(),"audience":audience})

with right:
    st.markdown("### Your workflow")
    steps = [("01", "Research", "Explore and structure ideas"),("02", "Research approval", "You review the outline"),("03", "Writing", "Generate a full article"),("04", "Draft approval", "You refine the writing"),("05", "Editing", "Polish and finalize")]
    active = 1 if stage=="research" else 3 if stage=="draft" else 4 if stage=="finished" else -1
    for i,(num,title,subtitle) in enumerate(steps):
        cls = "step step-active" if i==active else "step"
        symbol = "✓" if i<active else num
        st.markdown(f'<div class="{cls}"><strong>{symbol} &nbsp; {title}</strong><div class="muted" style="font-size:13px;margin-left:29px">{subtitle}</div></div>',unsafe_allow_html=True)

if st.session_state.busy_error:
    st.error("The workflow encountered an error: " + st.session_state.busy_error)
    st.caption("Check your GROQ_API_KEY, model availability, and the terminal logs. You can start a new project if needed.")

if st.session_state.started:
    st.divider()
    st.markdown("## ✦ Content studio")
    research_tab,draft_tab,final_tab = st.tabs(["🔎 Research", "✍️ Draft", "✨ Final article"])
    with research_tab:
        if values.get("research"):
            st.markdown(values["research"])
        else: st.info("Research will appear here after generation.")
    with draft_tab:
        if values.get("draft"):
            st.markdown(values["draft"])
        else: st.info("Approve your research to generate a draft.")
    with final_tab:
        if values.get("final_blog"):
            st.markdown(values["final_blog"])
            st.download_button("↓ Download Markdown",values["final_blog"],file_name="article.md",mime="text/markdown",use_container_width=True)
        else: st.info("Your polished article will appear after draft approval.")

    if pending:
        st.markdown("### Your approval is needed")
        st.caption("Review the content above, then approve or send feedback for another pass.")
        with st.form("review_form",clear_on_submit=False):
            feedback = st.text_area("Revision instructions (optional)",placeholder="e.g. Add more practical examples and simplify the technical language...",height=110)
            approve = st.form_submit_button("✓ Approve & continue",type="primary",use_container_width=True)
            revise = st.form_submit_button("↻ Request revision",use_container_width=True)
        if approve:
            submit_graph(Command(resume={"action":"approve","feedback":""}))
        if revise:
            if not feedback.strip():
                st.warning("Describe what you want the agent to change.")
            elif stage=="draft" and values.get("revision_count",0)>=MAX_REVISION:
                st.warning("Maximum draft revisions reached. Approve to continue to editing.")
            else:
                submit_graph(Command(resume={"action":"revise","feedback":feedback.strip()}))
    elif values.get("final_blog"):
        st.success("Your article is ready to publish!")
