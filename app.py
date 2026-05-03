"""AI Courtroom — Multi-Agent Debate Arena — Streamlit UI."""

import os
import time

import plotly.graph_objects as go
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Courtroom",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

    .court-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #0f172a 100%);
        border: 2px solid #f59e0b;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .court-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(ellipse at center, rgba(245,158,11,0.08) 0%, transparent 70%);
    }
    .court-header h1 {
        color: #f59e0b;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 2px 20px rgba(245,158,11,0.3);
    }
    .court-header p {
        color: #94a3b8;
        font-size: 1.15rem;
        margin: 0.5rem 0 0;
        font-family: 'Inter', sans-serif;
    }

    .agent-card {
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .agent-research { background: rgba(59,130,246,0.08); border-left-color: #3b82f6; }
    .agent-prosecution { background: rgba(239,68,68,0.08); border-left-color: #ef4444; }
    .agent-defense { background: rgba(34,197,94,0.08); border-left-color: #22c55e; }
    .agent-crossexam { background: rgba(168,85,247,0.08); border-left-color: #a855f7; }
    .agent-judge { background: rgba(245,158,11,0.08); border-left-color: #f59e0b; }

    .agent-label {
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    .label-research { color: #3b82f6; }
    .label-prosecution { color: #ef4444; }
    .label-defense { color: #22c55e; }
    .label-crossexam { color: #a855f7; }
    .label-judge { color: #f59e0b; }

    .verdict-card {
        background: linear-gradient(135deg, rgba(245,158,11,0.12) 0%, rgba(245,158,11,0.04) 100%);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .verdict-text {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    .verdict-sustained { color: #22c55e; }
    .verdict-overruled { color: #ef4444; }
    .verdict-partial { color: #f59e0b; }

    .stat-box {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .step-flow {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    .step-node {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .step-active { background: #f59e0b; color: #0f172a; }
    .step-done { background: rgba(34,197,94,0.2); color: #22c55e; border: 1px solid #22c55e; }
    .step-pending { background: rgba(255,255,255,0.05); color: #64748b; border: 1px solid rgba(255,255,255,0.1); }
    .step-arrow { color: #475569; font-size: 1.2rem; }

    .topic-chip {
        display: inline-block;
        background: rgba(245,158,11,0.1);
        border: 1px solid rgba(245,158,11,0.3);
        color: #f59e0b;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        cursor: pointer;
    }

    .tech-badge {
        display: inline-block;
        background: rgba(245,158,11,0.08);
        border: 1px solid rgba(245,158,11,0.2);
        color: #fbbf24;
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
    }
</style>""",
    unsafe_allow_html=True,
)

# ── Session state ────────────────────────────────────────────────────────────
for key, default in [
    ("trial_running", False),
    ("trial_result", None),
    ("trial_history", []),
    ("stage", "idle"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key = st.text_input(
        "Groq API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
    )
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    st.divider()

    st.markdown("### 🏛️ Sample Debates")
    sample_claims = [
        "Artificial Intelligence will replace most white-collar jobs within 10 years",
        "Remote work is more productive than office work",
        "Social media does more harm than good to society",
        "Cryptocurrency will eventually replace traditional banking",
        "Universal Basic Income is economically viable and necessary",
        "Space colonization should be humanity's top priority",
        "Nuclear energy is the best solution to climate change",
        "College education is no longer worth the cost",
    ]
    for claim in sample_claims:
        if st.button(f"⚖️ {claim}", key=f"sample_{hash(claim)}", use_container_width=True):
            st.session_state["_pending_claim"] = claim
            st.rerun()

    st.divider()

    tech_badges = ["LangGraph", "Groq / Llama 3.1", "Multi-Agent", "DuckDuckGo", "Streamlit", "Plotly"]
    st.markdown(
        " ".join(f'<span class="tech-badge">{t}</span>' for t in tech_badges),
        unsafe_allow_html=True,
    )

    st.divider()
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.trial_history = []
        st.session_state.trial_result = None
        st.rerun()


# ── Helper: build score chart ────────────────────────────────────────────────

def build_radar_chart(scores: dict) -> go.Figure:
    """Build a radar chart comparing prosecution vs defense."""
    categories = ["Argument Strength", "Evidence Quality", "Logic", "Persuasion", "Confidence"]
    p_score = scores.get("prosecution_score", 5)
    d_score = scores.get("defense_score", 5)
    ev_score = scores.get("evidence_quality", 5)
    confidence = scores.get("confidence", 50)

    # Derive approximate values for the radar
    prosecution_vals = [p_score, ev_score, min(p_score + 1, 10), max(p_score - 1, 1), confidence / 10]
    defense_vals = [d_score, ev_score, min(d_score + 1, 10), max(d_score - 1, 1), (100 - confidence) / 10]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=prosecution_vals + [prosecution_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="🔴 Prosecution",
        line_color="#ef4444",
        fillcolor="rgba(239,68,68,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=defense_vals + [defense_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="🟢 Defense",
        line_color="#22c55e",
        fillcolor="rgba(34,197,94,0.15)",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        ),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f1f5f9"),
        margin=dict(l=60, r=60, t=30, b=30),
        height=350,
    )
    return fig


def build_bar_chart(scores: dict) -> go.Figure:
    """Build a horizontal bar chart comparing scores."""
    p = scores.get("prosecution_score", 5)
    d = scores.get("defense_score", 5)
    ev = scores.get("evidence_quality", 5)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Evidence Quality", "Defense", "Prosecution"],
        x=[ev, d, p],
        orientation="h",
        marker_color=["#3b82f6", "#22c55e", "#ef4444"],
        text=[f"{ev}/10", f"{d}/10", f"{p}/10"],
        textposition="auto",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f1f5f9"),
        xaxis=dict(range=[0, 10], gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=200,
        showlegend=False,
    )
    return fig


# ── Progress indicator ───────────────────────────────────────────────────────

def render_progress(current_stage: str):
    """Render the pipeline progress bar."""
    stages = [
        ("🔍 Research", "research"),
        ("🔴 Prosecution", "prosecution"),
        ("🟢 Defense", "defense"),
        ("⚔️ Cross-Exam", "cross_exam"),
        ("⚖️ Verdict", "verdict"),
    ]
    stage_order = [s[1] for s in stages]
    current_idx = stage_order.index(current_stage) if current_stage in stage_order else -1

    html_parts = []
    for i, (label, _) in enumerate(stages):
        if i < current_idx:
            css = "step-done"
        elif i == current_idx:
            css = "step-active"
        else:
            css = "step-pending"
        html_parts.append(f'<span class="step-node {css}">{label}</span>')
        if i < len(stages) - 1:
            html_parts.append('<span class="step-arrow">→</span>')

    st.markdown(
        f'<div class="step-flow">{"".join(html_parts)}</div>',
        unsafe_allow_html=True,
    )


# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="court-header">
    <h1>⚖️ AI Courtroom</h1>
    <p>Multi-Agent Debate Arena — Present a claim and watch AI agents argue, cross-examine, and deliver a verdict</p>
</div>""",
    unsafe_allow_html=True,
)

# ── How it works ─────────────────────────────────────────────────────────────
with st.expander("🏛️ How the Courtroom Works", expanded=False):
    cols = st.columns(5)
    icons = ["🔍", "🔴", "🟢", "⚔️", "⚖️"]
    titles = ["Research Clerk", "Prosecution", "Defense", "Cross-Exam", "Judge"]
    descs = [
        "Searches the web for real evidence on both sides",
        "Builds the strongest case FOR the claim",
        "Dismantles the prosecution's case AGAINST the claim",
        "Analyzes weaknesses in both arguments",
        "Delivers final verdict with confidence score",
    ]
    for col, icon, title, desc in zip(cols, icons, titles, descs):
        col.markdown(f"**{icon} {title}**")
        col.caption(desc)

st.markdown("")

# ── Input ────────────────────────────────────────────────────────────────────
pending = st.session_state.pop("_pending_claim", None)
if pending:
    st.session_state["claim_text"] = pending

claim_input = st.text_input(
    "🏛️ Present your claim to the court",
    placeholder="e.g., 'AI will replace most white-collar jobs within 10 years'",
    key="claim_text",
)

col_submit, col_info = st.columns([1, 3])
start_trial = col_submit.button("⚖️ Begin Trial", type="primary", use_container_width=True)
col_info.caption("The AI courtroom will research, debate, cross-examine, and deliver a verdict on your claim.")

# ── Run trial ────────────────────────────────────────────────────────────────

if start_trial and claim_input and api_key:
    from agents.graph import build_courtroom_graph

    st.markdown("---")
    st.markdown(f"### 🏛️ Trial: *\"{claim_input}\"*")

    graph = build_courtroom_graph()

    # Stage 1: Research
    render_progress("research")
    with st.status("🔍 **Research Clerk** gathering evidence...", expanded=True) as status:
        st.write("Searching the web for evidence on both sides...")
        result = {"claim": claim_input, "stage": "started"}

        # Run research node
        from agents.nodes import research_node
        result.update(research_node(result))
        status.update(label="🔍 Research complete!", state="complete")

    with st.expander("📋 Research Brief", expanded=False):
        st.markdown(
            f'<div class="agent-card agent-research">'
            f'<div class="agent-label label-research">🔍 Court Research Clerk</div>'
            f'{result["research"]}</div>',
            unsafe_allow_html=True,
        )

    # Stage 2: Prosecution
    render_progress("prosecution")
    with st.status("🔴 **Prosecution** building the case...", expanded=True) as status:
        st.write("Constructing arguments IN FAVOR of the claim...")
        from agents.nodes import prosecution_node
        result.update(prosecution_node(result))
        status.update(label="🔴 Prosecution rests!", state="complete")

    with st.expander("🔴 Prosecution Argument", expanded=True):
        st.markdown(
            f'<div class="agent-card agent-prosecution">'
            f'<div class="agent-label label-prosecution">🔴 Prosecution Attorney</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(result["prosecution_argument"])

    # Stage 3: Defense
    render_progress("defense")
    with st.status("🟢 **Defense** preparing rebuttal...", expanded=True) as status:
        st.write("Dismantling the prosecution's case...")
        from agents.nodes import defense_node
        result.update(defense_node(result))
        status.update(label="🟢 Defense rests!", state="complete")

    with st.expander("🟢 Defense Argument", expanded=True):
        st.markdown(
            f'<div class="agent-card agent-defense">'
            f'<div class="agent-label label-defense">🟢 Defense Attorney</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(result["defense_argument"])

    # Stage 4: Cross-Examination
    render_progress("cross_exam")
    with st.status("⚔️ **Cross-Examination** in progress...", expanded=True) as status:
        st.write("Analyzing weaknesses in both arguments...")
        from agents.nodes import cross_examination_node
        result.update(cross_examination_node(result))
        status.update(label="⚔️ Cross-examination complete!", state="complete")

    with st.expander("⚔️ Cross-Examination Analysis", expanded=False):
        st.markdown(
            f'<div class="agent-card agent-crossexam">'
            f'<div class="agent-label label-crossexam">⚔️ Cross-Examination Specialist</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(result["cross_examination"])

    # Stage 5: Judge's Verdict
    render_progress("verdict")
    with st.status("⚖️ **Judge** deliberating...", expanded=True) as status:
        st.write("Weighing all evidence and arguments...")
        from agents.nodes import judge_node
        result.update(judge_node(result))
        status.update(label="⚖️ Verdict delivered!", state="complete")

    # ── Display Verdict ──────────────────────────────────────────────────
    st.markdown("---")
    scores = result.get("scores", {})
    verdict_val = scores.get("verdict", "PARTIALLY SUSTAINED")
    confidence = scores.get("confidence", 50)

    if "SUSTAINED" in verdict_val and "PARTIALLY" not in verdict_val:
        verdict_class = "verdict-sustained"
        verdict_emoji = "✅"
    elif "OVERRULED" in verdict_val:
        verdict_class = "verdict-overruled"
        verdict_emoji = "❌"
    else:
        verdict_class = "verdict-partial"
        verdict_emoji = "⚠️"

    st.markdown(
        f'<div class="verdict-card">'
        f'<div style="font-size:3rem">{verdict_emoji}</div>'
        f'<div class="verdict-text {verdict_class}">{verdict_val}</div>'
        f'<div style="color:#94a3b8; font-size:1.1rem">Confidence: {confidence}%</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Score cards
    c1, c2, c3, c4 = st.columns(4)
    score_data = [
        (c1, f"{scores.get('prosecution_score', 5)}/10", "Prosecution", "#ef4444"),
        (c2, f"{scores.get('defense_score', 5)}/10", "Defense", "#22c55e"),
        (c3, f"{scores.get('evidence_quality', 5)}/10", "Evidence", "#3b82f6"),
        (c4, f"{confidence}%", "Confidence", "#f59e0b"),
    ]
    for col, val, label, color in score_data:
        col.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-value" style="color:{color}">{val}</div>'
            f'<div class="stat-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("#### 📊 Argument Comparison")
        st.plotly_chart(build_radar_chart(scores), use_container_width=True)
    with chart_col2:
        st.markdown("#### 📈 Score Breakdown")
        st.plotly_chart(build_bar_chart(scores), use_container_width=True)

    # Full verdict text
    with st.expander("⚖️ Full Judicial Opinion", expanded=True):
        st.markdown(
            f'<div class="agent-card agent-judge">'
            f'<div class="agent-label label-judge">⚖️ Presiding Judge</div></div>',
            unsafe_allow_html=True,
        )
        # Remove JSON block from display
        import re
        display_verdict = re.sub(r"```json.*?```", "", result["verdict"], flags=re.DOTALL).strip()
        st.markdown(display_verdict)

    # Tags
    tags = scores.get("tags", [])
    if tags:
        tag_html = " ".join(f'<span class="topic-chip">{t}</span>' for t in tags)
        st.markdown(f"**🏷️ Topics:** {tag_html}", unsafe_allow_html=True)

    # Save to history
    st.session_state.trial_history.append({
        "claim": claim_input,
        "verdict": verdict_val,
        "confidence": confidence,
        "scores": scores,
    })
    st.session_state.trial_result = result

elif start_trial and not api_key:
    st.warning("Please enter your Groq API key in the sidebar.")
elif start_trial and not claim_input:
    st.warning("Please enter a claim to debate.")

# ── Trial History ────────────────────────────────────────────────────────────
if st.session_state.trial_history and not (start_trial and claim_input and api_key):
    st.markdown("---")
    st.markdown("### 📜 Trial History")
    for i, trial in enumerate(reversed(st.session_state.trial_history)):
        v = trial["verdict"]
        emoji = "✅" if "SUSTAINED" in v and "PARTIALLY" not in v else ("❌" if "OVERRULED" in v else "⚠️")
        st.markdown(
            f"**{emoji} {v}** ({trial['confidence']}% confidence) — *\"{trial['claim']}\"*"
        )

# ── Empty state ──────────────────────────────────────────────────────────────
if not st.session_state.trial_history and not (start_trial and claim_input):
    st.markdown("---")
    st.info("👈 Enter a claim above or pick a sample debate from the sidebar to begin a trial.")
