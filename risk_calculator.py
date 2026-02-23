import streamlit as st

st.set_page_config(
    page_title="Risk Calculator",
    page_icon="◈",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Mono', monospace; background-color: #0d0f12; color: #e2e4e9; }
.stApp { background: #0d0f12; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }
.stNumberInput input, .stSelectbox select, .stTextInput input {
    background: #161820 !important; border: 1px solid #252837 !important;
    border-radius: 8px !important; color: #e2e4e9 !important;
    font-family: 'DM Mono', monospace !important; font-size: 14px !important;
}
.stNumberInput input:focus { border-color: #00e5a0 !important; box-shadow: 0 0 0 2px rgba(0,229,160,0.12) !important; }
[data-testid="metric-container"] { background: #161820; border: 1px solid #252837; border-radius: 12px; padding: 16px 18px; }
[data-testid="stMetricLabel"] { font-size: 10px !important; letter-spacing: 0.1em; text-transform: uppercase; color: #6b7280 !important; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; font-size: 22px !important; font-weight: 800 !important; }
[data-testid="stMetricDelta"] { font-size: 11px !important; }
hr { border-color: #252837 !important; margin: 20px 0 !important; }
label { font-size: 12px !important; color: #6b7280 !important; letter-spacing: 0.05em; }
.stProgress > div > div { background-color: #00e5a0 !important; }
.stProgress > div { background-color: #252837 !important; border-radius: 99px !important; height: 6px !important; }
.stAlert { background: #161820 !important; border: 1px solid #252837 !important; border-radius: 10px !important; font-size: 12px !important; }
.spec-box { background: #0f111a; border: 1px solid #1e2235; border-radius: 10px; padding: 14px 18px; font-size: 12px; color: #6b7280; margin-top: 4px; line-height: 2.0; }
.spec-box span { color: #e2e4e9; }
.spec-box .acc { color: #00e5a0; font-weight: 500; }
[data-testid="stSidebar"] { background: #0d0f12 !important; border-right: 1px solid #1e2235 !important; }
</style>
""", unsafe_allow_html=True)

# ─── INSTRUMENT DATABASE ────────────────────────────────────────────────────
INSTRUMENTS = {
    "EURUSD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=True,  jpy=False, gold=False, group="Majors"),
    "GBPUSD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=True,  jpy=False, gold=False, group="Majors"),
    "USDJPY": dict(contract=100_000, pip=0.01,   decimals=3, quote_usd=False, jpy=True,  gold=False, group="Majors"),
    "USDCHF": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=False, jpy=False, gold=False, group="Majors"),
    "AUDUSD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=True,  jpy=False, gold=False, group="Majors"),
    "NZDUSD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=True,  jpy=False, gold=False, group="Majors"),
    "USDCAD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=False, jpy=False, gold=False, group="Majors"),
    "GBPJPY": dict(contract=100_000, pip=0.01,   decimals=3, quote_usd=False, jpy=True,  gold=False, group="Crosses"),
    "EURJPY": dict(contract=100_000, pip=0.01,   decimals=3, quote_usd=False, jpy=True,  gold=False, group="Crosses"),
    "EURGBP": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=False, jpy=False, gold=False, group="Crosses"),
    "EURCAD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=False, jpy=False, gold=False, group="Crosses"),
    "GBPAUD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=False, jpy=False, gold=False, group="Crosses"),
    "GBPCAD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=False, jpy=False, gold=False, group="Crosses"),
    "AUDCAD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=False, jpy=False, gold=False, group="Crosses"),
    "AUDNZD": dict(contract=100_000, pip=0.0001, decimals=5, quote_usd=True,  jpy=False, gold=False, group="Crosses"),
    "CADJPY": dict(contract=100_000, pip=0.01,   decimals=3, quote_usd=False, jpy=True,  gold=False, group="Crosses"),
    "CHFJPY": dict(contract=100_000, pip=0.01,   decimals=3, quote_usd=False, jpy=True,  gold=False, group="Crosses"),
    "NZDJPY": dict(contract=100_000, pip=0.01,   decimals=3, quote_usd=False, jpy=True,  gold=False, group="Crosses"),
    "XAUUSD": dict(contract=100,     pip=0.01,   decimals=2, quote_usd=True,  jpy=False, gold=True,  group="Metals"),
    "XAGUSD": dict(contract=5_000,   pip=0.001,  decimals=3, quote_usd=True,  jpy=False, gold=False, group="Metals"),
}

BROKERS = {
    "Exness":      dict(spread={"EURUSD":0.7,"GBPUSD":0.9,"USDJPY":0.7,"GBPJPY":1.5,"XAUUSD":20,"XAGUSD":3,"default":1.2}, commission=0,   raw_comm=0),
    "IC Markets":  dict(spread={"EURUSD":0.1,"GBPUSD":0.2,"USDJPY":0.1,"GBPJPY":0.5,"XAUUSD":15,"XAGUSD":2,"default":0.5}, commission=3.5, raw_comm=3.5),
    "Pepperstone": dict(spread={"EURUSD":0.1,"GBPUSD":0.2,"USDJPY":0.1,"GBPJPY":0.5,"XAUUSD":12,"XAGUSD":2,"default":0.5}, commission=3.5, raw_comm=3.5),
    "FTMO":        dict(spread={"EURUSD":1.0,"GBPUSD":1.2,"USDJPY":1.0,"GBPJPY":2.0,"XAUUSD":25,"XAGUSD":4,"default":1.5}, commission=0,   raw_comm=0),
    "Autre":       dict(spread={"default":1.0}, commission=0, raw_comm=0),
}

def pip_value_usd(symbol, lots, entry_price, quote_rate=1.0):
    spec = INSTRUMENTS[symbol]
    c, p = spec["contract"], spec["pip"]
    if spec["gold"]:
        return lots * c * p       # XAUUSD: 100 oz * 0.01 = $1/lot
    if spec["quote_usd"]:
        return lots * c * p       # USD quote: direct
    if spec["jpy"]:
        return (lots * c * p) / entry_price  # JPY: divide by rate
    return (lots * c * p) / quote_rate       # Cross: divide by quote/USD

def grouped_opts():
    seen = {}
    for sym, s in INSTRUMENTS.items():
        seen.setdefault(s["group"], []).append(sym)
    return [f"{g} — {s}" for g, syms in seen.items() for s in syms]

# ═══════════════════════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("## ◈ Risk Calculator")
st.caption("Paires FX · Or · Calcul pip value par broker")
st.divider()

# ── ROW 1 ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    balance  = st.number_input("Balance ($)", min_value=0.0, value=10_000.0, step=500.0, format="%.2f")
    leverage = st.number_input("Levier (x)", min_value=1, max_value=2000, value=100, step=50)
with c2:
    broker_name  = st.selectbox("Broker", list(BROKERS.keys()))
    account_type = st.selectbox("Type de compte", ["Standard (spread inclus)", "Raw / ECN (+ commission)"])

st.divider()

# ── ROW 2 ────────────────────────────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    sym_sel = st.selectbox("Instrument", grouped_opts(), index=0)
    symbol  = sym_sel.split(" — ")[1]
    spec    = INSTRUMENTS[symbol]
    step_v  = spec["pip"]
    fmt_v   = f"%.{spec['decimals']}f"

    default_entry = 2300.00 if spec["gold"] else (150.000 if spec["jpy"] else 1.10000)
    entry     = st.number_input("Prix d'entrée", value=default_entry, step=step_v, format=fmt_v)
    stop_loss = st.number_input("Stop Loss",      value=entry - spec["pip"]*50, step=step_v, format=fmt_v)

with c4:
    risk_mode = st.selectbox("Risque exprimé en", ["Pourcentage (%)", "Montant fixe ($)"])
    if risk_mode == "Pourcentage (%)":
        risk_pct = st.number_input("Risque (%)", min_value=0.1, max_value=20.0, value=1.0, step=0.1, format="%.1f")
        risk_amt = balance * risk_pct / 100
    else:
        risk_amt = st.number_input("Risque ($)", min_value=1.0, value=100.0, step=10.0, format="%.2f")
        risk_pct = (risk_amt / balance * 100) if balance > 0 else 0

    take_profit = st.number_input("Take Profit", value=entry + spec["pip"]*100, step=step_v, format=fmt_v)

    # Cross pairs need quote/USD rate
    quote_rate = 1.0
    if not spec["quote_usd"] and not spec["jpy"] and not spec["gold"]:
        qc = symbol[-3:]
        defaults = {"GBP":1.27, "EUR":1.08, "AUD":0.65, "NZD":0.61, "CAD":0.74, "CHF":1.12}
        quote_rate = st.number_input(
            f"Taux {qc}/USD (pour pip value)",
            min_value=0.001, value=defaults.get(qc, 1.0), step=0.001, format="%.4f"
        )

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# CALCULS
# ═══════════════════════════════════════════════════════════════════════════════
sl_dist = abs(entry - stop_loss)
tp_dist = abs(take_profit - entry)
sl_pips = sl_dist / spec["pip"]
tp_pips = tp_dist / spec["pip"]

pv1 = pip_value_usd(symbol, 1.0, entry, quote_rate)   # pip value for 1 lot
lots = risk_amt / (sl_pips * pv1) if sl_pips > 0 and pv1 > 0 else 0
pv   = pip_value_usd(symbol, lots, entry, quote_rate)  # pip value for position

max_loss   = lots * sl_pips * pv1
max_profit = lots * tp_pips * pv1 if tp_pips > 0 else 0
rr         = tp_pips / sl_pips if sl_pips > 0 else 0
min_wr     = 1 / (1 + rr) * 100 if rr > 0 else 50

notional = lots * spec["contract"] * entry
margin   = notional / leverage if leverage > 0 else 0

broker      = BROKERS[broker_name]
spread_pip  = broker["spread"].get(symbol, broker["spread"]["default"])
spread_cost = spread_pip * pv1 * lots
raw_comm    = broker["raw_comm"] if "ECN" in account_type or "Raw" in account_type else 0
comm_cost   = (raw_comm / 10_000) * notional * 2  # round-trip %
total_cost  = spread_cost + comm_cost

# ═══════════════════════════════════════════════════════════════════════════════
# AFFICHAGE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("#### Résultats")

r1,r2,r3,r4 = st.columns(4)
r1.metric("Risque",             f"${risk_amt:,.2f}",      f"{risk_pct:.2f}%")
r2.metric("Position",           f"{lots:.2f} lot",        f"{lots*spec['contract']:,.0f} unités")
r3.metric("Pip value (1 lot)",  f"${pv1:.2f}",            "par pip · 1 lot")
r4.metric("Pip value (pos.)",   f"${pv:.3f}",             "par pip · ta pos")

st.markdown("<br>", unsafe_allow_html=True)
r5,r6,r7,r8 = st.columns(4)
r5.metric("SL distance",      f"{sl_pips:.1f} pips")
r6.metric("TP distance",      f"{tp_pips:.1f} pips")
r7.metric("Profit potentiel", f"+${max_profit:,.2f}",    f"+{max_profit/balance*100:.2f}%")
r8.metric("Ratio R:R",        f"1 : {rr:.2f}")

st.markdown("<br>", unsafe_allow_html=True)
r9,r10,r11,r12 = st.columns(4)
r9.metric( "Marge requise",  f"${margin:,.2f}",       f"{margin/balance*100:.1f}% compte")
r10.metric("Win rate min.",  f"{min_wr:.0f}%",        "pour breakeven")
r11.metric("Coût spread",    f"${spread_cost:.2f}",   f"{spread_pip} pips")
r12.metric("Coût total",     f"${total_cost:.2f}",    "aller-retour")

st.divider()

# ── RR BAR ───────────────────────────────────────────────────────────────────
icon = "🟢" if rr >= 2 else "🟡" if rr >= 1 else "🔴"
st.markdown(f"**Ratio R:R**  {icon}  `1 : {rr:.2f}`")
st.progress(min(int((rr / 4) * 100), 100))

# ── SPEC BOX ─────────────────────────────────────────────────────────────────
comm_str = f"${broker['raw_comm']}/lot/side" if broker["raw_comm"] > 0 else "incluse dans spread"
st.markdown(f"""
<div class="spec-box">
  <b style="color:#e2e4e9">Spécifications — {symbol} · {broker_name}</b><br>
  Contract size &nbsp;→ <span>{spec['contract']:,} unités/lot</span> &emsp;
  Pip size &nbsp;→ <span>{spec['pip']}</span> &emsp;
  Pip value (1 std lot) &nbsp;→ <span class="acc">${pv1:.2f}</span><br>
  Spread typique ({broker_name}) &nbsp;→ <span>{spread_pip} pips</span> &emsp;
  Commission &nbsp;→ <span>{comm_str}</span> &emsp;
  Notional &nbsp;→ <span>${notional:,.0f}</span>
</div>
""", unsafe_allow_html=True)

# ── TIP ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if risk_pct > 3:
    st.warning(f"⚠️ {risk_pct:.1f}% de risque par trade est élevé. La plupart des prop firms sanctionnent à partir de 5–10% de drawdown.")
elif rr < 1:
    st.error("R:R < 1 : vous perdez plus que vous ne gagnez. Difficile d'être profitable sur le long terme.")
elif spec["gold"] and sl_pips < 50:
    st.warning("Stop Loss très serré sur Gold. L'or bouge souvent 100–300 pips/jour. Risque de stop out élevé.")
elif rr >= 2 and risk_pct <= 2:
    st.success(f"Setup solide : R:R ≥ 2 + risque ≤ 2%. Rentable si win rate > {min_wr:.0f}%.")
else:
    st.info(f"Avec un R:R de 1:{rr:.1f}, un win rate de {min_wr:.0f}% suffit pour atteindre le breakeven.")

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Calculs basés sur specs MT4/MT5 standards · Pip values approximatives · Pas de conseil financier.")
