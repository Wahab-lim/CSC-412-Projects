import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="RNG Systems",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── Global ── */
    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
    .stApp { background-color: #0f1117; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d2e 0%, #1e2130 100%);
        border-right: 1px solid #2d3148;
    }
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #a5b4fc;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #2d3148;
        border-radius: 16px;
        padding: 1.4rem 1.2rem;
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
        font-size: 0.75rem !important;
        font-weight: 600;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: #94a3b8 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 700;
        color: #e2e8f0 !important;
    }

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

    /* ── Slider ── */
    [data-testid="stSlider"] [role="slider"] {
        background: #6366f1 !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] [role="tablist"] {
        background: #1e2130;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #2d3148;
        gap: 4px;
    }
    [data-testid="stTabs"] [role="tab"] {
        border-radius: 8px;
        color: #64748b;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.45rem 1.2rem;
        transition: all 0.2s;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: #ffffff !important;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #2d3148;
    }

    /* ── Radio buttons ── */
    [data-testid="stRadio"] label {
        color: #cbd5e1 !important;
        font-size: 0.9rem;
    }

    /* ── Buttons ── */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 2rem !important;
        transition: opacity 0.2s, transform 0.2s !important;
        letter-spacing: 0.02em !important;
    }
    [data-testid="stButton"] > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important;
    }

    /* ── Info / warning boxes ── */
    [data-testid="stAlert"] {
        border-radius: 12px;
        border-width: 1px;
    }

    /* ── Divider ── */
    hr { border-color: #2d3148 !important; }

    /* ── Headings ── */
    h1 {
        background: linear-gradient(90deg, #e2e8f0, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    h2 { color: #cbd5e1 !important; font-weight: 700 !important; }
    h3 { color: #94a3b8 !important; font-weight: 600 !important; }

    /* ── Info pill ── */
    .algo-pill {
        display: inline-block;
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(99,102,241,0.3);
        color: #a5b4fc;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.8rem;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }

    /* ── Hint card ── */
    .hint-card {
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.55;
    }
    .hint-card strong { color: #a5b4fc; }
</style>
""", unsafe_allow_html=True)


def generate_lcg(seed, a, c, m, n):
    data, X = [], seed
    for i in range(n):
        X = (a * X + c) % m
        data.append({"Index": i + 1, "Integer (Xi)": X, "Random (Ri)": round(X / m, 6)})
    return pd.DataFrame(data)


def generate_mcg(seed, a, m, n):
    data, X = [], seed
    for i in range(n):
        X = (a * X) % m
        data.append({"Index": i + 1, "Integer (Xi)": X, "Random (Ri)": round(X / m, 6)})
    return pd.DataFrame(data)


def generate_middle_square(seed, n):
    data, X = [], seed
    num_digits = len(str(X))
    for i in range(n):
        sq_str = str(X ** 2).zfill(num_digits * 2)
        start = (len(sq_str) - num_digits) // 2
        X = int(sq_str[start: start + num_digits])
        data.append({"Index": i + 1, "Integer (Xi)": X, "Random (Ri)": round(X / (10 ** num_digits), 6)})
    return pd.DataFrame(data)



with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")

    num_samples = st.slider(
        "Sample Size (N)",
        min_value=5, max_value=1000, value=20, step=5,
        help="Number of random numbers to generate",
    )

    st.markdown("**Algorithm**")
    algorithm = st.radio(
        "Select technique",
        ("Linear Congruential (Mixed)", "Multiplicative Congruential", "Middle-Square Method"),
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("Adjust parameters on the right, then click **Generate** to compute the sequence.")



st.markdown("# Random Number Generation")
st.markdown(
    '<p style="color:#64748b;font-size:1rem;margin-top:-0.5rem;margin-bottom:1.75rem;">'
    "Simulate & analyse pseudo-random sequences  ·  Three classic algorithms"
    "</p>",
    unsafe_allow_html=True,
)


df = pd.DataFrame()

if algorithm == "Linear Congruential (Mixed)":
    st.markdown('<span class="algo-pill">LINEAR CONGRUENTIAL · MIXED</span>', unsafe_allow_html=True)
    st.markdown("### Parameters")
    st.caption("Formula: X₍ₙ₊₁₎ = (a · Xₙ + c) mod m")

    p1, p2, p3 = st.columns([1, 1, 1])
    with p1:
        seed_in = st.number_input("Seed X₀", value=27, min_value=0)
        a_in    = st.number_input("Multiplier a", value=17, min_value=1)
    with p2:
        c_in = st.number_input("Increment c", value=43, min_value=0)
        m_in = st.number_input("Modulus m", value=100, min_value=2)
    with p3:
        st.markdown(
            '<div class="hint-card">'
            "<strong>Example defaults</strong><br>"
            "X₀ = 27 &nbsp;·&nbsp; a = 17<br>"
            "c = 43 &nbsp;·&nbsp; m = 100"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("")
    if st.button("Generate LCG Sequence", use_container_width=False):
        df = generate_lcg(seed_in, a_in, c_in, m_in, num_samples)

elif algorithm == "Multiplicative Congruential":
    st.markdown('<span class="algo-pill">MULTIPLICATIVE CONGRUENTIAL</span>', unsafe_allow_html=True)
    st.markdown("### Parameters")
    st.caption("Formula: X₍ₙ₊₁₎ = (a · Xₙ) mod m  &nbsp;(c = 0)")

    p1, p2, p3 = st.columns([1, 1, 1])
    with p1:
        seed_in = st.number_input("Seed X₀", value=1, min_value=1)
        a_in    = st.number_input("Multiplier a", value=13, min_value=1)
    with p2:
        m_in = st.number_input("Modulus m", value=1000, min_value=2,
                               help="Typically a power of 2, e.g. 2¹⁰ = 1024")
    with p3:
        st.markdown(
            '<div class="hint-card">'
            "<strong>Example defaults</strong><br>"
            "a = 13 &nbsp;·&nbsp; m = 1000<br>"
            "Try X₀ = 1, 2, 3, 4"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("")
    if st.button("Generate MCG Sequence", use_container_width=False):
        df = generate_mcg(seed_in, a_in, m_in, num_samples)

elif algorithm == "Middle-Square Method":
    st.markdown('<span class="algo-pill">MIDDLE-SQUARE METHOD</span>', unsafe_allow_html=True)
    st.markdown("### Parameters")
    st.caption("Square the seed, extract the middle digits, repeat.")

    p1, p2 = st.columns([1, 2])
    with p1:
        seed_in = st.number_input("Seed X₀", value=1234, min_value=1)
    with p2:
        st.markdown(
            '<div class="hint-card">'
            "<strong>How it works</strong><br>"
            "Seed 1234 → Square 1,522,756 → Take middle 4 digits → <strong>5227</strong>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("")
    if st.button("Generate Middle-Square Sequence", use_container_width=False):
        df = generate_middle_square(seed_in, num_samples)



if not df.empty:
    st.markdown("---")

    r = df["Random (Ri)"]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mean",     f"{r.mean():.4f}")
    m2.metric("Std Dev",  f"{r.std():.4f}")
    m3.metric("Min",      f"{r.min():.4f}")
    m4.metric("Max",      f"{r.max():.4f}")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋  Data Table", "📈  Visualisation"])

    with tab1:
        unique_vals = df["Integer (Xi)"].nunique()
        total_vals  = len(df)
        if unique_vals < total_vals:
            st.warning(
                f"⚠️ Cycle detected — only **{unique_vals}** unique integers "
                f"in {total_vals} samples. Period ≈ {unique_vals}."
            )

        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        lc, rc = st.columns(2, gap="large")

        with lc:
            st.markdown("**Sequence Plot**")
            st.caption("Random value Rᵢ across successive indices")
            st.line_chart(df.set_index("Index")["Random (Ri)"], height=280,
                          use_container_width=True, color="#6366f1")

        with rc:
            st.markdown("**Distribution (Histogram)**")
            st.caption("Frequency of values across the [0, 1) interval")
            bins = pd.cut(df["Random (Ri)"], bins=10)
            hist = df.groupby(bins, observed=True)["Random (Ri)"].count()
            hist.index = [str(i) for i in hist.index]
            st.bar_chart(hist, height=280, use_container_width=True, color="#8b5cf6")

else:
    st.markdown(
        '<div style="text-align:center;padding:3rem 1rem;color:#3d4266;">'
        '<div style="font-size:3rem">🎲</div>'
        '<div style="font-size:1rem;font-weight:600;margin-top:0.75rem;color:#64748b;">'
        "Configure parameters and click <strong style='color:#a5b4fc'>Generate</strong> to see results."
        "</div></div>",
        unsafe_allow_html=True,
    )
