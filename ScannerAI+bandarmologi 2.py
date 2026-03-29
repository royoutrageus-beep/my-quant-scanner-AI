import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# --- 🔐 CONFIG AREA ---
st.set_page_config(layout="wide", page_title="QUANT PRO - CLOUD EDITION")

# --- 📂 FULL 11 SECTOR DATABASE ---
SECTOR_DATA = {
    "TEKNOLOGI": ["GOTO.JK", "BUKA.JK", "EMTK.JK", "INET.JK", "MLPT.JK", "DCII.JK", "ATIC.JK", "GLVA.JK", "MTDL.JK", "WIFI.JK", "CHIP.JK", "ELIT.JK"],
    "KEUANGAN": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "ARTO.JK", "BRIS.JK", "BBTN.JK", "BDMN.JK", "PNBN.JK", "BJBR.JK", "BNGA.JK", "BBYB.JK"],
    "ENERGI": ["ADRO.JK", "PTBA.JK", "ITMG.JK", "HRUM.JK", "INDY.JK", "MEDC.JK", "ENRG.JK", "PGAS.JK", "AKRA.JK", "DOID.JK", "BUMI.JK", "RMKE.JK", "ADMR.JK"],
    "KONSUMEN PRIMER": ["UNVR.JK", "ICBP.JK", "INDF.JK", "AMRT.JK", "MIDI.JK", "CPIN.JK", "JPFA.JK", "MAIN.JK", "MYOR.JK", "GGRM.JK", "HMSP.JK", "CLEO.JK"],
    "KONSUMEN NON-PRIMER": ["MAPI.JK", "ACES.JK", "ERAA.JK", "ASII.JK", "SMSM.JK", "IMAS.JK", "GJTL.JK", "MNCN.JK", "SCMA.JK", "RALS.JK", "LPPF.JK", "FILM.JK"],
    "KESEHATAN": ["KLBF.JK", "MIKA.JK", "HEAL.JK", "SILO.JK", "PRDA.JK", "SAME.JK", "KAEF.JK", "SIDO.JK", "IRRA.JK", "DGNS.JK"],
    "INFRASTRUKTUR": ["TLKM.JK", "ISAT.JK", "EXCL.JK", "JSMR.JK", "BREN.JK", "POWR.JK", "ADHI.JK", "PTPP.JK", "WIKA.JK", "TOWR.JK", "TBIG.JK", "PGEO.JK"],
    "PERINDUSTRIAN": ["UNTR.JK", "ARNA.JK", "ASGR.JK", "IMPC.JK", "HEXA.JK", "GMFI.JK", "ABMM.JK", "WOOD.JK", "VOKS.JK", "KBLI.JK"],
    "BAHAN BAKU": ["TPIA.JK", "BRPT.JK", "ANTM.JK", "INCO.JK", "TINS.JK", "MDKA.JK", "SMGR.JK", "INTP.JK", "NCKL.JK", "ESSA.JK", "SRTG.JK", "MBMA.JK"],
    "PROPERTI": ["BSDE.JK", "PWON.JK", "SMRA.JK", "CTRA.JK", "ASRI.JK", "DILD.JK", "LPCK.JK", "LPKR.JK", "DMAS.JK", "PANI.JK", "MKPI.JK"],
    "TRANSPORTASI": ["BIRD.JK", "ASSA.JK", "SMDR.JK", "TMAS.JK", "GIAA.JK", "NELY.JK", "PSSI.JK", "ELPI.JK", "HUMI.JK"]
}

# --- 🎨 CSS (OPTIMIZED FOR CLOUD) ---
st.markdown("""
<style>
    .stTable { font-size: 11px !important; }
    table { width: 100%; border-collapse: collapse; text-transform: uppercase; border: 1px solid #374151; }
    th { background-color: #1e293b; color: #38bdf8; padding: 12px 5px !important; border: 1px solid #475569; 
         text-align: center !important; font-size: 12px !important; font-weight: 900 !important; letter-spacing: 1px; }
    td { padding: 4px 6px !important; border: 1px solid #1f2937; height: 32px !important; text-align: left; }
    td:nth-child(3), td:nth-child(4), td:nth-child(5) { text-align: center; }
    .status-box { font-weight: 800; padding: 3px 6px; border-radius: 4px; font-size: 10px; }
    .akum-besar { background-color: #064e3b; color: #4ade80; border: 1px solid #22c55e; }
    .oversold-blink { background-color: #1e3a8a; color: #60a5fa; border: 1px solid #3b82f6; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    .hint-box { font-weight: 900; padding: 3px 6px; border-radius: 4px; font-size: 10px; }
    .hint-entry { background-color: #22c55e; color: black; border: 1px solid white; }
    .strength-val { color: #22d3ee; font-weight: bold; font-size: 14px; text-shadow: 0 0 5px rgba(34,211,238,0.5); }
    .stButton>button { width: 100%; background-color: #22c55e; color: white; font-weight: bold; height: 3em; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300) # Cache data selama 5 menit
def get_data(ticker_list):
    return yf.download(ticker_list, period="60d", interval="1d", group_by='ticker', progress=False)

def calculate_atr(df, period=14):
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# --- ⚙️ SIDEBAR ---
st.sidebar.header("🕹️ COMMAND CENTER")
sel_cat = st.sidebar.multiselect("📂 SECTOR CATEGORY", ["🔥 SCAN ALL"] + list(SECTOR_DATA.keys()), default=None)
mode = st.sidebar.radio("🎯 MAIN STRATEGY", ["STANDARD (ACCUM)", "BOTTOM RADAR (OVERSOLD)"])

st.sidebar.markdown("---")
f_ma = st.sidebar.number_input("⚡ FAST MA", 1, 50, 5)
s_ma = st.sidebar.number_input("🐢 SLOW MA", 1, 200, 20)
m_rvol = st.sidebar.slider("🔥 MIN RVOL", 1.0, 5.0, 2.0, 0.1)
m_cmf = st.sidebar.slider("💰 MIN CMF", 0.0, 0.5, 0.15, 0.05)

btn = st.sidebar.button("🚀 EXECUTE RADAR")

st.title("🏹 QUANT PRO - CLOUD v3.4")

if btn and sel_cat:
    stocks = []
    if "🔥 SCAN ALL" in sel_cat:
        stocks = [t for s in SECTOR_DATA.values() for t in s]
    else:
        for c in sel_cat: stocks.extend(SECTOR_DATA[c])
    stocks = list(set(stocks))

    try:
        with st.spinner(f"FETCHING {len(stocks)} TICKERS FROM CLOUD..."):
            all_d = get_data(stocks)
        
        res = []
        for s in stocks:
            try:
                df = all_d[s].copy().dropna()
                if len(df) < 30: continue 
                p = int(df['Close'].iloc[-1])
                chg = round(((p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100, 2)
                mf, ms = df['Close'].rolling(int(f_ma)).mean().iloc[-1], df['Close'].rolling(int(s_ma)).mean().iloc[-1]
                zsc = round((df['Close'].iloc[-1] - df['Close'].rolling(20).mean().iloc[-1]) / df['Close'].rolling(20).std().iloc[-1], 2)
                atr = calculate_atr(df).iloc[-1]
                liq = round((atr / (df['Volume'].rolling(20).mean().iloc[-1] / 1000000)), 2)
                cmf = round((((df['Close']-df['Low']) - (df['High']-df['Close'])) / (df['High']-df['Low']).replace(0,0.001) * df['Volume']).rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1], 2)
                rv = round(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1], 2)

                stts, c_css, hnt, h_css, rnk = "NORMAL", "", "WATCH", "", 0
                if mode == "STANDARD (ACCUM)":
                    if chg > 0.5 and cmf >= m_cmf and rv >= m_rvol:
                        stts, c_css, rnk = "BIG ACCUM 🔥", "akum-besar", 3000
                        hnt, h_css = ("🚀 GAS ENTRY" if p > mf and p > ms else "⌛ WAIT BRK"), ("hint-entry" if p > mf else "")
                else:
                    if zsc <= -2.0:
                        stts, c_css, rnk = "SALAH HARGA 💎", "oversold-blink", 2500
                        hnt, h_css = "🎣 SPEC BUY", "hint-entry"

                res.append({
                    "TICKER": f"**{s.replace('.JK','')}**",
                    "ACTION": f"<span class='hint-box {h_css}'>{hnt}</span>" if hnt else "WATCH",
                    "STR": f"<span class='strength-val'>{int(rnk/10) if rnk > 0 else 0}</span>",
                    "Z-SCR": f"{zsc}",
                    "LIQ": "SAFE ✅" if liq < 5 else "THIN ⚠️",
                    "PRICE (ROC)": f"{p:,} ({chg}%)",
                    "TARGET": f"TP:{int(p+(atr*2.5))} | SL:{int(p-(atr*1.5))}",
                    "FLOW": f"<span class='status-box {c_css}'>{stts}</span>",
                    "_rnk": rnk
                })
            except: continue

        if res:
            df_f = pd.DataFrame(res).sort_values(by="_rnk", ascending=False).drop(columns=["_rnk"])
            st.markdown(df_f.to_html(escape=False, index=False), unsafe_allow_html=True)
    except Exception as e: st.error(f"ERR: {e}")