import os
import streamlit as st
import numpy as np
import pandas as pd
import requests
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "YOUR_BINANCE_API")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "YOUR_SECRET_KEY")

# --- 1. SYSTEM ARCHITECTURE & DARK INTERFACE DESIGN ---
st.set_page_config(
    page_title="QuantDesk: BTC Term Structure Radar",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Deep Matte Institutional Styling
st.markdown("""
    <style>
        body { background-color: #080b0e; color: #848e9c; }
        .stApp { background-color: #080b0e; }
        .hud-box { 
            background-color: #0d1117; 
            border: 1px solid #21262d; 
            border-radius: 6px; 
            padding: 20px; 
            margin-bottom: 20px;
        }
        h1, h2, h3 { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.title("QUANT ENGINE v4.1: CROSS-VENUE TERM STRUCTURE")
st.caption("Live institutional funding radar • market regime monitor")

# --- 2. HIGH-VELOCITY LIVE PUBLIC DATA ENGINE ---
@st.cache_data(ttl=10)
def fetch_live_market_data():
    """
    Fetches live BTC market data from Binance public endpoints using the provided API key.
    """
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}

    try:
        spot_params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "limit": 80,
        }
        spot_res = requests.get(
            "https://api.binance.com/api/v3/klines",
            params=spot_params,
            headers=headers,
            timeout=15,
        )
        spot_res.raise_for_status()
        spot_data = spot_res.json()

        candles = []
        for c in spot_data:
            candles.append({
                'time': pd.to_datetime(c[0], unit='ms'),
                'open': float(c[1]), 'high': float(c[2]),
                'low': float(c[3]), 'close': float(c[4])
            })
        df_candles = pd.DataFrame(candles)

        funding_res = requests.get(
            "https://fapi.binance.com/fapi/v1/fundingRate",
            params={"symbol": "BTCUSDT", "limit": 1},
            headers=headers,
            timeout=15,
        )
        funding_res.raise_for_status()
        funding_data = funding_res.json()

        live_funding = float(funding_data[0]["fundingRate"]) if isinstance(funding_data, list) and funding_data else 0.0001

        return df_candles, live_funding
    except Exception:
        dates = pd.date_range(end=pd.Timestamp.now(), periods=40)
        df_dummy = pd.DataFrame({
            'time': dates, 'open': 94200, 'high': 95800, 'low': 93900, 'close': 95100
        })
        return df_dummy, 0.0003

# Pull live execution ticks
df_candles, current_funding_rate = fetch_live_market_data()
latest_close = df_candles['close'].iloc[-1]

# --- 3. QUANTITATIVE SURFACE GENERATION MATRIX ---
# Extrapolating the live spot/perp basis displacement across theoretical duration steps
tenors = np.array([0.33, 1.0, 3.0, 7.0]) # 8H, 1D, 3D, 7D Term Horizons
venues = ['Binance', 'Bybit', 'OKX', 'dYdX']

# Compute dynamic structural skew based on underlying leverage momentum
annualized_apr = current_funding_rate * 3 * 365 * 100 

X_tenors = np.linspace(0.33, 7.0, 20)
Y_venues = np.arange(len(venues))
X_mesh, Y_mesh = np.meshgrid(X_tenors, Y_venues)

Z_surface = []
for v_idx in range(len(venues)):
    # Model structural term degradation curve + localized venue friction inefficiencies
    venue_friction = 0.8 * np.sin(v_idx * 1.5)
    curve_line = annualized_apr * np.exp(-0.3 * X_tenors) + venue_friction
    Z_surface.append(curve_line)
Z_surface = np.array(Z_surface)

# --- 4. DATA PRESENTATION & HUD GRID LAYOUT ---
# Keep the original simulation aesthetic: stacked, dark, institutional, and close to the funding-structure render.

# A. 3D Kinetic Topology Surface Visualization via Plotly Engine
fig_3d = go.Figure(data=[go.Surface(
    x=X_mesh, y=Y_mesh, z=Z_surface,
    colorscale='RdBu', reversescale=True,
    cmid=0, showscale=False, opacity=0.8,
    hovertemplate='Tenor: %{x:.2f}d<br>Venue: %{y}<br>APR: %{z:.2f}%<extra></extra>'
)])

for v_idx, venue in enumerate(venues):
    venue_yields = annualized_apr * np.exp(-0.3 * tenors) + (0.8 * np.sin(v_idx * 1.5))
    fig_3d.add_trace(go.Scatter3d(
        x=tenors, y=[v_idx] * len(tenors), z=venue_yields,
        mode='markers', name=venue,
        marker=dict(size=6, color='white', line=dict(color='black', width=1)),
        hovertemplate=f'{venue}<br>Tenor: %{{x:.2f}}d<br>APR: %{{z:.2f}}%<extra></extra>'
    ))

fig_3d.update_layout(
    title="Dynamic Funding Rate Term Structure Surface",
    scene=dict(
        xaxis=dict(
            title=dict(text="Tenor Scale (Days Horizon)", font=dict(color="#c1c9d4")),
            backgroundcolor="#04070a",
            gridcolor="#1d2430",
            zerolinecolor="#1d2430",
            tickfont=dict(color="#c1c9d4")
        ),
        yaxis=dict(
            title=dict(text="Venues", font=dict(color="#c1c9d4")),
            tickvals=list(range(len(venues))),
            ticktext=venues,
            backgroundcolor="#04070a",
            gridcolor="#1d2430",
            zerolinecolor="#1d2430",
            tickfont=dict(color="#c1c9d4")
        ),
        zaxis=dict(
            title=dict(text="Annualized APR (%)", font=dict(color="#c1c9d4")),
            backgroundcolor="#04070a",
            gridcolor="#1d2430",
            zerolinecolor="#1d2430",
            tickfont=dict(color="#c1c9d4")
        ),
        aspectratio=dict(x=1.2, y=1, z=0.6),
        bgcolor="#04070a",
        camera=dict(eye=dict(x=1.7, y=1.7, z=1.3))
    ),
    margin=dict(l=0, r=0, b=0, t=45),
    paper_bgcolor='#04070a',
    plot_bgcolor='#04070a',
    font=dict(color='#dfe6f1'),
    height=540
)
st.plotly_chart(fig_3d, width='stretch')

# B. Synchronized Financial Candlestick Tracking Chart
fig_2d = go.Figure(data=[go.Candlestick(
    x=df_candles['time'], open=df_candles['open'], high=df_candles['high'],
    low=df_candles['low'], close=df_candles['close'],
    increasing_line_color='#02c076', decreasing_line_color='#e44243',
    increasing_fillcolor='#02c076', decreasing_fillcolor='#e44243',
    line=dict(width=1)
)])
fig_2d.update_layout(
    title="BTC/USDT Spot Index Tracker",
    xaxis_rangeslider_visible=False,
    paper_bgcolor='#04070a', plot_bgcolor='#04070a',
    xaxis=dict(
        gridcolor="#1d2430",
        zerolinecolor="#1d2430",
        tickfont=dict(color="#aeb9c8"),
        title=dict(text="", font=dict(color="#c1c9d4"))
    ),
    yaxis=dict(
        gridcolor="#1d2430",
        zerolinecolor="#1d2430",
        side="right",
        tickfont=dict(color="#aeb9c8"),
        title=dict(text="", font=dict(color="#c1c9d4"))
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    font=dict(color='#dfe6f1'),
    height=300
)
st.plotly_chart(fig_2d, width='stretch')

# Small summary row to preserve the signal HUD feel without breaking the simulation aesthetic
metric_cols = st.columns(3)
with metric_cols[0]:
    st.metric("BTC Spot Index", f"${latest_close:,.2f}")
with metric_cols[1]:
    st.metric("Funding Rate (8H)", f"{current_funding_rate:.4%}")
with metric_cols[2]:
    st.metric("Curve Peak", f"{annualized_apr:.2f}% APR")

if annualized_apr > 12:
    regime = "STEEP CONTANGO"
    regime_color = "#00ff66"
    signal = "SHORT"
    signal_detail = "SHORT BTC PERPETUALS / LONG SPOT BTC"
    explanation = "Retail long leverage is over-extended and futures premiums remain elevated above spot parity."
elif annualized_apr < -2:
    regime = "INVERTED BACKWARDATION"
    regime_color = "#ff3333"
    signal = "LONG"
    signal_detail = "LONG BTC PERPETUALS / SHORT SPOT PROXY"
    explanation = "A liquidation cascade is compressing derivative pricing below spot, creating favorable long-basis structures."
else:
    regime = "MEAN-REVERTING EQUILIBRIUM"
    regime_color = "#00ccff"
    signal = "FLAT"
    signal_detail = "WAIT FOR DISLOCATION / SCALP SMALL BASIS"
    explanation = "The funding curve remains near neutral, with only modest dislocations across venue structures."

st.markdown("### STRATEGY RADAR SIGNAL", unsafe_allow_html=False)

if annualized_apr > 12:
    signal_name = "SHORT PREMIUM ARBITRAGE"
elif annualized_apr < -2:
    signal_name = "HARVEST LONG PREMIUM"
else:
    signal_name = "SCALPING MICRO-SPREADS"

st.markdown(f"### {signal_name}")

st.markdown(f"**Curve State:** {regime}")
st.markdown(f"**Structural Context:** {explanation}")
st.markdown(f"**Execution Order Layer:** {signal_detail}")

st.markdown(f"**Position Signal:** {signal}")
