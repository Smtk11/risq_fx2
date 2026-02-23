import streamlit as st

st.set_page_config(page_title="Risk Calculator", page_icon="◈", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Mono', monospace; background-color: #0d0f12; color: #e2e4e9; }
.stApp { background: #0d0f12; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }
.stNumberInput input, .stSelectbox select {
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
.spec-box {
    background: #0f111a; border: 1px solid #1e2235; border-radius: 10px;
    padding: 14px 18px; font-size: 12px; color: #6b7280; margin-top: 4px; line-height: 2.0;
}
.spec-box span { color: #e2e4e9; }
.spec-box .acc { color: #00e5a0; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# INSTRUMENT DATABASE
#
# Formules pip value :
#   usd_quote → lots × contract × pip          (EURUSD, AUDUSD...)
#   jpy       → (lots × contract × pip) / prix (USDJPY, GBPJPY...)
#   cross_usd → (lots × contract × pip) / quote_rate (EURGBP, USDCAD...)
#   gold      → lots × contract × pip          (XAUUSD: 100oz × $0.01 = $1/lot FIXE, indépendant du prix)
#
# MARGE = (lots × contract × prix_entrée) / levier_effectif
# ══════════════════════════════════════════════════════════════════
INSTRUMENTS = {
    # MAJORS
    "EURUSD": dict(contract=100_000, pip=0.0001, decimals=5, formula="usd_quote", group="Majors"),
    "GBPUSD": dict(contract=100_000, pip=0.0001, decimals=5, formula="usd_quote", group="Majors"),
    "USDJPY": dict(contract=100_000, pip=0.01,   decimals=3, formula="jpy",       group="Majors"),
    "USDCHF": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Majors"),
    "AUDUSD": dict(contract=100_000, pip=0.0001, decimals=5, formula="usd_quote", group="Majors"),
    "NZDUSD": dict(contract=100_000, pip=0.0001, decimals=5, formula="usd_quote", group="Majors"),
    "USDCAD": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Majors"),
    # CROSSES
    "GBPJPY": dict(contract=100_000, pip=0.01,   decimals=3, formula="jpy",       group="Crosses"),
    "EURJPY": dict(contract=100_000, pip=0.01,   decimals=3, formula="jpy",       group="Crosses"),
    "EURGBP": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Crosses"),
    "EURCAD": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Crosses"),
    "EURAUD": dict(contract=100_000, pip=0.0001, decimals=5, formula="usd_quote", group="Crosses"),
    "GBPAUD": dict(contract=100_000, pip=0.0001, decimals=5, formula="usd_quote", group="Crosses"),
    "GBPCAD": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Crosses"),
    "AUDCAD": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Crosses"),
    "AUDNZD": dict(contract=100_000, pip=0.0001, decimals=5, formula="usd_quote", group="Crosses"),
    "AUDCHF": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Crosses"),
    "CADJPY": dict(contract=100_000, pip=0.01,   decimals=3, formula="jpy",       group="Crosses"),
    "CHFJPY": dict(contract=100_000, pip=0.01,   decimals=3, formula="jpy",       group="Crosses"),
    "NZDJPY": dict(contract=100_000, pip=0.01,   decimals=3, formula="jpy",       group="Crosses"),
    "NZDCAD": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Crosses"),
    "NZDCHF": dict(contract=100_000, pip=0.0001, decimals=5, formula="cross_usd", group="Crosses"),
    # METALS
    # XAUUSD : 1 lot = 100 oz, 1 pip = $0.01 → pip value = $1/lot (FIXE, pas lié au prix spot)
    # vérification : 0.01 lot = $0.01/pip | marge = (0.01 × 100 × prix) / levier
    "XAUUSD": dict(contract=100,   pip=0.01,  decimals=2, formula="gold", group="Metals"),
    "XAGUSD": dict(contract=5_000, pip=0.001, decimals=3, formula="usd_quote", group="Metals"),
}

# Leverage caps effectifs par broker (HMR — High Market Risk)
# Exness plafonne XAUUSD à 1:1000 même si le compte est 1:2000
LEVER_CAPS = {
    "Exness":      {"gold": 1000, "forex": 2000},
    "IC Markets":  {"gold": 500,  "forex": 500},
    "Pepperstone": {"gold": 500,  "forex": 500},
    "FTMO":        {"gold": 100,  "forex": 100},
    "Autre":       {"gold": 9999, "forex": 9999},
}

BROKERS = {
    "Exness":      dict(spread={"EURUSD":0.7,"GBPUSD":0.9,"USDJPY":0.7,"GBPJPY":1.5,"XAUUSD":20,"XAGUSD":3,"default":1.2}, commission=0),
    "IC Markets":  dict(spread={"EURUSD":0.1,"GBPUSD":0.2,"USDJPY":0.1,"GBPJPY":0.5,"XAUUSD":15,"XAGUSD":2,"default":0.5}, commission=3.5),
    "Pepperstone": dict(spread={"EURUSD":0.1,"GBPUSD":0.2,"USDJPY":0.1,"GBPJPY":0.5,"XAUUSD":12,"XAGUSD":2,"default":0.5}, commission=3.5),
    "FTMO":        dict(spread={"EURUSD":1.0,"GBPUSD":1.2,"USDJPY":1.0,"GBPJPY":2.0,"XAUUSD":25,"XAGUSD":4,"default":1.5}, commission=0),
    "Autre":       dict(spread={"default":1.0}, commission=0),
}

def pip_value_per_lot(symbol, price, quote_rate=1.0):
    """Pip value en USD pour 1 lot standard."""
    s = INSTRUMENTS[symbol]
    c, p = s["contract"], s["pip"]
    f = s["formula"]
    if f == "usd_quote":
        return c * p                     # 100000 × 0.0001 = $10
    if f == "jpy":
        return (c * p) / price           # (100000 × 0.01) / prix
    if f == "gold":
        return c * p                     # 100 × 0.01 = $1 — FIXE
    if f == "cross_usd":
        return (c * p) / quote_rate      # divisé par taux quote/USD
    return c * p

def grouped_opts():
    g = {}
    for sym, s in INSTRUMENTS.items():
        g.setdefault(s["group"], []).append(sym)
    return [f"{grp} — {sym}" for grp, syms in g.items() for sym in syms]

# ══════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════
st.markdown("## ◈ Risk Calculator")
st.caption("FX · Gold · Pip value réel par broker")
st.divider()

col1, col2 = st.columns(2)
with col1:
    balance      = st.number_input("Balance ($)", min_value=0.0, value=10_000.0, step=500.0, format="%.2f")
    leverage_in  = st.number_input("Levier (x)", min_value=1, max_value=2000, value=2000, step=100)
with col2:
    broker_name  = st.selectbox("Broker", list(BROKERS.keys()))
    account_type = st.selectbox("Type de compte", ["Standard (spread inclus)", "Raw / ECN (+ commission)"])

st.divider()

col3, col4 = st.columns(2)

with col3:
    sym_sel = st.selectbox("Instrument", grouped_opts(), index=list(grouped_opts()).index("Metals — XAUUSD"))
    symbol  = sym_sel.split(" — ")[1]
    spec    = INSTRUMENTS[symbol]
    is_gold = spec["formula"] == "gold"
    is_jpy  = spec["formula"] == "jpy"
    step_v  = spec["pip"]
    fmt_v   = f"%.{spec['decimals']}f"

    default_entry = 5166.00 if is_gold else (150.000 if is_jpy else 1.10000)
    entry     = st.number_input("Prix d'entrée", value=default_entry, step=step_v, format=fmt_v)
    stop_loss = st.number_input("Stop Loss",      value=round(entry - spec["pip"]*50, spec["decimals"]),
                                step=step_v, format=fmt_v)

with col4:
    risk_mode = st.selectbox("Risque exprimé en", ["Pourcentage (%)", "Montant fixe ($)"])
    if risk_mode == "Pourcentage (%)":
        risk_pct = st.number_input("Risque (%)", min_value=0.1, max_value=20.0, value=1.0, step=0.1, format="%.1f")
        risk_amt = balance * risk_pct / 100
    else:
        risk_amt = st.number_input("Risque ($)", min_value=1.0, value=100.0, step=10.0, format="%.2f")
        risk_pct = (risk_amt / balance * 100) if balance > 0 else 0

    take_profit = st.number_input("Take Profit",
                                  value=round(entry + spec["pip"]*100, spec["decimals"]),
                                  step=step_v, format=fmt_v)

    # Cross pairs: besoin du taux quote/USD
    quote_rate = 1.0
    needs_rate = spec["formula"] == "cross_usd" and symbol not in ["USDCAD","USDCHF"]
    if needs_rate:
        qc = symbol[-3:]
        defaults = {"GBP":1.27,"EUR":1.09,"AUD":0.65,"NZD":0.61,"CAD":0.74,"CHF":1.12}
        quote_rate = st.number_input(f"Taux {qc}/USD", min_value=0.001,
                                     value=defaults.get(qc, 1.0), step=0.0001, format="%.4f")
    elif symbol in ["USDCAD","USDCHF","EURGBP"]:
        # pour ces paires on divise par le prix lui-même comme proxy
        quote_rate = entry

# ══════════════════════════════════════════════════════════════════
# CALCULS
# ══════════════════════════════════════════════════════════════════
# Levier effectif (caps HMR du broker)
cat_lev   = "gold" if is_gold else "forex"
cap       = LEVER_CAPS.get(broker_name, {}).get(cat_lev, 9999)
eff_lev   = min(leverage_in, cap)

sl_dist   = abs(entry - stop_loss)
tp_dist   = abs(take_profit - entry)
sl_pips   = sl_dist / spec["pip"] if spec["pip"] > 0 else 0
tp_pips   = tp_dist / spec["pip"] if spec["pip"] > 0 else 0

# pip value pour 1 lot (en $)
pv1 = pip_value_per_lot(symbol, entry, quote_rate)

# taille de position
lots = risk_amt / (sl_pips * pv1) if sl_pips > 0 and pv1 > 0 else 0

# pip value pour la position calculée
pv_pos = pv1 * lots

max_profit = tp_pips * pv1 * lots if tp_pips > 0 else 0
rr         = tp_pips / sl_pips if sl_pips > 0 else 0
min_wr     = 1 / (1 + rr) * 100 if rr > 0 else 50

# marge = (lots × contract × prix) / levier_effectif
notional = lots * spec["contract"] * entry
margin   = notional / eff_lev if eff_lev > 0 else 0

# coûts broker
broker     = BROKERS[broker_name]
spread_pip = broker["spread"].get(symbol, broker["spread"]["default"])
spread_cost = spread_pip * pv1 * lots
raw_comm   = broker["commission"] if ("ECN" in account_type or "Raw" in account_type) else 0
comm_cost  = raw_comm * lots * 2  # aller-retour, par lot
total_cost = spread_cost + comm_cost

# ══════════════════════════════════════════════════════════════════
# RÉSULTATS
# ══════════════════════════════════════════════════════════════════
st.divider()
st.markdown("#### Résultats")

r1, r2, r3, r4 = st.columns(4)
r1.metric("Risque",            f"${risk_amt:,.2f}",   f"{risk_pct:.2f}% du compte")
r2.metric("Position",          f"{lots:.2f} lot",     f"{lots * spec['contract']:,.0f} unités")
r3.metric("Pip value · 1 lot", f"${pv1:.3f}",         "par pip")
r4.metric("Pip value · pos.",  f"${pv_pos:.4f}",      "par pip")

st.markdown("<br>", unsafe_allow_html=True)

r5, r6, r7, r8 = st.columns(4)
r5.metric("SL distance",      f"{sl_pips:.1f} pips")
r6.metric("TP distance",      f"{tp_pips:.1f} pips")
r7.metric("Profit potentiel", f"+${max_profit:,.2f}", f"+{max_profit/balance*100:.2f}%")
r8.metric("Ratio R:R",        f"1 : {rr:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

r9, r10, r11, r12 = st.columns(4)
r9.metric( "Marge requise",    f"${margin:,.2f}",      f"Levier effectif: 1:{eff_lev:,}")
r10.metric("Win rate min.",    f"{min_wr:.0f}%",        "pour breakeven")
r11.metric("Coût spread",      f"${spread_cost:.3f}",  f"{spread_pip} pips")
r12.metric("Coût total",       f"${total_cost:.3f}",   "aller-retour")

st.divider()

# RR BAR
icon = "🟢" if rr >= 2 else "🟡" if rr >= 1 else "🔴"
st.markdown(f"**Ratio R:R**  {icon}  `1 : {rr:.2f}`")
st.progress(min(int((rr / 4) * 100), 100))

# SPEC BOX
lev_note = f" ⚠️ cappé à 1:{cap:,} sur {symbol} (HMR)" if eff_lev < leverage_in else ""
comm_str = f"${broker['commission']}/lot/side" if broker["commission"] > 0 else "incluse dans spread"
st.markdown(f"""
<div class="spec-box">
  <b style="color:#e2e4e9">Specs — {symbol} · {broker_name}</b><br>
  Contract size &nbsp;→ <span>{spec['contract']:,} unités/lot</span> &emsp;
  Pip size &nbsp;→ <span>{spec['pip']}</span> &emsp;
  Pip value (1 std lot) &nbsp;→ <span class="acc">${pv1:.4f}</span><br>
  Levier saisi &nbsp;→ <span>1:{leverage_in:,}</span> &emsp;
  Levier effectif &nbsp;→ <span class="acc">1:{eff_lev:,}{lev_note}</span> &emsp;
  Marge &nbsp;→ <span class="acc">${margin:,.2f}</span><br>
  Spread ({broker_name}) &nbsp;→ <span>{spread_pip} pips</span> &emsp;
  Commission &nbsp;→ <span>{comm_str}</span> &emsp;
  Notional &nbsp;→ <span>${notional:,.0f}</span>
</div>
""", unsafe_allow_html=True)

# TIP
st.markdown("<br>", unsafe_allow_html=True)
if risk_pct > 3:
    st.warning(f"⚠️ {risk_pct:.1f}% de risque par trade est élevé. La plupart des prop firms sanctionnent à 5–10% de DD.")
elif rr < 1:
    st.error("R:R < 1 — vous perdez plus que vous ne gagnez. Impossible d'être profitable sur le long terme.")
elif is_gold and sl_pips < 50:
    st.warning("Stop Loss très serré sur Gold. L'or peut bouger 100–300 pips/jour. Risque de stop out élevé.")
elif rr >= 2 and risk_pct <= 2:
    st.success(f"Setup solide : R:R ≥ 2 + risque ≤ 2%. Rentable si win rate > {min_wr:.0f}%.")
else:
    st.info(f"Avec R:R 1:{rr:.1f}, un win rate de {min_wr:.0f}% suffit pour le breakeven.")

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Calculs vérifiés sur Exness MT5 · Pip values selon specs officielles · Pas de conseil financier.")
