import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="M/M/1 Queue Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── Global reset ── */
    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

    /* ── App background ── */
    .stApp { background-color: #0f1117; }

    /* ── Remove top padding ── */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d2e 0%, #1e2130 100%);
        border-right: 1px solid #2d3148;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #a5b4fc;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #2d3148;
        border-radius: 16px;
        padding: 1.5rem 1.25rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        border-radius: 16px 16px 0 0;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(99,102,241,0.18);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #94a3b8 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700;
        color: #e2e8f0 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
        color: #a5b4fc !important;
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* ── Section card wrapper ── */
    .section-card {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
    }

    /* ── Stat row inside Quick Stats ── */
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.65rem 0;
        border-bottom: 1px solid #2d3148;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .stat-value {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .stat-value.highlight { color: #a5b4fc; }

    /* ── Progress bar ── */
    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        border-radius: 99px;
    }
    [data-testid="stProgressBar"] > div {
        background: #2d3148;
        border-radius: 99px;
        height: 10px;
    }

    /* ── Divider ── */
    hr { border-color: #2d3148 !important; }

    /* ── Number inputs ── */
    [data-testid="stNumberInput"] input {
        background: #252840 !important;
        border: 1px solid #3d4266 !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stNumberInput"] input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 12px;
    }

    /* ── Alert/success/error banners ── */
    [data-testid="stAlert"] {
        border-radius: 12px;
        border-width: 1px;
    }

    /* ── Sidebar caption ── */
    [data-testid="stSidebar"] .stCaption { color: #64748b !important; }

    /* ── Headings inside main ── */
    h1 { 
        background: linear-gradient(90deg, #e2e8f0, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
    }
    h2 { color: #cbd5e1 !important; font-weight: 700 !important; }
    h3 { color: #94a3b8 !important; font-weight: 600 !important; }

    /* ── Badge pill ── */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .badge-stable   { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
    .badge-unstable { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

    /* ── Chart labels ── */
    [data-testid="stVegaLiteChart"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    st.markdown("**Input Parameters**")

    lambda_input = st.number_input(
        "λ — Arrival Rate (per hr)",
        min_value=0.1,
        max_value=500.0,
        value=8.0,
        step=0.5,
        help="Average number of customers arriving per hour",
    )
    mu_input = st.number_input(
        "μ — Service Rate (per hr)",
        min_value=0.1,
        max_value=500.0,
        value=9.0,
        step=0.5,
        help="Average number of customers the server can handle per hour",
    )

    st.markdown("---")
    rho = lambda_input / mu_input

    if rho >= 1:
        st.markdown(
            '<span class="badge badge-unstable">⚠ Unstable  ρ = {:.2f}</span>'.format(rho),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="badge badge-stable">✓ Stable  ρ = {:.2f}</span>'.format(rho),
            unsafe_allow_html=True,
        )

    st.markdown("")
    st.caption("Traffic intensity ρ = λ / μ must be < 1 for the system to be stable.")

    st.markdown("---")

    with st.expander("ℹ️ Parameter guide"):
        st.write(
            """
            **λ (Lambda):** Average arrivals per hour.  
            **μ (Mu):** Average service completions per hour.  
            
            *Example: λ = 8, μ = 9 — server handles 9/hr against 8 arrivals/hr.*
            """
        )


# ─── MAIN HEADER ────────────────────────────────────────────────────────────
st.markdown("# M/M/1 Queue Calculator")
st.markdown(
    '<p style="color:#64748b;font-size:1rem;margin-top:-0.5rem;margin-bottom:1.75rem;">'
    "Single-server Poisson queueing system  ·  Performance metrics dashboard"
    "</p>",
    unsafe_allow_html=True,
)

# ─── STABILITY GUARD ────────────────────────────────────────────────────────
if rho >= 1.0:
    st.error(
        f"**System Unstable** — λ ({lambda_input}/hr) ≥ μ ({mu_input}/hr). "
        "The queue grows without bound. Reduce λ or increase μ to stabilise."
    )
    st.stop()


# ─── CALCULATIONS ───────────────────────────────────────────────────────────
p0   = 1 - rho
L_q  = (rho ** 2) / p0
L_s  = L_q + rho
W_s  = 1 / (mu_input - lambda_input)
W_q  = rho / (mu_input - lambda_input)
p_n1     = p0 * rho
p_queue  = 1 - p0 - p_n1          # P(N ≥ 2) → at least one waiting
p_5      = p0 * (rho ** 5)


# ─── METRIC CARDS ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers in System  Ls", f"{L_s:.3f}")
c2.metric("Customers in Queue  Lq",  f"{L_q:.3f}")
c3.metric("Time in System  Ws",      f"{W_s:.3f} hr",  f"{W_s*60:.1f} min")
c4.metric("Time in Queue  Wq",       f"{W_q:.3f} hr",  f"{W_q*60:.1f} min")

st.markdown("<br>", unsafe_allow_html=True)


# ─── CHART + STATS ROW ──────────────────────────────────────────────────────
chart_col, stats_col = st.columns([3, 2], gap="large")

with chart_col:
    st.markdown("### Probability Distribution  P(n)")
    st.caption("Probability that exactly *n* customers are in the system")

    n_range  = 22
    n_values = list(range(n_range))
    p_values = [round(p0 * (rho ** n), 6) for n in n_values]

    df = pd.DataFrame({"Customers n": n_values, "P(n)": p_values})

    st.bar_chart(
        df.set_index("Customers n"),
        color="#6366f1",
        height=340,
        use_container_width=True,
    )

with stats_col:
    st.markdown("### Quick Stats")

    st.markdown("**Server Utilisation**")
    st.progress(rho)
    st.caption(f"Server busy **{rho*100:.1f}%** of the time")

    st.markdown("---")
    st.markdown("**Probability Queries**")

    st.markdown(
        f"""
        <div class="stat-row">
            <span class="stat-label">P(System empty)</span>
            <span class="stat-value highlight">{p0:.2%}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">P(Waiting in queue)</span>
            <span class="stat-value highlight">{p_queue:.2%}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">P(exactly 5 in system)</span>
            <span class="stat-value highlight">{p_5:.4f}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">P(n = 1)</span>
            <span class="stat-value highlight">{p_n1:.2%}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("**Little's Law Verification**")
    st.caption(f"Ls = λ · Ws = {lambda_input} × {W_s:.4f} = **{lambda_input*W_s:.3f}** ≈ {L_s:.3f}")


# ─── PROBABILITY TABLE ──────────────────────────────────────────────────────
with st.expander("📋 Full Probability Table", expanded=False):
    tbl_data = {
        "n": list(range(15)),
        "P(n)": [f"{p0 * (rho**n):.6f}" for n in range(15)],
        "Cumulative P(N ≤ n)": [f"{sum(p0*(rho**k) for k in range(n+1)):.6f}" for n in range(15)],
    }
    st.dataframe(
        pd.DataFrame(tbl_data).set_index("n"),
        use_container_width=True,
    )
