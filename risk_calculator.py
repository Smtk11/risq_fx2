import streamlit as st

st.set_page_config(
    page_title="Risk Calculator",
    page_icon="◈",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0d0f12;
    color: #e2e4e9;
}

.stApp { background: #0d0f12; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* Inputs */
.stNumberInput input, .stSelectbox select {
    background: #161820 !important;
    border: 1px solid #252837 !important;
    border-radius: 8px !important;
    color: #e2e4e9 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 14px !important;
}
.stNumberInput input:focus {
    border-color: #00e5a0 !important;
    box-shadow: 0 0 0 2px rgba(0,229,160,0.15) !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #161820;
    border: 1px solid #252837;
    border-radius: 12px;
    padding: 18px 20px;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 10px !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b7280 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 24px !important;
    font-weight: 800 !important;
}

/* Divider */
hr { border-color: #252837 !important; margin: 24px 0 !important; }

/* Labels */
label { font-size: 12px !important; color: #6b7280 !important; letter-spacing: 0.05em; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0f12 !important;
    border-right: 1px solid #252837 !important;
}

/* Progress bar */
.stProgress > div > div { background-color: #00e5a0 !important; }
.stProgress > div { background-color: #252837 !important; border-radius: 99px !important; }

/* Info/warning boxes */
.stAlert {
    background: #161820 !important;
    border: 1px solid #252837 !important;
    border-radius: 10px !important;
    font-size: 12px !important;
}

/* Columns gap */
[data-testid="column"] { padding: 0 8px; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("## ◈ Risk Calculator")
st.caption("Gérez votre risque, protégez votre capital")
st.divider()

# ── INPUTS ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    balance = st.number_input("Balance du compte ($)", min_value=0.0, value=10000.0, step=500.0, format="%.2f")
    entry   = st.number_input("Prix d'entrée", value=1.10000, step=0.00001, format="%.5f")
    stop_loss = st.number_input("Stop Loss", value=1.09500, step=0.00001, format="%.5f")

with col2:
    risk_input_mode = st.selectbox("Risque exprimé en", ["Pourcentage (%)", "Montant fixe ($)"])
    
    if risk_input_mode == "Pourcentage (%)":
        risk_pct = st.number_input("Risque (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1, format="%.1f")
        risk_amt = balance * risk_pct / 100
    else:
        risk_amt = st.number_input("Risque ($)", min_value=1.0, value=100.0, step=10.0, format="%.2f")
        risk_pct = (risk_amt / balance * 100) if balance > 0 else 0

    take_profit = st.number_input("Take Profit", value=1.11000, step=0.00001, format="%.5f")
    leverage    = st.number_input("Levier (x)", min_value=1, max_value=500, value=100, step=10)

st.divider()

# ── CALCULS ─────────────────────────────────────────────────────────────────
sl_dist = abs(entry - stop_loss)
tp_dist = abs(take_profit - entry)
sl_pips = sl_dist * 10000
tp_pips = tp_dist * 10000

lots       = risk_amt / (sl_pips * 10) if sl_pips > 0 else 0
pip_value  = lots * 10
max_loss   = risk_amt
max_profit = (tp_dist / sl_dist * risk_amt) if sl_dist > 0 else 0
rr         = tp_dist / sl_dist if sl_dist > 0 else 0
min_wr     = 1 / (1 + rr) * 100 if rr > 0 else 50
margin     = lots * 100000 * entry / leverage if leverage > 0 else 0

# ── RÉSULTATS ───────────────────────────────────────────────────────────────
st.markdown("#### Résultats")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Risque", f"${risk_amt:,.2f}", f"{risk_pct:.2f}%")
c2.metric("Taille position", f"{lots:.2f} lot", f"{lots*100000:,.0f} unités")
c3.metric("Profit potentiel", f"+${max_profit:,.2f}", f"+{max_profit/balance*100:.2f}%")
c4.metric("Ratio R:R", f"1 : {rr:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)

c5.metric("Stop Loss", f"{sl_pips:.1f} pips")
c6.metric("Take Profit", f"{tp_pips:.1f} pips")
c7.metric("Marge requise", f"${margin:,.2f}")
c8.metric("Win rate min.", f"{min_wr:.0f}%")

st.divider()

# ── RR VISUAL ───────────────────────────────────────────────────────────────
rr_color = "🟢" if rr >= 2 else "🟡" if rr >= 1 else "🔴"
rr_pct   = min(int((rr / 4) * 100), 100)

st.markdown(f"**Ratio R:R**  {rr_color}  `1 : {rr:.2f}`")
st.progress(rr_pct)

# ── TIP ─────────────────────────────────────────────────────────────────────
if risk_pct > 3:
    st.warning(f"⚠️ Risquer {risk_pct:.1f}% par trade est élevé. Quelques pertes consécutives peuvent fortement impacter votre compte.", icon=None)
elif rr < 1:
    st.error("Ratio R:R inférieur à 1. Vous perdez plus que vous ne gagnez — difficile d'être rentable même avec un bon win rate.", icon=None)
elif rr >= 2 and risk_pct <= 2:
    st.success(f"Configuration solide. R:R ≥ 2 + risque ≤ 2% = gestion saine du capital.", icon=None)
else:
    st.info(f"Avec ce R:R, un win rate de {min_wr:.0f}% suffit pour atteindre le breakeven.", icon=None)

# ── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Outil pédagogique uniquement — Pas de conseil financier.")
